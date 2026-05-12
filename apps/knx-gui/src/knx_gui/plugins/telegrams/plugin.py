from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.telegrams.ui import TelegramsPanel
from knx_gui.strings import S
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
        self._panels = [
            PanelDefinition(
                name="telegrams",
                label=S.PANEL_TELEGRAMS,
                dock="BottomSpace",
                render=self._panel.render,
            ),
        ]

    @property
    def telegrams(self) -> list[Telegram]:
        return self._telegrams

    def add_telegram(self, telegram: Telegram) -> None:
        self._telegrams.append(telegram)

    def clear_telegrams(self) -> None:
        self._telegrams.clear()

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
