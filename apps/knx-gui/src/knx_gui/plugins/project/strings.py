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
    def PANEL_EDITOR(self) -> str:
        return _("Editor")

    @property
    def PANEL_GROUP_ADDRESSES(self) -> str:
        return _("Group Addresses")

    @property
    def PANEL_BUILDINGS(self) -> str:
        return _("Buildings")

    @property
    def PANEL_PROJECT_INFO(self) -> str:
        return _("Project")

    @property
    def SPACES_EMPTY(self) -> str:
        return _("No buildings/rooms in this project")

    @property
    def PROJECT_INFO_EMPTY(self) -> str:
        return _("No project")

    @property
    def PROJECT_INFO_NAME(self) -> str:
        return _("Name")

    @property
    def PROJECT_INFO_GA_STYLE(self) -> str:
        return _("Group address style")

    @property
    def PROJECT_INFO_CREATED_BY(self) -> str:
        return _("Created by")

    @property
    def PROJECT_INFO_TOOL_VERSION(self) -> str:
        return _("Tool version")

    @property
    def PROJECT_INFO_SCHEMA_VERSION(self) -> str:
        return _("Schema version")

    @property
    def PROJECT_INFO_LAST_MODIFIED(self) -> str:
        return _("Last modified")

    @property
    def PROJECT_INFO_GUID(self) -> str:
        return _("GUID")

    @property
    def CONFIGURE_ORDER_NUMBER(self) -> str:
        return _("Order number")

    @property
    def CONFIGURE_DESCRIPTION(self) -> str:
        return _("Description")

    @property
    def GA_DESCRIPTION(self) -> str:
        return _("Description")

    @property
    def GA_COMMENT(self) -> str:
        return _("Comment")

    @property
    def EDITOR_TAB_PARAMETERS(self) -> str:
        return _("Parameters ({count})")

    @property
    def EDITOR_TAB_GROUP_OBJECTS(self) -> str:
        return _("Group Objects ({count})")

    @property
    def GA_NO_PROJECT(self) -> str:
        return _("No project")

    @property
    def GA_ASSIGNED_OBJECTS(self) -> str:
        return _("Assigned objects")

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
    def BTN_PROGRAM_DEVICE(self) -> str:
        return _("Program Device")

    @property
    def BTN_EVAL_DEVICE(self) -> str:
        return _("Test Before Programming")

    @property
    def PROGRAM_CONFIRM_TITLE(self) -> str:
        return _("Program device?")

    @property
    def PROGRAM_CONFIRM_TEXT(self) -> str:
        return _(
            "This writes to the device at {address} (scope: {scope}) and changes its "
            "configuration. Continue?"
        )

    @property
    def CONFIGURE_DOWNLOAD_SCOPE(self) -> str:
        return _("Download")

    @property
    def SCOPE_FULL(self) -> str:
        return _("Full")

    @property
    def SCOPE_PARAMETERS(self) -> str:
        return _("Partial: Parameters")

    @property
    def SCOPE_GROUP_COMMUNICATION(self) -> str:
        return _("Partial: Group Communication")

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
    def CONFIGURE_LOAD_PROCEDURES(self) -> str:
        return _("Load Procedures ({count})")

    @property
    def BTN_PREVIEW_MEMORY(self) -> str:
        return _("Preview Memory")

    @property
    def CONFIGURE_MEMORY_PREVIEW(self) -> str:
        return _("Memory Preview")

    @property
    def PREFLIGHT_RESULT_TITLE(self) -> str:
        return _("Programming test result")

    @property
    def PREFLIGHT_FAILED(self) -> str:
        return _("Evaluation failed")

    @property
    def PREFLIGHT_NO_CHANGES_MADE(self) -> str:
        return _(
            "Read-only test: checks that the download function generates the same image "
            "as what is already programmed on the device. Nothing is written to the device."
        )

    @property
    def PREFLIGHT_PROJECT_MODIFIED(self) -> str:
        return _(
            "Cannot run: the project was changed since import. This test compares the "
            "generated image against the device's programmed state, which only matches "
            "an unedited (freshly imported) project. Undo your changes or re-import to test."
        )

    @property
    def PREFLIGHT_NO_CONNECTION(self) -> str:
        return _(
            "Cannot run: no KNX connection. Connect to a gateway (Connection menu) "
            "and make sure the device is reachable at its individual address."
        )

    @property
    def PREFLIGHT_MATCH(self) -> str:
        return _("Match: the generated image is identical to what is on the device")

    @property
    def PREFLIGHT_WOULD_CHANGE(self) -> str:
        return _(
            "Mismatch: {bytes} byte(s) differ from the device in {locations} location(s)"
        )

    @property
    def PREFLIGHT_SUMMARY_COUNTS(self) -> str:
        return _("{matched} matched, {changed} would change")

    @property
    def PREFLIGHT_COL_LOCATION(self) -> str:
        return _("Location")

    @property
    def PREFLIGHT_COL_SIZE(self) -> str:
        return _("Size")

    @property
    def PREFLIGHT_COL_STATUS(self) -> str:
        return _("Status")

    @property
    def PREFLIGHT_COL_CHANGED(self) -> str:
        return _("Changed")

    @property
    def PREFLIGHT_STATUS_MATCH(self) -> str:
        return _("match")

    @property
    def PREFLIGHT_STATUS_CHANGE(self) -> str:
        return _("would change")

    @property
    def PREFLIGHT_STATUS_RUNTIME(self) -> str:
        return _("device-managed")

    @property
    def PREFLIGHT_RUNTIME_TOOLTIP(self) -> str:
        return _(
            "System byte the device sets itself at runtime (e.g. a download "
            "detection byte reset by the application after a download). A "
            "difference here is expected and does not indicate a bad download."
        )

    @property
    def PREFLIGHT_RUNTIME_NOTE(self) -> str:
        return _("plus {bytes} device-managed runtime byte(s) (expected, benign)")

    @property
    def PREFLIGHT_EXPORT(self) -> str:
        return _("Export Ist/Soll...")

    @property
    def PREFLIGHT_EXPORT_PATH(self) -> str:
        return _("Export path:")

    @property
    def PREFLIGHT_MEM_LABEL(self) -> str:
        return _("memory {address}")

    @property
    def PREFLIGHT_PROP_LABEL(self) -> str:
        return _("object {object} property {property}")

    @property
    def DEVICE_FILTER_HINT(self) -> str:
        return _("Filter devices (name, address)...")

    @property
    def DEVICE_EMPTY_HINT(self) -> str:
        return _(
            "No devices. Open or import a project (File menu), "
            "or right-click here to add an area."
        )

    @property
    def GA_FILTER_HINT(self) -> str:
        return _("Filter group addresses (address, name)...")

    @property
    def SPACES_FILTER_HINT(self) -> str:
        return _("Filter rooms, devices, functions...")

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
    def CONTEXT_COPY_ADDRESS(self) -> str:
        return _("Copy address")

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
    def BTN_ADD(self) -> str:
        return _("Add")

    @property
    def BTN_OK(self) -> str:
        return _("OK")

    @property
    def BTN_SAVE(self) -> str:
        return _("Save")

    @property
    def COPY_LOG(self) -> str:
        return _("Copy Log")

    @property
    def BTN_CANCEL(self) -> str:
        return _("Cancel")

    @property
    def GA_NEW(self) -> str:
        return _("New group address")

    @property
    def GA_RENAME(self) -> str:
        return _("Rename group address")

    @property
    def GA_SET_DPT(self) -> str:
        return _("Set datapoint type")

    @property
    def GA_ADDRESS(self) -> str:
        return _("Address")

    @property
    def GA_DPT_HINT(self) -> str:
        return _("Datapoint type (e.g. DPST-1-1); empty to clear")

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
