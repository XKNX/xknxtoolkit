"""Regression tests for `ProxyPlugin`'s restart-after-failure lifecycle.

The bug: clicking "Start proxy" again from the ERROR state reassigned
`self._proxy` to a brand-new `TunnellingGateway` without stopping the prior
instance, orphaning the old gateway's daemon thread + asyncio loop (and, when
the failure happened after `create_server` succeeded, a listening `_server`
still bound to the original port) for the rest of the process. The fix routes
the click through `_start_proxy`, which `stop_and_wait()`s the old gateway
before constructing the replacement.

`_start_proxy` is the imgui-free seam extracted from `_render_proxy_section`'s
click handler for exactly this testability: the click handler itself can only
be driven by the Dear ImGui Test Engine harness (a real display), but the
lifecycle fix is plain attribute reassignment with no thread-affinity guard,
so exercising `_start_proxy` directly is faithful to the UI path. The e2e
harness (under `src/knx_gui/testing`) closes the menu-state -> ERROR -> click
transition end-to-end; these tests cover the fix deterministically without a
display.
"""

from __future__ import annotations

import socket
import threading
import time
import types
from typing import cast

import pytest
from knx_gui.knxip_tunnelling_gateway import GatewayState, TunnellingGateway
from knx_gui.plugins.base import API_VERSION, PluginAPI
from knx_gui.plugins.proxy.plugin import ProxyPlugin
from xknx.io import util


class _LocalIpStub:
    """Controls what the patched `get_default_local_ip` returns per call.

    `_start_proxy` constructs its replacement gateway with default
    `enable_discovery=True`, so the replacement needs `get_default_local_ip`
    to return None (skip the discovery block) to reach RUNNING
    deterministically regardless of the host's multicast capability. The
    Case B failure, conversely, needs it to return an IP so the discovery
    block actually runs and the multicast join then fails. Flip `.value`
    between the two phases of a single test."""

    def __init__(self, value: str | None) -> None:
        self.value = value

    async def __call__(self, _group: str) -> str | None:
        return self.value


_NO_LOCAL_IP = _LocalIpStub(None)


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
    end = time.monotonic() + timeout
    while time.monotonic() < end and gw.state not in states:
        time.sleep(0.01)


def _wait_port_free(port: int, timeout: float = 2.0) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("", port))
            s.listen(1)
            return
        except OSError:
            time.sleep(0.01)
        finally:
            s.close()


def _hold_tcp(port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen(1)
    return s


class _NullLog:
    """Duck-typed `LogService` stand-in - only `ProxyPlugin`/the gateway's
    `Logger` wrapper ever calls these, and only to record (or, in this test,
    discard) log lines."""

    def debug(self, _event: object, *_args: object, **_kwargs: object) -> None:
        pass

    def info(self, _event: object, *_args: object, **_kwargs: object) -> None:
        pass

    def warning(self, _event: object, *_args: object, **_kwargs: object) -> None:
        pass

    def error(self, _event: object, *_args: object, **_kwargs: object) -> None:
        pass


class _NullConnection:
    """Duck-typed `ConnectionService` stand-in carrying only the two members
    `ProxyPlugin.__init__` touches (`dispatch_proxy_cemi`, passed as the
    gateway's `on_cemi`; `add_raw_cemi_listener`, registered once and never
    fired in these tests)."""

    def dispatch_proxy_cemi(self, _raw: bytes) -> None:
        pass

    def add_raw_cemi_listener(self, _cb: object) -> None:
        pass


def _fake_plugin_api() -> PluginAPI:
    """A `PluginAPI` carrying only what `ProxyPlugin.__init__` and
    `_start_proxy` touch (`connection.dispatch_proxy_cemi`,
    `connection.add_raw_cemi_listener`, `log.*`) - no project, catalog, or
    tasks. `cast()` lets pyright keep `ProxyPlugin`'s real `PluginAPI`
    annotation strict for actual callers."""
    return cast(
        PluginAPI,
        types.SimpleNamespace(
            api_version=API_VERSION,
            project=None,
            catalog=None,
            connection=_NullConnection(),
            log=_NullLog(),
            tasks=None,
        ),
    )


def _fail_gateway_on_port(port: int) -> TunnellingGateway:
    """Start a gateway that fails at `create_server` (port held) and return it
    in its ERROR state with the loop+thread left alive - the exact artifact a
    failed "Start proxy" leaves in `self._proxy`."""
    gw = TunnellingGateway(port=port, enable_discovery=False)
    gw.start()
    _wait_state(gw, {GatewayState.ERROR, GatewayState.RUNNING})
    assert gw.state == GatewayState.ERROR
    return gw


def _stop(plugin: ProxyPlugin) -> None:
    """Cleanly tear down the plugin's current gateway so no thread outlives
    the test. `shutdown()` is fire-and-forget, which is fine on app exit but
    would leave a thread alive at test teardown."""
    proxy = plugin._proxy  # pyright: ignore[reportPrivateUsage]
    proxy.stop_and_wait()


# -- _start_proxy ------------------------------------------------------------


def test_start_proxy_tears_down_prior_failed_gateway_before_replacing_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The core regression: on the ERROR -> Start path, `_start_proxy` must
    `stop_and_wait` the failed gateway before constructing the replacement, so
    the old loop/thread come down instead of being orphaned for the session."""
    monkeypatch.setattr(util, "get_default_local_ip", _NO_LOCAL_IP)
    plugin = ProxyPlugin(_fake_plugin_api())

    port = _free_port()
    holder = _hold_tcp(port)
    try:
        failed = _fail_gateway_on_port(port)
    finally:
        holder.close()
    _wait_port_free(port)
    old_thread = failed._thread  # pyright: ignore[reportPrivateUsage]
    assert old_thread is not None and old_thread.is_alive()
    plugin._proxy = failed  # pyright: ignore[reportPrivateUsage]

    plugin._start_proxy(port)  # pyright: ignore[reportPrivateUsage]
    _wait_state(plugin._proxy, {GatewayState.RUNNING, GatewayState.ERROR})  # pyright: ignore[reportPrivateUsage]

    assert failed.state == GatewayState.STOPPED
    assert old_thread is not None and not old_thread.is_alive()
    assert plugin._proxy is not failed  # pyright: ignore[reportPrivateUsage]
    assert plugin._proxy.state == GatewayState.RUNNING  # pyright: ignore[reportPrivateUsage]

    _stop(plugin)


def test_start_proxy_on_stopped_gateway_creates_and_starts_new_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The STOPPED -> Start path (the one users normally hit) must still work:
    the initial never-started gateway is already dead, so `stop_and_wait` is a
    no-op and a new gateway is constructed and started."""
    monkeypatch.setattr(util, "get_default_local_ip", _NO_LOCAL_IP)
    plugin = ProxyPlugin(_fake_plugin_api())
    initial = plugin._proxy  # pyright: ignore[reportPrivateUsage]
    assert initial.state == GatewayState.STOPPED

    plugin._start_proxy(_free_port())  # pyright: ignore[reportPrivateUsage]
    _wait_state(plugin._proxy, {GatewayState.RUNNING, GatewayState.ERROR})  # pyright: ignore[reportPrivateUsage]

    assert plugin._proxy is not initial  # pyright: ignore[reportPrivateUsage]
    assert plugin._proxy.state == GatewayState.RUNNING  # pyright: ignore[reportPrivateUsage]

    _stop(plugin)


def test_start_proxy_repeated_retries_do_not_accumulate_gateway_threads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The headline impact of the leak: each failed-then-retried "Start proxy"
    used to add one daemon thread + asyncio loop that stayed alive for the rest
    of the session. After the fix, only the *current* gateway's own thread is
    alive no matter how many retries happen - each `_start_proxy` tears the
    prior one down before constructing the replacement.

    Models the real UI flow: every retry goes through "_start_proxy on a held
    port", so the previous gateway (running or failed) is always torn down via
    `stop_and_wait` before the next is built - never reassigned directly."""
    monkeypatch.setattr(util, "get_default_local_ip", _NO_LOCAL_IP)
    plugin = ProxyPlugin(_fake_plugin_api())

    for _ in range(3):
        port = _free_port()
        holder = _hold_tcp(port)
        try:
            # "Start proxy" on the held port -> the new gateway fails (Case A);
            # _start_proxy first tears down whatever self._proxy currently is.
            plugin._start_proxy(port)  # pyright: ignore[reportPrivateUsage]
            proxy = plugin._proxy  # pyright: ignore[reportPrivateUsage]
            _wait_state(proxy, {GatewayState.RUNNING, GatewayState.ERROR})
            # the attempt must have failed *while the port was held*
            assert proxy.state == GatewayState.ERROR
        finally:
            holder.close()

    # all prior failed gateways were torn down by the next _start_proxy; the
    # only live gateway thread is the current (last failed) one
    live_gateway_threads = [
        t for t in threading.enumerate() if t.name == "KNX-Gateway" and t.is_alive()
    ]
    assert len(live_gateway_threads) == 1, (
        f"expected exactly one live KNX-Gateway thread (the current gateway's), "
        f"got {live_gateway_threads}"
    )

    # a final successful retry (free port) confirms recovery and that the
    # accumulated-leak fix still holds once the conflict clears
    plugin._start_proxy(_free_port())  # pyright: ignore[reportPrivateUsage]
    proxy = plugin._proxy  # pyright: ignore[reportPrivateUsage]
    _wait_state(proxy, {GatewayState.RUNNING, GatewayState.ERROR})
    assert proxy.state == GatewayState.RUNNING
    live_gateway_threads = [
        t for t in threading.enumerate() if t.name == "KNX-Gateway" and t.is_alive()
    ]
    assert len(live_gateway_threads) == 1, (
        f"expected exactly one live KNX-Gateway thread after recovery, "
        f"got {live_gateway_threads}"
    )

    _stop(plugin)
    assert all(not t.is_alive() for t in live_gateway_threads)


def test_start_proxy_same_port_retry_recovers_after_case_b_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Case B recovery via the plugin path: a failure that left a live `_server`
    bound to the port used to make a same-port retry stay in ERROR for the rest
    of the session. With `stop_and_wait` tearing the orphan's `_server` down
    first, the retry rebinds the original port and reaches RUNNING."""
    # First phase: an IP so the failed gateway's discovery block runs (and the
    # multicast join on a non-multicast group then fails -> Case B).
    discovery = _LocalIpStub("127.0.0.1")
    monkeypatch.setattr(util, "get_default_local_ip", discovery)
    plugin = ProxyPlugin(_fake_plugin_api())

    port = _free_port()
    failed = TunnellingGateway(port=port, multicast_group="1.2.3.4")
    failed.start()
    _wait_state(failed, {GatewayState.ERROR, GatewayState.RUNNING})
    assert failed.state == GatewayState.ERROR
    assert failed._server is not None  # pyright: ignore[reportPrivateUsage]
    plugin._proxy = failed  # pyright: ignore[reportPrivateUsage]

    # Second phase: skip discovery so the replacement reaches RUNNING on the
    # now-freed port deterministically.
    discovery.value = None
    plugin._start_proxy(port)  # pyright: ignore[reportPrivateUsage]
    _wait_state(plugin._proxy, {GatewayState.RUNNING, GatewayState.ERROR})  # pyright: ignore[reportPrivateUsage]

    assert plugin._proxy.state == GatewayState.RUNNING  # pyright: ignore[reportPrivateUsage]
    assert failed.state == GatewayState.STOPPED
    assert failed._server is None  # pyright: ignore[reportPrivateUsage]

    _stop(plugin)
