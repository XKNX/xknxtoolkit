"""Proxy plugin strings."""

from pathlib import Path

from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("proxy", _locale_dir)


class ProxyStrings:
    @property
    def MENU_PROXY(self) -> str:
        return _("Proxy")


S = ProxyStrings()
