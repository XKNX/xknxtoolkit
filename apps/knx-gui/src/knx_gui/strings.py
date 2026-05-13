"""
Centralized UI strings for internationalization.

All user-facing text should be defined here to enable future translation support.
"""


class Strings:
    # Application
    APP_TITLE = "XKNX Toolkit"

    # Panel titles
    PANEL_DEVICES = "Devices"
    PANEL_CATALOG = "Catalog"
    PANEL_NODE_EDITOR = "Node Editor"
    PANEL_NETWORK = "Network"
    PANEL_CONFIGURE = "Configure"
    PANEL_HISTORY = "History"

    # Menu: File
    MENU_FILE = "File"
    MENU_NEW_PROJECT = "New Project"
    MENU_OPEN_PROJECT = "Open Project"
    MENU_SAVE_PROJECT = "Save Project"
    MENU_LOAD_KNXPROD = "Load .knxprod..."
    MENU_EXIT = "Exit"

    # Menu: Edit
    MENU_EDIT = "Edit"
    MENU_UNDO = "Undo"
    MENU_REDO = "Redo"

    # Menu: Connection
    MENU_CONNECTION = "Connection"
    MENU_CONNECT = "Connect"
    MENU_DISCONNECT = "Disconnect"

    # Status bar
    STATUS_CONNECTED = "Connected: {ip}"
    STATUS_CONNECTED_TO = "Connected to {ip}"
    STATUS_DISCONNECTED = "Disconnected"
    STATUS_DEVICES_LINKS = "| Devices: {devices} | Links: {links}"

    # Buttons
    BTN_ADD = "Add"
    BTN_CLOSE = "Close"
    BTN_CANCEL = "Cancel"
    BTN_COPY = "Copy"
    BTN_CLEAR = "Clear"
    BTN_REMOVE_LINKS = "Remove Links"
    BTN_RECORD = "Record"
    BTN_RECORDING = "Recording"
    BTN_STOP = "Stop"

    # Archive popup
    ARCHIVE_FAILED_TO_LOAD = "Failed to load archive"
    ARCHIVE_LOADED = "Loaded: {path}"
    ARCHIVE_FOUND_APPS = "Found {count} application(s)"
    ARCHIVE_COM_OBJECTS = "({count} com objects)"

    # Configure panel
    CONFIGURE_NO_DEVICES = "No devices"
    CONFIGURE_NAME = "Name"
    CONFIGURE_INDIVIDUAL_ADDRESS = "Individual Address"
    CONFIGURE_MANUFACTURER = "Manufacturer"
    CONFIGURE_APPLICATION = "Application"
    CONFIGURE_HARDWARE = "Hardware"
    CONFIGURE_FIRMWARE = "Firmware"
    CONFIGURE_PARAMETERS = "Parameters ({count})"
    CONFIGURE_COM_FLAGS = "Com Flags ({count})"

    # Telegrams panel
    TELEGRAMS_TITLE = "Telegrams"
    TELEGRAMS_SELECTED = "({count} selected)"

    # Node editor
    NODE_SELECT_DPT = "Select DPT"
    NODE_DEFAULT_FOR = "Default for {direction}:"
    NODE_MODIFIED = "(modified)"
    NODE_IMAGE_PLACEHOLDER = "(image)"
    NODE_COM_FLAGS = "Com Flags"
    NODE_PARAMETERS = "Parameters"

    # Link warnings
    LINK_WARNING_HIDE_COM_OBJECTS = (
        "This change will hide the following communication objects:"
    )
    LINK_WARNING_REMOVED = "{count} link(s) will be removed."
    LINK_CANNOT_CONNECT_OUTPUTS = "Cannot connect two outputs"
    LINK_CANNOT_CONNECT_INPUTS = "Cannot connect two inputs"
    LINK_INCOMPATIBLE_DPTS = "Incompatible DPTs"
    LINK_WARNING_LOOSE_MATCH = "Warning: same byte format, different semantics"
    LINK_DPT_INFO = "DPT {code} - {name}"
    LINK_FROM_DPT = "From: DPT {code} - {name}"
    LINK_TO_DPT = "To:   DPT {code} - {name}"

    # Device tree
    DEVICE_AREA = "Area {area}"
    DEVICE_AREA_NAMED = "{name} (Area {area})"
    DEVICE_LINE = "Line {area}.{line}"
    DEVICE_LINE_NAMED = "{name} (Line {area}.{line})"
    DEVICE_UNASSIGNED = "Unassigned ({count})"

    # Context menu
    CONTEXT_ADD_AREA = "Add Area"
    CONTEXT_ADD_LINE = "Add Line"
    CONTEXT_RENAME = "Rename"
    CONTEXT_DELETE = "Delete"

    # Popups
    POPUP_NEW_AREA = "New Area"
    POPUP_NEW_LINE = "New Line"
    POPUP_RENAME = "Rename"
    POPUP_NUMBER = "Number"
    POPUP_NAME = "Name"

    # Tooltips
    TOOLTIP_LOCKED = "{name} (locked)"

    # File dialogs
    FILE_DIALOG_KNXPROD_TITLE = "Open KNX product archive"
    FILE_DIALOG_KNXPROD_FILTER = "KNX product (*.knxprod)"
    FILE_DIALOG_PROJECT_TITLE = "Open XKNX project"
    FILE_DIALOG_PROJECT_SAVE_TITLE = "Save XKNX project"
    FILE_DIALOG_PROJECT_FILTER = "XKNX project (*.xknx)"
    FILE_DIALOG_ALL_FILES = "All files"

    # Shortcuts
    SHORTCUT_UNDO = "Ctrl+Z"
    SHORTCUT_REDO = "Ctrl+Y"

    # Status
    STATUS_PROJECT = "Project: {name}"
    STATUS_UNSAVED = "(unsaved)"

    # History panel
    HISTORY_NO_HISTORY = "No history"
    HISTORY_REVERT = "Restore"
    HISTORY_DEVICE_ADD = "Add device: {name}"
    HISTORY_DEVICE_REMOVE = "Remove device: {name}"
    HISTORY_ADDRESS_CHANGE = "Address: {old} -> {new}"
    HISTORY_NAME_CHANGE = "Name: {old} -> {new}"
    HISTORY_PARAM_CHANGE = "Parameter: {old} -> {new}"
    HISTORY_DPT_CHANGE = "DPT: {old} -> {new}"
    HISTORY_FLAG_CHANGE = "Flag: {flag} -> {state}"
    HISTORY_LINK_CREATE = "Link created"
    HISTORY_LINK_REMOVE = "Link removed"
    HISTORY_AREA_CREATE = "Area {number} created"
    HISTORY_AREA_REMOVE = "Area {number} removed"
    HISTORY_AREA_RENAME = "Area: {old} -> {new}"
    HISTORY_LINE_CREATE = "Line {number} created"
    HISTORY_LINE_REMOVE = "Line {number} removed"
    HISTORY_LINE_RENAME = "Line: {old} -> {new}"


S = Strings
