"""Node editor plugin strings."""

from pathlib import Path

from knx_gui.strings import BaseStrings, create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("node_editor", _locale_dir)


class NodeEditorStrings(BaseStrings):
    @property
    def PANEL_NODE_EDITOR(self) -> str:
        return _("Node Editor")

    @property
    def STATUS_DEVICES_GAS(self) -> str:
        return _("Devices: {devices} | Group Addresses: {group_addresses}")

    @property
    def STATUS_SHOW_GA_NODES(self) -> str:
        return _("Show GA Nodes")

    @property
    def NODE_SELECT_DPT(self) -> str:
        return _("Select DPT")

    @property
    def NODE_DEFAULT_FOR(self) -> str:
        return _("Default for {direction}:")

    @property
    def NODE_MODIFIED(self) -> str:
        return _("(modified)")

    @property
    def NODE_IMAGE_PLACEHOLDER(self) -> str:
        return _("(image)")

    @property
    def NODE_COM_FLAGS(self) -> str:
        return _("Com Flags")

    @property
    def NODE_PARAMETERS(self) -> str:
        return _("Parameters")

    @property
    def LINK_WARNING_HIDE_COM_OBJECTS(self) -> str:
        return _("This change will hide the following communication objects:")

    @property
    def LINK_WARNING_REMOVED(self) -> str:
        return _("{count} link(s) will be removed.")

    @property
    def LINK_CANNOT_CONNECT_OUTPUTS(self) -> str:
        return _("Cannot connect two outputs")

    @property
    def LINK_CANNOT_CONNECT_INPUTS(self) -> str:
        return _("Cannot connect two inputs")

    @property
    def LINK_INCOMPATIBLE_DPTS(self) -> str:
        return _("Incompatible DPTs")

    @property
    def LINK_WARNING_LOOSE_MATCH(self) -> str:
        return _("Warning: same byte format, different semantics")

    @property
    def LINK_DPT_INFO(self) -> str:
        return _("DPT {code} - {name}")

    @property
    def LINK_FROM_DPT(self) -> str:
        return _("From: DPT {code} - {name}")

    @property
    def LINK_TO_DPT(self) -> str:
        return _("To:   DPT {code} - {name}")

    @property
    def BTN_REMOVE_LINKS(self) -> str:
        return _("Remove Links")

    @property
    def TOOLTIP_LOCKED(self) -> str:
        return _("{name} (locked)")


S = NodeEditorStrings()
