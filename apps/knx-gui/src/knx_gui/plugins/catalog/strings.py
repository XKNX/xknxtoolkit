"""Catalog plugin strings."""

from pathlib import Path

from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("catalog", _locale_dir)


class CatalogStrings:
    @property
    def PANEL_CATALOG(self) -> str:
        return _("Catalog")


S = CatalogStrings()
