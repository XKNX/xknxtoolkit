"""ETS-like Group Addresses view: the named range tree (main/middle/…) down to group addresses.

Shows, for the selected group address, the device com-objects assigned to it, and lets the user
create / rename / delete group addresses and set their datapoint type (context menus + modals,
mirroring the Devices panel)."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui._filter import filter_box

if TYPE_CHECKING:
    from knx_gui.device import Device
    from knx_gui.plugins.project.service import _Assignment
    from xknxmono.project.core.service import GroupRangeInfo


class GroupAddressesPanel:
    def __init__(
        self,
        get_range_tree: "Callable[[], list[GroupRangeInfo]]",
        get_assignments_for_ga: "Callable[[int], list[_Assignment]]",
        get_devices: "Callable[[], list[Device]]",
        on_create_ga: Callable[[str, str], None],
        on_rename_ga: Callable[[int, str], None],
        on_set_ga_dpt: Callable[[int, str], None],
        on_remove_ga: Callable[[int], None],
    ) -> None:
        self._get_range_tree = get_range_tree
        self._get_assignments_for_ga = get_assignments_for_ga
        self._get_devices = get_devices
        self._on_create_ga = on_create_ga
        self._on_rename_ga = on_rename_ga
        self._on_set_ga_dpt = on_set_ga_dpt
        self._on_remove_ga = on_remove_ga
        self._filter_text: str = ""
        self._selected_ga_id: int | None = None
        self._selected_ga_text: str = ""
        self._selected_ga_description: str = ""
        self._selected_ga_comment: str = ""
        # Modal state.
        self._popup_ga_id: int = 0
        self._popup_address: str = ""
        self._popup_name: str = ""
        self._popup_dpt: str = ""
        self._open_new_ga = False
        self._open_rename_ga = False
        self._open_set_dpt = False

    def render(self) -> None:
        tree = self._get_range_tree()

        if imgui.begin_popup_context_window("##ga_context"):
            if imgui.menu_item(S.GA_NEW, "", False)[0]:
                self._popup_address = ""
                self._popup_name = ""
                self._open_new_ga = True
            imgui.end_popup()

        if self._open_new_ga:
            imgui.open_popup(S.GA_NEW)
            self._open_new_ga = False
        if self._open_rename_ga:
            imgui.open_popup(S.GA_RENAME)
            self._open_rename_ga = False
        if self._open_set_dpt:
            imgui.open_popup(S.GA_SET_DPT)
            self._open_set_dpt = False
        self._render_new_ga_popup()
        self._render_rename_popup()
        self._render_dpt_popup()

        if not tree:
            imgui.text_disabled(S.GA_NO_PROJECT)
            return

        self._filter_text = filter_box(
            "##ga_filter", S.GA_FILTER_HINT, self._filter_text
        )
        flt = self._filter_text.strip().lower()

        avail = imgui.get_content_region_avail()
        tree_height = max(avail.y * 0.6, 0.0)
        if imgui.begin_child("##ga_tree", imgui.ImVec2(0.0, tree_height)):
            for node in tree:
                self._render_range(node, flt)
        imgui.end_child()

        imgui.separator()
        self._render_assignments()

    def _render_range(self, node: "GroupRangeInfo", flt: str = "") -> None:
        if flt and not self._range_has_match(node, flt):
            return  # while filtering, hide ranges with no matching group address
        label = (
            f"{node.name}##gr{node.id}" if node.name else f"[{node.id}]##gr{node.id}"
        )
        if flt:
            imgui.set_next_item_open(True, imgui.Cond_.always)
        if not imgui.tree_node_ex(label, imgui.TreeNodeFlags_.default_open):
            return
        for child in node.children:
            self._render_range(child, flt)
        for ga in node.group_addresses:
            if flt and not self._ga_matches(ga, flt):
                continue
            selected = ga.id == self._selected_ga_id
            ga_label = f"{ga.text}  {ga.name}##ga{ga.id}"
            if imgui.selectable(ga_label, selected)[0]:
                self._selected_ga_id = ga.id
                self._selected_ga_text = f"{ga.text}  {ga.name}"
                self._selected_ga_description = ga.description
                self._selected_ga_comment = ga.comment
            self._render_ga_context_menu(ga)
        imgui.tree_pop()

    @staticmethod
    def _ga_matches(ga: object, flt: str) -> bool:
        text = getattr(ga, "text", "") or ""
        name = getattr(ga, "name", "") or ""
        return flt in text.lower() or flt in name.lower()

    def _range_has_match(self, node: "GroupRangeInfo", flt: str) -> bool:
        if any(self._ga_matches(ga, flt) for ga in node.group_addresses):
            return True
        return any(self._range_has_match(child, flt) for child in node.children)

    def _render_ga_context_menu(self, ga: object) -> None:
        # ga is a core GroupAddressInfo (id, text, name, datapoint_type, …).
        if not imgui.begin_popup_context_item(f"##ga_ctx_{ga.id}"):  # type: ignore[attr-defined]
            return
        if imgui.menu_item(S.CONTEXT_RENAME, "", False)[0]:
            self._popup_ga_id = ga.id  # type: ignore[attr-defined]
            self._popup_name = ga.name  # type: ignore[attr-defined]
            self._open_rename_ga = True
        if imgui.menu_item(S.GA_SET_DPT, "", False)[0]:
            self._popup_ga_id = ga.id  # type: ignore[attr-defined]
            self._popup_dpt = ga.datapoint_type or ""  # type: ignore[attr-defined]
            self._open_set_dpt = True
        if imgui.menu_item(S.CONTEXT_COPY_ADDRESS, "", False)[0]:
            imgui.set_clipboard_text(getattr(ga, "text", "") or "")
        imgui.separator()
        if imgui.menu_item(S.CONTEXT_DELETE, "", False)[0]:
            self._on_remove_ga(ga.id)  # type: ignore[attr-defined]
            if self._selected_ga_id == ga.id:  # type: ignore[attr-defined]
                self._selected_ga_id = None
        imgui.end_popup()

    def _render_new_ga_popup(self) -> None:
        if not imgui.begin_popup_modal(
            S.GA_NEW, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.text_disabled(S.GA_ADDRESS)
        imgui.set_next_item_width(220.0)
        _, self._popup_address = imgui.input_text_with_hint(
            "##ga_addr", "1/2/3", self._popup_address
        )
        imgui.text_disabled(S.POPUP_NAME)
        imgui.set_next_item_width(220.0)
        _, self._popup_name = imgui.input_text("##ga_new_name", self._popup_name)
        btn_w = imgui.ImVec2(120, 0)
        if imgui.button(S.BTN_OK, btn_w) and self._popup_address.strip():
            self._on_create_ga(self._popup_address.strip(), self._popup_name)
            imgui.close_current_popup()
        imgui.same_line()
        if imgui.button(S.BTN_CANCEL, btn_w):
            imgui.close_current_popup()
        imgui.end_popup()

    def _render_rename_popup(self) -> None:
        if not imgui.begin_popup_modal(
            S.GA_RENAME, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.set_next_item_width(220.0)
        _, self._popup_name = imgui.input_text("##ga_rename", self._popup_name)
        btn_w = imgui.ImVec2(120, 0)
        if imgui.button(S.BTN_OK, btn_w):
            self._on_rename_ga(self._popup_ga_id, self._popup_name)
            imgui.close_current_popup()
        imgui.same_line()
        if imgui.button(S.BTN_CANCEL, btn_w):
            imgui.close_current_popup()
        imgui.end_popup()

    def _render_dpt_popup(self) -> None:
        if not imgui.begin_popup_modal(
            S.GA_SET_DPT, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.text_disabled(S.GA_DPT_HINT)
        imgui.set_next_item_width(220.0)
        _, self._popup_dpt = imgui.input_text_with_hint(
            "##ga_dpt", "DPST-1-1", self._popup_dpt
        )
        btn_w = imgui.ImVec2(120, 0)
        if imgui.button(S.BTN_OK, btn_w):
            self._on_set_ga_dpt(self._popup_ga_id, self._popup_dpt.strip())
            imgui.close_current_popup()
        imgui.same_line()
        if imgui.button(S.BTN_CANCEL, btn_w):
            imgui.close_current_popup()
        imgui.end_popup()

    def _render_assignments(self) -> None:
        if self._selected_ga_id is None:
            imgui.text_disabled(S.GA_ASSIGNED_OBJECTS)
            return
        imgui.text_disabled(self._selected_ga_text)
        if self._selected_ga_description:
            imgui.text_wrapped(f"{S.GA_DESCRIPTION}: {self._selected_ga_description}")
        if self._selected_ga_comment:
            imgui.text_wrapped(f"{S.GA_COMMENT}: {self._selected_ga_comment}")

        names = self._com_object_names()
        assignments = self._get_assignments_for_ga(self._selected_ga_id)
        flags = imgui.TableFlags_.borders_inner | imgui.TableFlags_.sizing_stretch_prop
        if not imgui.begin_table("##ga_assignments", 3, flags):
            return
        imgui.table_setup_column("Device", imgui.TableColumnFlags_.width_stretch, 0.5)
        imgui.table_setup_column("Object", imgui.TableColumnFlags_.width_stretch, 0.4)
        imgui.table_setup_column("S", imgui.TableColumnFlags_.width_fixed, 20.0)
        imgui.table_headers_row()
        for a in assignments:
            device_name, co_name = names.get(a.com_object_id, ("?", "?"))
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            imgui.text(device_name)
            imgui.table_set_column_index(1)
            imgui.text_disabled(co_name)
            imgui.table_set_column_index(2)
            if a.is_sending:
                imgui.text("→")
        imgui.end_table()

    def _com_object_names(self) -> dict[int, tuple[str, str]]:
        names: dict[int, tuple[str, str]] = {}
        for device in self._get_devices():
            label = device.name or device.individual_address or "?"
            for co in device.com_objects:
                if co.db_id is not None:
                    names[co.db_id] = (label, co.name)
        return names
