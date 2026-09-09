"""Project plugin strings."""

from pathlib import Path

from knx_gui.strings import BaseStrings, create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("project", _locale_dir)


class ProjectStrings(BaseStrings):
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
    def CONFIGURE_ID(self) -> str:
        return _("ID")

    @property
    def CONFIGURE_INDIVIDUAL_ADDRESS(self) -> str:
        return _("Individual Address")

    @property
    def BTN_PROGRAM_DEVICE(self) -> str:
        return _("Program Device")

    @property
    def PROGRAM_STEP_FIND_DEVICE(self) -> str:
        return _("1. Find Device")

    @property
    def PROGRAM_STEP_MODE(self) -> str:
        return _("2. Programming Mode")

    @property
    def PROGRAM_TRIGGER_HEADER(self) -> str:
        return _("Trigger")

    @property
    def PROGRAM_TRIGGER_BUTTON(self) -> str:
        return _("Programming Button")

    @property
    def PROGRAM_TRIGGER_SERIAL(self) -> str:
        return _("Serial Number")

    @property
    def PROGRAM_TRIGGER_HELP_BUTTON(self) -> str:
        return _(
            "Press the programming button on the device, then click Program - "
            "its LED lights up while it's in programming mode. Only one device "
            "on the bus should be in programming mode at a time."
        )

    @property
    def PROGRAM_TRIGGER_HELP_SERIAL(self) -> str:
        return _(
            "Programs the device with this serial number - no button press "
            "needed, and safe with other devices on the bus."
        )

    @property
    def PROGRAM_SERIAL_INVALID(self) -> str:
        return _("Serial number must be 12 hex characters (6 bytes)")

    @property
    def PROGRAM_SERIAL_MISSING(self) -> str:
        return _("Enter a serial number")

    @property
    def BTN_NEXT(self) -> str:
        return _("Next")

    @property
    def BTN_BACK(self) -> str:
        return _("Back")

    @property
    def PROGRAM_SCOPE_HEADER(self) -> str:
        return _("Scope")

    @property
    def PROGRAM_SCOPE_FULL(self) -> str:
        return _("Full")

    @property
    def PROGRAM_SCOPE_PARTIAL(self) -> str:
        return _("Partial")

    @property
    def PROGRAM_SCOPE_GROUP_ADDRESSES(self) -> str:
        return _("Group Addresses")

    @property
    def PROGRAM_SCOPE_PARAMETERS(self) -> str:
        return _("Parameters")

    @property
    def PROGRAM_SCOPE_NONE_SELECTED(self) -> str:
        return _("Select at least one part to program")

    @property
    def PROGRAM_NOT_YET_SUPPORTED(self) -> str:
        return _(
            "Group Addresses and Parameters download aren't implemented yet - "
            "only Individual Address programming actually runs on the bus."
        )

    @property
    def BTN_PROGRAM(self) -> str:
        return _("Program")

    @property
    def BTN_PROGRAM_ANOTHER(self) -> str:
        return _("Start Over")

    @property
    def PROGRAM_CHECKLIST_ADDRESS_BUTTON(self) -> str:
        return _("Waiting for a device in programming mode")

    @property
    def PROGRAM_CHECKLIST_ADDRESS_SERIAL(self) -> str:
        return _("Addressing device by serial number")

    @property
    def PROGRAM_CHECKLIST_WRITE_IA(self) -> str:
        return _("Write Individual Address {address}")

    @property
    def PROGRAM_CHECKLIST_GA_PARAMS(self) -> str:
        return _("Group Addresses / Parameters - not implemented yet")

    @property
    def PROGRAM_LOG_NOT_CONNECTED(self) -> str:
        return _("Not connected - nothing was sent")

    @property
    def PROGRAM_STATUS_ERROR(self) -> str:
        return _("Failed: {error}")

    @property
    def CONFIGURE_METADATA(self) -> str:
        return _("Metadata")

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
    def CONFIGURE_MASK_VERSION(self) -> str:
        return _("Mask Version")

    @property
    def CONFIGURE_PEI_TYPE(self) -> str:
        return _("PEI Type")

    @property
    def CONFIGURE_APPLICATION_NUMBER(self) -> str:
        return _("Application Number")

    @property
    def CONFIGURE_APPLICATION_VERSION(self) -> str:
        return _("Application Version")

    @property
    def CONFIGURE_PROGRAM_TYPE(self) -> str:
        return _("Program Type")

    @property
    def CONFIGURE_LOAD_PROCEDURE_STYLE(self) -> str:
        return _("Load Procedure Style")

    @property
    def CONFIGURE_LINKABLE(self) -> str:
        return _("Linkable")

    @property
    def CONFIGURE_DYNAMIC_TABLE_MANAGEMENT(self) -> str:
        return _("Dynamic Table Management")

    @property
    def CONFIGURE_SECURE_ENABLED(self) -> str:
        return _("Secure Enabled")

    @property
    def CONFIGURE_ADDITIONAL_ADDRESSES(self) -> str:
        return _("Additional Addresses")

    @property
    def CONFIGURE_DESCRIPTION(self) -> str:
        return _("Description")

    @property
    def CONFIGURE_ORIGINAL_MANUFACTURER(self) -> str:
        return _("Original Manufacturer")

    @property
    def CONFIGURE_ORDER_NUMBER(self) -> str:
        return _("Order Number")

    @property
    def CONFIGURE_SERIAL_NUMBER(self) -> str:
        return _("Serial Number")

    @property
    def CONFIGURE_VERSION_NUMBER(self) -> str:
        return _("Version Number")

    @property
    def CONFIGURE_BUS_CURRENT(self) -> str:
        return _("Bus Current")

    @property
    def CONFIGURE_RAIL_MOUNTED(self) -> str:
        return _("Rail Mounted")

    @property
    def CONFIGURE_WIDTH(self) -> str:
        return _("Width")

    @property
    def CONFIGURE_ROLE(self) -> str:
        return _("Role")

    @property
    def ROLE_COUPLER(self) -> str:
        return _("Coupler")

    @property
    def ROLE_POWER_SUPPLY(self) -> str:
        return _("Power Supply")

    @property
    def ROLE_IP_ENABLED(self) -> str:
        return _("IP-enabled")

    @property
    def ROLE_END_DEVICE(self) -> str:
        return _("End Device")

    @property
    def YES(self) -> str:
        return _("Yes")

    @property
    def NO(self) -> str:
        return _("No")

    @property
    def CONFIGURE_PARAMETERS(self) -> str:
        return _("Parameters ({count})")

    @property
    def CONFIGURE_COM_FLAGS(self) -> str:
        return _("Com Flags ({count})")

    @property
    def TOOLTIP_LOCKED(self) -> str:
        return _("{name} (locked)")

    @property
    def CONFIGURE_LOAD_PROCEDURES(self) -> str:
        return _("Load Procedures ({count})")

    @property
    def BTN_PREVIEW_MEMORY(self) -> str:
        return _("Preview Memory")

    @property
    def CONFIGURE_RESET_SECTION(self) -> str:
        return _("Advanced Actions")

    @property
    def CONFIGURE_RESET_HEADER(self) -> str:
        return _("Reset Device")

    @property
    def BTN_RESET(self) -> str:
        return _("Reset")

    @property
    def RESET_MODE_BASIC_RESTART(self) -> str:
        return _("Basic Restart (unconfirmed)")

    @property
    def RESET_MODE_CONFIRMED_RESTART(self) -> str:
        return _("Confirmed Restart - resets nothing")

    @property
    def RESET_MODE_FACTORY_RESET(self) -> str:
        return _("Factory Reset - all Resources, incl. Individual Address")

    @property
    def RESET_MODE_RESET_IA(self) -> str:
        return _("Reset Individual Address")

    @property
    def RESET_MODE_RESET_AP(self) -> str:
        return _("Reset Application Program")

    @property
    def RESET_MODE_RESET_PARAM(self) -> str:
        return _("Reset Application Parameters")

    @property
    def RESET_MODE_RESET_LINKS(self) -> str:
        return _("Reset Group Object Links")

    @property
    def RESET_MODE_FACTORY_RESET_NO_IA(self) -> str:
        return _("Factory Reset - keep Individual Address")

    @property
    def RESET_MODE_ERASE_APP_DATA(self) -> str:
        return _("Erase Persistently Stored Application Data")

    @property
    def POPUP_CONFIRM_RESET_TITLE(self) -> str:
        return _("Confirm Reset")

    @property
    def POPUP_CONFIRM_RESET_TEXT(self) -> str:
        return _("This will {mode} on {device}.\nThis cannot be undone. Continue?")

    @property
    def BTN_CANCEL(self) -> str:
        return _("Cancel")

    @property
    def CONFIGURE_MEMORY_PREVIEW(self) -> str:
        return _("Memory Preview")

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
