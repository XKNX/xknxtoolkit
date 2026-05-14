"""Project plugin strings."""

from pathlib import Path

from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("project", _locale_dir)


class ProjectStrings:
    @property
    def PANEL_DEVICES(self) -> str:
        return _("Devices")

    @property
    def PANEL_CONFIGURE(self) -> str:
        return _("Configure")

    @property
    def PANEL_HISTORY(self) -> str:
        return _("History")

    @property
    def CONFIGURE_NO_DEVICES(self) -> str:
        return _("No devices")

    @property
    def CONFIGURE_NAME(self) -> str:
        return _("Name")

    @property
    def CONFIGURE_INDIVIDUAL_ADDRESS(self) -> str:
        return _("Individual Address")

    @property
    def CONFIGURE_MANUFACTURER(self) -> str:
        return _("Manufacturer")

    @property
    def CONFIGURE_APPLICATION(self) -> str:
        return _("Application")

    @property
    def CONFIGURE_HARDWARE(self) -> str:
        return _("Hardware")

    @property
    def CONFIGURE_FIRMWARE(self) -> str:
        return _("Firmware")

    @property
    def CONFIGURE_PARAMETERS(self) -> str:
        return _("Parameters ({count})")

    @property
    def CONFIGURE_COM_FLAGS(self) -> str:
        return _("Com Flags ({count})")

    @property
    def DEVICE_AREA(self) -> str:
        return _("Area {area}")

    @property
    def DEVICE_AREA_NAMED(self) -> str:
        return _("{name} (Area {area})")

    @property
    def DEVICE_LINE(self) -> str:
        return _("Line {area}.{line}")

    @property
    def DEVICE_LINE_NAMED(self) -> str:
        return _("{name} (Line {area}.{line})")

    @property
    def DEVICE_UNASSIGNED(self) -> str:
        return _("Unassigned ({count})")

    @property
    def CONTEXT_ADD_AREA(self) -> str:
        return _("Add Area")

    @property
    def CONTEXT_ADD_LINE(self) -> str:
        return _("Add Line")

    @property
    def CONTEXT_RENAME(self) -> str:
        return _("Rename")

    @property
    def CONTEXT_DELETE(self) -> str:
        return _("Delete")

    @property
    def POPUP_NEW_AREA(self) -> str:
        return _("New Area")

    @property
    def POPUP_NEW_LINE(self) -> str:
        return _("New Line")

    @property
    def POPUP_RENAME(self) -> str:
        return _("Rename")

    @property
    def POPUP_NUMBER(self) -> str:
        return _("Number")

    @property
    def POPUP_NAME(self) -> str:
        return _("Name")

    @property
    def STATUS_PROJECT(self) -> str:
        return _("Project: {name}")

    @property
    def STATUS_UNSAVED(self) -> str:
        return _("(unsaved)")

    @property
    def HISTORY_NO_HISTORY(self) -> str:
        return _("No history")

    @property
    def HISTORY_REVERT(self) -> str:
        return _("Restore")

    @property
    def HISTORY_DEVICE_ADD(self) -> str:
        return _("Add device: {name}")

    @property
    def HISTORY_DEVICE_REMOVE(self) -> str:
        return _("Remove device: {name}")

    @property
    def HISTORY_ADDRESS_CHANGE(self) -> str:
        return _("Address: {old} -> {new}")

    @property
    def HISTORY_NAME_CHANGE(self) -> str:
        return _("Name: {old} -> {new}")

    @property
    def HISTORY_PARAM_CHANGE(self) -> str:
        return _("Parameter: {old} -> {new}")

    @property
    def HISTORY_DPT_CHANGE(self) -> str:
        return _("DPT: {old} -> {new}")

    @property
    def HISTORY_FLAG_CHANGE(self) -> str:
        return _("Flag: {flag} -> {state}")

    @property
    def HISTORY_GA_CREATE(self) -> str:
        return _("Group address {address} created")

    @property
    def HISTORY_GA_REMOVE(self) -> str:
        return _("Group address {address} removed")

    @property
    def HISTORY_GA_RENAME(self) -> str:
        return _("Group address: {old} -> {new}")

    @property
    def HISTORY_CO_LINKED(self) -> str:
        return _("Com object linked to group address")

    @property
    def HISTORY_CO_UNLINKED(self) -> str:
        return _("Com object unlinked from group address")

    @property
    def HISTORY_AREA_CREATE(self) -> str:
        return _("Area {number} created")

    @property
    def HISTORY_AREA_REMOVE(self) -> str:
        return _("Area {number} removed")

    @property
    def HISTORY_AREA_RENAME(self) -> str:
        return _("Area: {old} -> {new}")

    @property
    def HISTORY_LINE_CREATE(self) -> str:
        return _("Line {number} created")

    @property
    def HISTORY_LINE_REMOVE(self) -> str:
        return _("Line {number} removed")

    @property
    def HISTORY_LINE_RENAME(self) -> str:
        return _("Line: {old} -> {new}")


S = ProjectStrings()
