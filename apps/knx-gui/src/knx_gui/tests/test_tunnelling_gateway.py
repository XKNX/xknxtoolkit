"""Unit tests for `TunnellingGateway`'s restart-after-failure lifecycle.

`start()` always spawns its own daemon thread running a private asyncio
loop. A failed `_start_async` records the error and returns, but leaves
that loop/thread running (and, when `create_server` succeeded before the
failure, a listening `_server` bound to the port). The `stop_and_wait()`
helper added to close that gap is what `ProxyPlugin._start_proxy` now calls
before replacing the gateway - these tests cover the helper directly, so the
fix doesn't depend on the imgui render loop (which the e2e harness exercises
under `src/knx_gui/testing`).

No monkeypatching of `xknx` is needed for the failed-start cases: holding a
TCP port with a plain socket reproduces the everyday conflict (an external
process on TCP 3671) because asyncio's `create_server` does not set
`SO_REUSEPORT`. The discovery-phase failure (the rarer Case B, where
`create_server` succeeds before the failure) is triggered by pointing the
multicast join at a non-multicast address, which `IP_ADD_MEMBERSHIP` rejects
deterministically on Linux.
"""

from __future__ import annotations

import contextlib
import socket
import threading
import time
from collections.abc import Generator

import pytest
from xknx.io import util

from knx_gui.knxip_tunnelling_gateway import GatewayState, TunnellingGateway

# -- async fake for `xknx.IO.util.get_default_local_ip` ------------------------
# The gateway `await`s this, so the replacement has to be a coroutine function.
# Returning an IP makes the discovery block run; the Case B test then points
# the multicast join at a non-multicast group, which `IP_ADD_MEMBERSHIP`
# rejects deterministically on Linux.


async def _loopback_local_ip(_group: str) -> str | None:
    return "127.0.0.1"


# -- small helpers ------------------------------------------------------------


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def _wait_state(
    gw: TunnellingGateway, states: set[GatewayState], timeout: float = 2.0
) -> None:
    """Poll until the gateway reaches one of `states`; never raises on timeout
    (the caller asserts the resulting state explicitly)."""
    end = time.monotonic() + timeout
    while time.monotonic() < end and gw.state not in states:
        time.sleep(0.01)


def _can_bind_tcp(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("", port))
        s.listen(1)
        return True
    except OSError:
        return False
    finally:
        s.close()


def _wait_port_free(port: int, timeout: float = 2.0) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end and not _can_bind_tcp(port):
        time.sleep(0.01)


@contextlib.contextmanager
def _hold_tcp(port: int) -> Generator[None, None, None]:
    """Hold a listening TCP socket on `port` so asyncio `create_server` fails
    with EADDRINUSE - the everyday conflict (another KNX app on TCP 3671)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen(1)
    try:
        yield
    finally:
        s.close()


# -- stop_and_wait ------------------------------------------------------------


def test_stop_and_wait_on_never_started_gateway_is_a_noop() -> None:
    """A gateway that was constructed but never `start()`ed has no thread/loop;
    `stop_and_wait` must return True immediately and leave state STOPPED.

    Covers the `ProxyPlugin.__init__` initial gateway (never started) and the
    STOPPED-state "Start proxy" path, which must not regress."""
    gw = TunnellingGateway(enable_discovery=False)
    assert gw.state == GatewayState.STOPPED

    result = gw.stop_and_wait()

    assert result is True
    assert gw.state == GatewayState.STOPPED
    assert gw._thread is None  # pyright: ignore[reportPrivateUsage]


def test_stop_and_wait_tears_down_running_gateway_and_joins_thread() -> None:
    """On a cleanly running gateway, `stop_and_wait` closes the server,
    stops the loop, and joins the daemon thread within the timeout."""
    gw = TunnellingGateway(port=_free_port(), enable_discovery=False)
    gw.start()
    _wait_state(gw, {GatewayState.RUNNING, GatewayState.ERROR})
    assert gw.state == GatewayState.RUNNING
    assert gw._thread is not None and gw._thread.is_alive()  # pyright: ignore[reportPrivateUsage]

    result = gw.stop_and_wait()

    assert result is True
    assert gw.state == GatewayState.STOPPED
    assert gw._thread is not None and not gw._thread.is_alive()  # pyright: ignore[reportPrivateUsage]
    assert gw._loop is None  # pyright: ignore[reportPrivateUsage]


def test_stop_and_wait_releases_listening_port_for_rebind() -> None:
    """After `stop_and_wait`, the listening `_server` is closed and the port can
    be rebound by a fresh gateway - the mechanism that lets a same-port retry
    succeed once the fix tears the old gateway down."""
    port = _free_port()
    first = TunnellingGateway(port=port, enable_discovery=False)
    first.start()
    _wait_state(first, {GatewayState.RUNNING, GatewayState.ERROR})
    assert first.state == GatewayState.RUNNING

    first.stop_and_wait()

    second = TunnellingGateway(port=port, enable_discovery=False)
    second.start()
    _wait_state(second, {GatewayState.RUNNING, GatewayState.ERROR})
    assert second.state == GatewayState.RUNNING
    second.stop_and_wait()


def test_stop_and_wait_tears_down_gateway_that_failed_to_start_case_a() -> None:
    """Case A (the everyday conflict): `create_server` fails before `_server`
    is assigned, so the orphan is only an idle loop + thread. `stop_and_wait`
    must still tear that loop/thread down rather than leaving them running for
    the rest of the process."""
    port = _free_port()
    with _hold_tcp(port):
        gw = TunnellingGateway(port=port, enable_discovery=False)
        gw.start()
        _wait_state(gw, {GatewayState.ERROR, GatewayState.RUNNING})
        assert gw.state == GatewayState.ERROR
        assert gw._server is None  # pyright: ignore[reportPrivateUsage]
        # the failure left the loop + daemon thread alive
        assert gw._loop is not None and gw._loop.is_running()  # pyright: ignore[reportPrivateUsage]
        thread = gw._thread  # pyright: ignore[reportPrivateUsage]
        assert thread is not None and thread.is_alive()

    # port is free again (the holder released it; the failure never bound it)
    _wait_port_free(port)

    result = gw.stop_and_wait()

    assert result is True
    assert gw.state == GatewayState.STOPPED
    assert thread is not None and not thread.is_alive()
    assert gw._loop is None  # pyright: ignore[reportPrivateUsage]


def test_stop_and_wait_after_case_b_failure_releases_original_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case B: `create_server` succeeds (so `_server` is a live listener bound to
    the port) and the failure lands in the discovery block. Without the fix the
    orphaned `_server` keeps holding the original port for the rest of the
    session; `stop_and_wait` must close it so a same-port retry reaches RUNNING.

    Triggered without monkeypatching any `xknx` code: the multicast join is
    aimed at a non-multicast address, which `IP_ADD_MEMBERSHIP` rejects. The
    only patch is `get_default_local_ip` returning a non-None IP so the
    discovery block actually runs (otherwise it skips to RUNNING)."""
    monkeypatch.setattr(util, "get_default_local_ip", _loopback_local_ip)

    port = _free_port()
    gw = TunnellingGateway(port=port, multicast_group="1.2.3.4")
    gw.start()
    _wait_state(gw, {GatewayState.ERROR, GatewayState.RUNNING})
    assert gw.state == GatewayState.ERROR
    # the failure happened *after* create_server succeeded
    assert gw._server is not None  # pyright: ignore[reportPrivateUsage]
    # so the orphaned listener still holds the original port
    assert not _can_bind_tcp(port)

    result = gw.stop_and_wait()

    assert result is True
    assert gw.state == GatewayState.STOPPED
    assert gw._server is None  # pyright: ignore[reportPrivateUsage]
    # the port is released - a same-port retry can now rebind and reach RUNNING
    assert _can_bind_tcp(port)
    retry = TunnellingGateway(port=port, enable_discovery=False)
    retry.start()
    _wait_state(retry, {GatewayState.RUNNING, GatewayState.ERROR})
    assert retry.state == GatewayState.RUNNING
    retry.stop_and_wait()


def test_stop_and_wait_returns_false_when_thread_does_not_exit_in_time() -> None:
    """Timeout contract: if the gateway's thread doesn't exit within `timeout`,
    `stop_and_wait` logs and returns False without raising - so a caller that
    proceeds to replace the gateway is no worse off than today's
    fire-and-forget `stop()`.

    Models a wedged loop with a live thread that `stop()` can't reach because
    there is no event loop to schedule `_stop_async` on (so `stop()` only flips
    the state, and the join times out against the still-running thread)."""
    gw = TunnellingGateway(enable_discovery=False)
    blocker = threading.Event()
    wedge = threading.Thread(target=lambda: blocker.wait(5.0), daemon=True)
    wedge.start()
    try:
        gw._state = GatewayState.ERROR  # pyright: ignore[reportPrivateUsage]
        gw._thread = wedge  # pyright: ignore[reportPrivateUsage]
        gw._loop = None  # pyright: ignore[reportPrivateUsage]  # stop() can't reach a loop

        result = gw.stop_and_wait(timeout=0.1)

        assert result is False
        assert wedge.is_alive()  # timed out, not killed
        # stop() still flipped the recorded state, even though the thread is stuck
        assert gw.state == GatewayState.STOPPED
    finally:
        blocker.set()
        wedge.join(1.0)
