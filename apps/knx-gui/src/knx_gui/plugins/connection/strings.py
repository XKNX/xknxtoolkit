"""Connection plugin strings."""

from pathlib import Path

from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("connection", _locale_dir)


class ConnectionStrings:
    @property
    def MENU_CONNECTION(self) -> str:
        return _("Connection")

    @property
    def MENU_PROXY(self) -> str:
        return _("Proxy")

    @property
    def MENU_CONNECT(self) -> str:
        return _("Connect")

    @property
    def MENU_DISCONNECT(self) -> str:
        return _("Disconnect")

    @property
    def STATUS_CONNECTED(self) -> str:
        return _("Connected: {ip}")

    @property
    def STATUS_CONNECTED_TO(self) -> str:
        return _("Connected to {ip}")

    @property
    def STATUS_DISCONNECTED(self) -> str:
        return _("Disconnected")


S = ConnectionStrings()
