from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.telegrams.ui import TelegramsPanel


class TelegramsPlugin:
    name = "telegrams"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._panel = TelegramsPanel(
            get_telegrams=lambda: api.state.telegrams,
            on_focus_source=self._on_focus_source,
        )

    def _on_focus_source(self, address: str) -> None:
        device = self._api.state.find_device_by_address(address)
        if device:
            self._api.state.selected_device = device

    @property
    def panel(self) -> TelegramsPanel:
        return self._panel

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
