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
        self._panel = VirtualPanel(
            get_gateway_state=lambda: self._service.gateway_state,
            get_gateway_error=lambda: self._service.gateway_error,
            on_start=self._service.start_gateway,
            on_stop=self._service.stop_gateway,
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
