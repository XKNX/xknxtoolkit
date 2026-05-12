from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.telegrams.ui import TelegramsPanel
from knx_gui.strings import S
from knx_gui.types import Telegram


MOCK_TELEGRAMS = [
    Telegram("2026-05-12 09:15:23", "1.1.10", "0/0/1", "GroupValueWrite", "1.001", "On"),
    Telegram("2026-05-12 09:15:24", "1.1.15", "0/0/2", "GroupValueRead", "", ""),
    Telegram("2026-05-12 09:15:24", "1.1.20", "0/0/2", "GroupValueResponse", "5.001", "75%"),
    Telegram("2026-05-12 09:15:26", "1.1.10", "0/1/5", "GroupValueWrite", "9.001", "21.5 °C"),
    Telegram("2026-05-12 09:15:28", "1.1.12", "0/0/1", "GroupValueWrite", "1.001", "Off"),
    Telegram("2026-05-12 09:15:30", "1.1.15", "0/2/10", "GroupValueRead", "", ""),
    Telegram("2026-05-12 09:15:30", "1.1.25", "0/2/10", "GroupValueResponse", "1.001", "On"),
    Telegram("2026-05-12 09:15:32", "1.1.10", "0/1/6", "GroupValueWrite", "5.001", "50%"),
    Telegram("2026-05-12 09:15:35", "1.1.30", "0/3/1", "GroupValueWrite", "16.001", "Hello World"),
    Telegram("2026-05-12 09:15:38", "1.1.12", "0/0/3", "GroupValueWrite", "1.001", "On"),
    Telegram("2026-05-12 09:15:40", "1.1.15", "0/1/5", "GroupValueRead", "", ""),
    Telegram("2026-05-12 09:15:40", "1.1.20", "0/1/5", "GroupValueResponse", "9.001", "22.0 °C"),
    Telegram("2026-05-12 09:15:42", "1.1.10", "0/0/1", "GroupValueWrite", "1.001", "On"),
    Telegram("2026-05-12 09:15:45", "1.1.25", "0/2/15", "GroupValueWrite", "10.001", "12:30:00"),
    Telegram("2026-05-12 09:15:48", "1.1.30", "0/3/2", "GroupValueWrite", "11.001", "2026-05-12"),
]


class TelegramsPlugin:
    name = "telegrams"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._telegrams: list[Telegram] = list(MOCK_TELEGRAMS)
        self._panel = TelegramsPanel(
            get_telegrams=lambda: self._telegrams,
            on_focus_source=self._on_focus_source,
            on_clear=self.clear_telegrams,
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
