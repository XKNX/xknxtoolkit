"""Catalog plugin strings."""

from pathlib import Path

from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("catalog", _locale_dir)


class CatalogStrings:
    @property
    def PANEL_CATALOG(self) -> str:
        return _("Catalog")

    @property
    def ARCHIVE_FAILED_TO_LOAD(self) -> str:
        return _("Failed to load archive")

    @property
    def ARCHIVE_LOADED(self) -> str:
        return _("Loaded: {path}")

    @property
    def ARCHIVE_FOUND_APPS(self) -> str:
        return _("Found {count} application(s)")

    @property
    def ARCHIVE_COM_OBJECTS(self) -> str:
        return _("({count} com objects)")


S = CatalogStrings()
