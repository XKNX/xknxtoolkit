"""ETS-like "Group Objects" table: each com-object with its assigned group addresses and flags.

Complements :class:`~knx_gui.widgets.com_flags_widgets.ComFlagsTable` (which shows only flags) by
adding the group-address assignment column, including linking/unlinking addresses.
"""

from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.device import FLAG_LABELS, ComObject, Device
from knx_gui.plugins.node_editor.strings import S

# One com-object → group-address link: (assignment_id, group_address_id, text, is_sending).
GroupLink = tuple[int, int, str, bool]
# Resolver: com-object db id -> its links.
GroupLinkResolver = Callable[[int], list[GroupLink]]
# All assignable group addresses: (group_address_id, text).
GroupAddressCatalog = Callable[[], list[tuple[int, str]]]


class GroupObjectsTable:
    def __init__(
        self,
        set_flag: Callable[[Device, str, str, bool], None],
        on_link: Callable[[int, int], None],
        on_unlink: Callable[[int], None],
    ) -> None:
        self._set_flag = set_flag
        self._on_link = on_link
        self._on_unlink = on_unlink
        self._picker_filter = ""

    def render(
        self,
        device: Device,
        com_objects: list[ComObject],
        get_links: GroupLinkResolver,
        get_all_group_addresses: GroupAddressCatalog,
    ) -> None:
        flags = (
            imgui.TableFlags_.borders_inner
            | imgui.TableFlags_.sizing_stretch_prop
            | imgui.TableFlags_.resizable
        )
        n_cols = 4 + len(FLAG_LABELS)
        if not imgui.begin_table(f"##group_objects_{device.node_id}", n_cols, flags):
            return

        imgui.table_setup_column("#", imgui.TableColumnFlags_.width_fixed, 32.0)
        imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch, 0.3)
        imgui.table_setup_column("DPT", imgui.TableColumnFlags_.width_stretch, 0.12)
        imgui.table_setup_column(
            "Group Addresses", imgui.TableColumnFlags_.width_stretch, 0.58
        )
        for _attr, letter, _name in FLAG_LABELS:
            imgui.table_setup_column(letter, imgui.TableColumnFlags_.width_fixed, 22.0)
        imgui.table_headers_row()

        for com_obj in com_objects:
            self._render_row(device, com_obj, get_links, get_all_group_addresses)

        imgui.end_table()

    def _render_row(
        self,
        device: Device,
        com_object: ComObject,
        get_links: GroupLinkResolver,
        get_all_group_addresses: GroupAddressCatalog,
    ) -> None:
        row_id = f"{device.node_id}_{com_object.id}"
        imgui.table_next_row()

        imgui.table_set_column_index(0)
        imgui.text_disabled(str(com_object.number))

        imgui.table_set_column_index(1)
        imgui.text(com_object.name)

        imgui.table_set_column_index(2)
        imgui.text_disabled(getattr(com_object.dpt, "name", "") or "")

        imgui.table_set_column_index(3)
        db_id = com_object.db_id
        links = get_links(db_id) if db_id is not None else []
        # Sending group address first (marked with an arrow); the rest are receive-only.
        for assignment_id, _ga_id, text, is_sending in sorted(
            links, key=lambda link: not link[3]
        ):
            if imgui.small_button(f"x##unlink{assignment_id}"):
                self._on_unlink(assignment_id)
            imgui.same_line()
            imgui.text(f"→ {text}" if is_sending else text)
        if db_id is not None:
            self._render_add(db_id, links, get_all_group_addresses)

        for col, (attr, _letter, full_name) in enumerate(FLAG_LABELS, start=4):
            imgui.table_set_column_index(col)
            current = getattr(com_object.flags, attr)
            is_locked = (
                getattr(com_object.flags, f"{attr}_locked", False)
                if attr != "communication"
                else False
            )
            if is_locked:
                imgui.begin_disabled()
            changed, new_value = imgui.checkbox(f"##{row_id}_{attr}", current)
            if changed and not is_locked:
                self._set_flag(device, com_object.id, attr, new_value)
            if is_locked:
                imgui.end_disabled()
            if imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_disabled):
                imgui.set_tooltip(
                    S.TOOLTIP_LOCKED.format(name=full_name) if is_locked else full_name
                )

    def _render_add(
        self,
        db_id: int,
        links: list[GroupLink],
        get_all_group_addresses: GroupAddressCatalog,
    ) -> None:
        popup_id = f"##addga{db_id}"
        if imgui.small_button(f"+##add{db_id}"):
            self._picker_filter = ""
            imgui.open_popup(popup_id)
        if not imgui.begin_popup(popup_id):
            return
        already = {ga_id for _aid, ga_id, _text, _sending in links}
        imgui.set_next_item_width(240.0)
        _, self._picker_filter = imgui.input_text_with_hint(
            "##ga_filter", S.SEARCH_HINT, self._picker_filter
        )
        needle = self._picker_filter.lower()
        if imgui.begin_child("##ga_list", imgui.ImVec2(240.0, 260.0)):
            for ga_id, text in get_all_group_addresses():
                if ga_id in already or (needle and needle not in text.lower()):
                    continue
                if imgui.selectable(f"{text}##pick{db_id}_{ga_id}", False)[0]:
                    self._on_link(db_id, ga_id)
                    imgui.close_current_popup()
        imgui.end_child()
        imgui.end_popup()
