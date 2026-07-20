from __future__ import annotations

from typing import Any

from knx_gui.plugins.virtual.virtual_gateway import VirtualGateway, VirtualGatewayState


class VirtualService:
    """Owns the virtual gateway (and, in future, virtual devices) lifecycle."""

    def __init__(self) -> None:
        self._logger: Any = None
        self._gateway = VirtualGateway()

    def set_logger(self, logger: Any) -> None:
        self._logger = logger

    @property
    def gateway_state(self) -> VirtualGatewayState:
        return self._gateway.state

    @property
    def gateway_error(self) -> str | None:
        return self._gateway.error

    def start_gateway(self, name: str, port: int, multicast_group: str) -> None:
        self._gateway = VirtualGateway(
            name=name,
            port=port,
            multicast_group=multicast_group,
            logger=self._logger,
        )
        self._gateway.start()

    def stop_gateway(self) -> None:
        self._gateway.stop()

    def shutdown(self) -> None:
        self._gateway.stop()
