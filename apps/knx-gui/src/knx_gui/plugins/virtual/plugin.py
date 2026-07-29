from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.virtual.service import VirtualService
from knx_gui.plugins.virtual.strings import S
from knx_gui.plugins.virtual.ui import VirtualPanel


class VirtualPlugin:
    name = "virtual"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._service = VirtualService()
        self._service.set_logger(Logger(api.log, "virtual"))
        self._service.set_cemi_listener(api.connection.dispatch_virtual_cemi)
        self._panel = VirtualPanel(
            get_router_state=lambda: self._service.router_state,
            get_router_error=lambda: self._service.router_error,
            get_gateway_connected=lambda: self._service.gateway_connected,
            on_start=self._service.start_router,
            on_stop=self._service.stop_router,
            get_device=lambda: self._service.device,
        )
        self._panels = [
            PanelDefinition(
                name="virtual",
                label=S.PANEL_VIRTUAL,
                dock="RightSpace",
                render=self._panel.render,
            ),
        ]

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        self._service.shutdown()
