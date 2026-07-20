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
    def SECTION_DISCOVERED(self) -> str:
        return _("Discovered gateways")

    @property
    def NO_GATEWAYS_FOUND(self) -> str:
        return _("No gateways found")

    @property
    def SECTION_MANUAL(self) -> str:
        return _("Manual connection")

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
