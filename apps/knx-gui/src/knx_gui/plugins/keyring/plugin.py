"""Keyring / KNX Secure plugin: import and browse a ``.knxkeys`` keyring."""

from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.keyring.service import KeyringService
from knx_gui.plugins.keyring.strings import S
from knx_gui.plugins.keyring.ui import KeyringPanel


class KeyringPlugin:
    name = "keyring"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._service = KeyringService()
        self._service.set_logger(Logger(api.log, "keyring"))
        self._panel = KeyringPanel(
            service=self._service,
            get_group_addresses=lambda: api.project.group_addresses,
        )

    @property
    def panels(self) -> list[PanelDefinition]:
        return [
            PanelDefinition(
                name="keyring",
                label=S.PANEL_KEYRING,
                dock="LeftSpace",
                render=self._panel.render,
            )
        ]

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
