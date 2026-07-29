from __future__ import annotations

from collections.abc import Callable
from typing import Any

from knx_gui.plugins.virtual.virtual_device import VirtualDevice
from knx_gui.plugins.virtual.virtual_router import VirtualRouter, VirtualRouterState


class VirtualService:
    """Owns the virtual router and virtual device lifecycle."""

    def __init__(self) -> None:
        self._logger: Any = None
        self._cemi_listener: Callable[[bytes], None] | None = None
        self._router = VirtualRouter()
        self.device = VirtualDevice()

    def set_logger(self, logger: Any) -> None:
        self._logger = logger
        self.device.set_logger(logger)

    def set_cemi_listener(self, listener: Callable[[bytes], None] | None) -> None:
        self._cemi_listener = listener

    @property
    def router_state(self) -> VirtualRouterState:
        return self._router.state

    @property
    def router_error(self) -> str | None:
        return self._router.error

    def start_router(self, name: str, port: int, multicast_group: str) -> None:
        self._router = VirtualRouter(
            name=name,
            port=port,
            multicast_group=multicast_group,
            on_cemi=self._handle_cemi,
            logger=self._logger,
        )
        self._router.start()

    def stop_router(self) -> None:
        self._router.stop()

    def _handle_cemi(self, raw: bytes) -> None:
        if self._cemi_listener is not None:
            self._cemi_listener(raw)
        for reply in self.device.handle_cemi(raw):
            self._router.send_cemi(reply)

    def shutdown(self) -> None:
        self._router.stop()
