"""Regression coverage for VirtualRouter.send_cemi observability.

``send_cemi`` previously discarded the ``concurrent.futures.Future`` returned
by ``asyncio.run_coroutine_threadsafe(...)``, silently swallowing every
exception from ``Routing.send_cemi`` (OSError on a closed multicast socket, a
frame-encode error, ...). The fix mirrors ``connection/service.py``'s
``_log_send_cemi_result`` precedent: a done-callback logs the send outcome and
the not-running early-return is logged instead of being silent.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable, Iterator
from concurrent.futures import Future
from typing import Any, cast

import pytest
from knx_gui.plugins.virtual.virtual_router import VirtualRouter, VirtualRouterState
from xknx.cemi.cemi_frame import CEMIFrame
from xknx.cemi.const import CEMIMessageCode
from xknx.io.routing import Routing


class _FakeLogger:
    """Minimal stand-in for knx_gui.plugins.base.Logger recording all calls.

    The real Logger forwards (event, plugin, **kwargs) to LogService; tests
    only need to assert on the (level, event, kwargs) the plugin emits.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def debug(self, event: str, **kwargs: Any) -> None:
        self.calls.append(("debug", event, kwargs))

    def info(self, event: str, **kwargs: Any) -> None:
        self.calls.append(("info", event, kwargs))

    def warning(self, event: str, **kwargs: Any) -> None:
        self.calls.append(("warning", event, kwargs))

    def error(self, event: str, **kwargs: Any) -> None:
        self.calls.append(("error", event, kwargs))


class _FakeRouting:
    """Stand-in for xknx.io.routing.Routing with a controllable send_cemi.

    Mirrors the real ``async def send_cemi(self, cemi: CEMIFrame) -> None``
    signature so it can be driven through run_coroutine_threadsafe on a real
    event loop; records the frames it was asked to send and optionally raises.
    """

    def __init__(self, *, exc: BaseException | None = None) -> None:
        self._exc = exc
        self.received: list[CEMIFrame] = []

    async def send_cemi(self, cemi: CEMIFrame) -> None:
        self.received.append(cemi)
        if self._exc is not None:
            raise self._exc


def _make_cemi() -> CEMIFrame:
    return CEMIFrame(code=CEMIMessageCode.L_DATA_REQ, data=None)


def _wait_until(predicate: Callable[[], bool], timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


@pytest.fixture
def running_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    ready = threading.Event()

    def _run() -> None:
        ready.set()
        loop.run_forever()

    thread = threading.Thread(target=_run, daemon=True, name="test-vrouter-loop")
    thread.start()
    ready.wait()
    try:
        yield loop
    finally:
        loop.call_soon_threadsafe(loop.stop)
        thread.join(timeout=3)
        loop.close()


def test_send_cemi_failure_is_observable_not_swallowed(
    running_loop: asyncio.AbstractEventLoop,
) -> None:
    """Regression for the discarded-Future swallow: before the fix an OSError
    from Routing.send_cemi was invisible - no log, no ERROR state, no return to
    the caller. With the done-callback in place the failure is now logged."""
    logger = _FakeLogger()
    router = VirtualRouter(logger=logger)
    router._loop = running_loop  # pyright: ignore[reportPrivateUsage]
    router._routing = cast(Routing, _FakeRouting(exc=OSError("closed")))  # pyright: ignore[reportPrivateUsage]

    router.send_cemi(_make_cemi())

    # The decisive regression assertion: the bug was that call_count stayed 0.
    assert _wait_until(lambda: any(call[0] == "error" for call in logger.calls))
    assert any(call[1] == "send_cemi failed" for call in logger.calls)
    # The fix mirrors connection/service.py: it only logs, it does not
    # transition the router to ERROR. Pin that boundary so a future change
    # is deliberate rather than accidental.
    assert router.state == VirtualRouterState.STOPPED
    assert router.error is None


def test_send_cemi_logs_success_when_routing_succeeds(
    running_loop: asyncio.AbstractEventLoop,
) -> None:
    """Success path is unchanged: the frame still reaches Routing.send_cemi and
    the done-callback fires (confirming it is actually attached by send_cemi)."""
    logger = _FakeLogger()
    router = VirtualRouter(logger=logger)
    router._loop = running_loop  # pyright: ignore[reportPrivateUsage]
    routing = _FakeRouting()
    router._routing = cast(Routing, routing)  # pyright: ignore[reportPrivateUsage]

    router.send_cemi(_make_cemi())

    assert _wait_until(
        lambda: any(
            call[0] == "debug" and call[1] == "send_cemi ok" for call in logger.calls
        )
    )
    assert ("debug", "send_cemi ok", {}) in logger.calls
    assert len(routing.received) == 1


def test_on_send_done_is_silent_when_cancelled() -> None:
    """A cancelled Future must short-circuit before .exception(); calling
    .exception() on a cancelled concurrent.futures.Future raises CancelledError,
    so the cancelled-guard is a real footgun, not a stylistic choice."""
    logger = _FakeLogger()
    router = VirtualRouter(logger=logger)
    fut: Future[None] = Future()
    fut.cancel()

    router._on_send_done(fut)  # pyright: ignore[reportPrivateUsage]

    assert not any(call[0] in ("error", "debug") for call in logger.calls)


def test_send_cemi_logs_warning_when_router_not_started() -> None:
    """The not-running early-return was silent before the fix; it now logs a
    warning so a send dropped during the stop-race / unstarted window is
    diagnosable instead of invisible."""
    logger = _FakeLogger()
    router = VirtualRouter(logger=logger)  # _loop and _routing are both None

    router.send_cemi(_make_cemi())

    assert (
        "warning",
        "send_cemi called while router not running",
        {},
    ) in logger.calls
