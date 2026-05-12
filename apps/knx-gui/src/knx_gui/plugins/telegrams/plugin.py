from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.telegrams.ui import TelegramsPanel
from knx_gui.types import Telegram


class TelegramsPlugin:
    name = "telegrams"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._telegrams: list[Telegram] = []
        self._panel = TelegramsPanel(
            get_telegrams=lambda: self._telegrams,
            on_focus_source=self._on_focus_source,
        )

    @property
    def telegrams(self) -> list[Telegram]:
        return self._telegrams

    def add_telegram(self, telegram: Telegram) -> None:
        self._telegrams.append(telegram)

    def clear_telegrams(self) -> None:
        self._telegrams.clear()

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
