"""
Centralized UI strings for internationalization.

Each plugin has its own translation domain. Use `create_translator()` to get
a translator function for a specific plugin.
"""

import gettext
from pathlib import Path

_current_locale: str = "en"


def set_locale(locale: str) -> None:
    global _current_locale
    _current_locale = locale


def get_locale() -> str:
    return _current_locale


def create_translator(domain: str, locale_dir: Path):
    def translate(text: str) -> str:
        try:
            trans = gettext.translation(domain, locale_dir, languages=[_current_locale])
            return trans.gettext(text)
        except FileNotFoundError:
            return text

    return translate


_base_locale_dir = Path(__file__).parent.parent / "locales"
_ = create_translator("knx_gui", _base_locale_dir)


class BaseStrings:
    @property
    def APP_TITLE(self) -> str:
        return _("XKNX Toolkit")

    @property
    def BTN_ADD(self) -> str:
        return _("Add")

    @property
    def BTN_CLOSE(self) -> str:
        return _("Close")

    @property
    def BTN_CANCEL(self) -> str:
        return _("Cancel")

    @property
    def BTN_COPY(self) -> str:
        return _("Copy")

    @property
    def BTN_CLEAR(self) -> str:
        return _("Clear")

    @property
    def BTN_STOP(self) -> str:
        return _("Stop")

    @property
    def FILE_DIALOG_ALL_FILES(self) -> str:
        return _("All files")

    @property
    def SHORTCUT_UNDO(self) -> str:
        return "Ctrl+Z"

    @property
    def SHORTCUT_REDO(self) -> str:
        return "Ctrl+Y"


class MenuStrings:
    @property
    def MENU_FILE(self) -> str:
        return _("File")

    @property
    def MENU_NEW_PROJECT(self) -> str:
        return _("New Project")

    @property
    def MENU_OPEN_PROJECT(self) -> str:
        return _("Open Project")

    @property
    def MENU_LOAD_KNXPROD(self) -> str:
        return _("Load .knxprod...")

    @property
    def MENU_EXIT(self) -> str:
        return _("Exit")

    @property
    def MENU_EDIT(self) -> str:
        return _("Edit")

    @property
    def MENU_UNDO(self) -> str:
        return _("Undo")

    @property
    def MENU_REDO(self) -> str:
        return _("Redo")

    @property
    def FILE_DIALOG_KNXPROD_TITLE(self) -> str:
        return _("Open KNX product archive")

    @property
    def FILE_DIALOG_KNXPROD_FILTER(self) -> str:
        return _("KNX product (*.knxprod)")

    @property
    def FILE_DIALOG_PROJECT_TITLE(self) -> str:
        return _("Open XKNX project")

    @property
    def FILE_DIALOG_PROJECT_SAVE_TITLE(self) -> str:
        return _("Save XKNX project")

    @property
    def FILE_DIALOG_PROJECT_FILTER(self) -> str:
        return _("XKNX project (*.xknx)")


class _CombinedStrings(BaseStrings, MenuStrings):
    pass


S = _CombinedStrings()
