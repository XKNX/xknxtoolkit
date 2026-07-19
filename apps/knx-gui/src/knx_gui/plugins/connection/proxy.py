from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from enum import Enum
from typing import Any

from xknx import XKNX
from xknx.io import util
from xknx.io.routing import Routing


class ProxyState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class RoutingProxy:
    """Listens on KNX/IP multicast, dispatches captured CEMI frames, and optionally forwards them."""

    DEFAULT_MCAST_GROUP = "224.0.23.12"
    DEFAULT_MCAST_PORT = 3671

    def __init__(
        self,
        on_cemi: Callable[[bytes], None],
        forward_cemi: Callable[[bytes], None] | None = None,
        multicast_group: str = DEFAULT_MCAST_GROUP,
        multicast_port: int = DEFAULT_MCAST_PORT,
        logger: Any = None,
    ) -> None:
        self._on_cemi = on_cemi
        self._forward_cemi = forward_cemi
        self._multicast_group = multicast_group
        self._multicast_port = multicast_port
        self._logger = logger

        self._state = ProxyState.STOPPED
        self._error: str | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._routing: Routing | None = None
        self._xknx: XKNX | None = None
        self._cemi_count = 0

    @property
    def state(self) -> ProxyState:
        return self._state

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def running(self) -> bool:
        return self._state == ProxyState.RUNNING

    def start(self) -> None:
        if self._state in (ProxyState.STARTING, ProxyState.RUNNING):
            return
        self._state = ProxyState.STARTING
        self._error = None

        loop_ready = threading.Event()

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            loop_ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run, daemon=True, name="KNX-Proxy")
        self._thread.start()
        loop_ready.wait()
        assert self._loop is not None
        asyncio.run_coroutine_threadsafe(self._start_async(), self._loop)

    async def _start_async(self) -> None:
        try:
            local_ip = await util.get_default_local_ip(self._multicast_group)
            if local_ip is None:
                raise RuntimeError("Could not determine local IP for multicast interface")
            self._xknx = XKNX()
            self._routing = Routing(
                self._xknx,
                individual_address=None,
                cemi_received_callback=self._on_cemi_received,
                local_ip=local_ip,
                multicast_group=self._multicast_group,
                multicast_port=self._multicast_port,
            )
            await self._routing.connect()
            self._state = ProxyState.RUNNING
            if self._logger:
                self._logger.info(
                    "proxy running",
                    local_ip=local_ip,
                    multicast=f"{self._multicast_group}:{self._multicast_port}",
                )
        except Exception as e:
            self._state = ProxyState.ERROR
            self._error = str(e)
            if self._logger:
                self._logger.error("proxy failed to start", error=str(e))

    def _on_cemi_received(self, raw: bytes) -> None:
        self._cemi_count += 1
        if self._logger and self._cemi_count <= 5:
            self._logger.info("cemi received", n=self._cemi_count, hex=raw.hex(" "))
        self._on_cemi(raw)
        if self._forward_cemi is not None:
            self._forward_cemi(raw)

    def stop(self) -> None:
        if self._state == ProxyState.STOPPED:
            return
        if self._loop is not None and self._routing is not None:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self._loop)
        else:
            self._state = ProxyState.STOPPED

    async def _stop_async(self) -> None:
        try:
            if self._routing is not None:
                await self._routing.disconnect()
        finally:
            self._routing = None
            self._xknx = None
            self._state = ProxyState.STOPPED
            if self._logger:
                self._logger.info("proxy stopped", total_cemi=self._cemi_count)
            self._cemi_count = 0
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None

    def set_forward(self, forward_cemi: Callable[[bytes], None] | None) -> None:
        self._forward_cemi = forward_cemi
