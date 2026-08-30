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
    def STATUS_PROJECT(self) -> str:
        return _("Project: {name}  ·  {devices} devices  ·  {gas} GAs")

    @property
    def STATUS_NO_PROJECT(self) -> str:
        return _("No project open")

    @property
    def STATUS_PROGRAMMING(self) -> str:
        return _("Programming {address}...")

    @property
    def STATUS_TESTING(self) -> str:
        return _("Testing {address}...")

    @property
    def STATUS_PROGRAM_DONE(self) -> str:
        return _("Programming complete")

    @property
    def STATUS_PROGRAM_FAILED(self) -> str:
        return _("Programming failed")

    @property
    def STATUS_NO_CONNECTION(self) -> str:
        return _("No KNX connection")

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
    def MENU_EXPORT_KNXPROJ(self) -> str:
        return _("Export .knxproj...")

    @property
    def FILE_DIALOG_KNXPROJ_SAVE_TITLE(self) -> str:
        return _("Export ETS project")

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
    def FILE_DIALOG_KNXPROJ_FILTER(self) -> str:
        return _("ETS project (*.knxproj)")

    @property
    def FILE_DIALOG_PROJECT_TITLE(self) -> str:
        return _("Open XKNX project")

    @property
    def FILE_DIALOG_PROJECT_SAVE_TITLE(self) -> str:
        return _("Save XKNX project")

    @property
    def FILE_DIALOG_PROJECT_FILTER(self) -> str:
        return _("XKNX project (*.xknx)")

    @property
    def FILE_DIALOG_OPEN_FILTER(self) -> str:
        return _("Projects (*.xknx, *.knxproj)")

    @property
    def PROGRESS_TITLE(self) -> str:
        return _("Working…")

    @property
    def IMPORT_PROGRESS_TEXT(self) -> str:
        return _("Importing project — this can take a while for large projects.")

    @property
    def PROGRESS_LOAD_KNXPROD(self) -> str:
        return _("Loading product catalog…")

    @property
    def PROGRESS_OPEN_PROJECT(self) -> str:
        return _("Opening project…")

    @property
    def IMPORT_PASSWORD_TITLE(self) -> str:
        return _("Project password")

    @property
    def IMPORT_PASSWORD_PROMPT(self) -> str:
        return _("This ETS project is password protected. Enter its password:")

    @property
    def IMPORT_PASSWORD_WRONG(self) -> str:
        return _("Wrong password, please try again.")

    @property
    def BTN_OK(self) -> str:
        return _("OK")

    @property
    def BTN_CANCEL(self) -> str:
        return _("Cancel")


class _CombinedStrings(BaseStrings, MenuStrings):
    pass


S = _CombinedStrings()
