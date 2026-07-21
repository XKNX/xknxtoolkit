from __future__ import annotations

from typing import Any

from knx_gui.plugins.virtual.virtual_router import VirtualRouter, VirtualRouterState


class VirtualService:
    """Owns the virtual router (and, in future, virtual devices) lifecycle."""

    def __init__(self) -> None:
        self._logger: Any = None
        self._router = VirtualRouter()

    def set_logger(self, logger: Any) -> None:
        self._logger = logger

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
            logger=self._logger,
        )
        self._router.start()

    def stop_router(self) -> None:
        self._router.stop()

    def shutdown(self) -> None:
        self._router.stop()
