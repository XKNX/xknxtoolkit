from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.network.service import NetworkService
from knx_gui.plugins.network.strings import S
from knx_gui.plugins.network.ui import CaptureState as UICaptureState
from knx_gui.plugins.network.ui import NetworkPanel


class NetworkPlugin:
    name = "network"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._service = NetworkService()
        self._panel = NetworkPanel(
            get_telegrams=lambda: self._service.telegrams,
            get_capture_state=lambda: UICaptureState(self._service.state.value),
            on_start=self._service.start,
            on_stop=self._service.stop,
            on_clear=self._service.clear,
            on_focus_source=self._on_focus_source,
        )
        self._panels = [
            PanelDefinition(
                name="network",
                label=S.PANEL_NETWORK,
                dock="BottomSpace",
                render=self._panel.render,
            ),
        ]

    @property
    def service(self) -> NetworkService:
        return self._service

    def _on_focus_source(self, address: str) -> None:
        device = self._api.project.find_device_by_address(address)
        if device:
            self._api.project.selected_device = device

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
