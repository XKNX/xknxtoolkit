from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S
from knx_gui.types import Device


@dataclass
class Area:
    id: int
    number: int
    name: str


@dataclass
class Line:
    id: int
    area_id: int
    number: int
    name: str


class DevicesPanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        get_areas: Callable[[], list[Area]],
        get_lines: Callable[[int], list[Line]],
        on_select_device: Callable[[Device], None],
        on_move_device: Callable[[Device, int, int], None],
        on_create_area: Callable[[int, str], None],
        on_remove_area: Callable[[Area], None],
        on_rename_area: Callable[[Area, str], None],
        on_create_line: Callable[[int, int, str], None],
        on_remove_line: Callable[[Line], None],
        on_rename_line: Callable[[Line, str], None],
    ) -> None:
        self._get_devices = get_devices
        self._get_areas = get_areas
        self._get_lines = get_lines
        self._on_select_device = on_select_device
        self._on_move_device = on_move_device
        self._on_create_area = on_create_area
        self._on_remove_area = on_remove_area
        self._on_rename_area = on_rename_area
        self._on_create_line = on_create_line
        self._on_remove_line = on_remove_line
        self._on_rename_line = on_rename_line
        self._dragging_device: Device | None = None

        self._popup_area_number: int = 0
        self._popup_line_number: int = 0
        self._popup_name: str = ""
        self._popup_target_area: Area | None = None
        self._popup_target_line: Line | None = None
        self._open_new_area_popup: bool = False
        self._open_new_line_popup: bool = False
        self._open_rename_popup: bool = False

    def render(self) -> None:
        devices = self._get_devices()
        areas = self._get_areas()
        device_tree = self._build_device_tree(devices)

        if imgui.begin_popup_context_window("##devices_context"):
            if imgui.menu_item(S.CONTEXT_ADD_AREA, "", False)[0]:
                self._popup_area_number = self._next_area_number(areas)
                self._popup_name = ""
                self._open_new_area_popup = True
            imgui.end_popup()

        if self._open_new_area_popup:
            imgui.open_popup(S.POPUP_NEW_AREA)
            self._open_new_area_popup = False
        if self._open_new_line_popup:
            imgui.open_popup(S.POPUP_NEW_LINE)
            self._open_new_line_popup = False
        if self._open_rename_popup:
            imgui.open_popup(S.POPUP_RENAME)
            self._open_rename_popup = False

        self._render_new_area_popup()
        self._render_new_line_popup()
        self._render_rename_popup()

        leaf_flags = (
            imgui.TreeNodeFlags_.leaf
            | imgui.TreeNodeFlags_.no_tree_push_on_open
            | imgui.TreeNodeFlags_.span_avail_width
        )

        for area in areas:
            lines = self._get_lines(area.id)
            area_label = self._format_area_label(area)
            area_flags = (
                imgui.TreeNodeFlags_.default_open
                | imgui.TreeNodeFlags_.span_avail_width
            )
            if imgui.tree_node_ex(f"{area_label}##area_{area.id}", area_flags):
                self._render_area_context_menu(area, lines)

                for line in lines:
                    line_label = self._format_line_label(area, line)
                    line_flags = (
                        imgui.TreeNodeFlags_.default_open
                        | imgui.TreeNodeFlags_.span_avail_width
                    )
                    if imgui.tree_node_ex(f"{line_label}##line_{line.id}", line_flags):
                        self._render_line_context_menu(line)
                        self._render_line_drop_target(area, line)

                        line_devices = device_tree.get(area.number, {}).get(
                            line.number, []
                        )
                        for device in line_devices:
                            imgui.tree_node_ex(
                                f"{device.name} ({device.individual_address})",
                                leaf_flags,
                            )
                            if imgui.is_item_clicked():
                                self._on_select_device(device)
                            self._render_device_drag_source(device)
                        imgui.tree_pop()
                imgui.tree_pop()

        unassigned = self._get_unassigned_devices(devices, areas)
        if unassigned:
            unassigned_flags = (
                imgui.TreeNodeFlags_.default_open
                | imgui.TreeNodeFlags_.span_avail_width
            )
            if imgui.tree_node_ex(
                S.DEVICE_UNASSIGNED.format(count=len(unassigned)), unassigned_flags
            ):
                for device in unassigned:
                    imgui.tree_node_ex(device.name, leaf_flags)
                    if imgui.is_item_clicked():
                        self._on_select_device(device)
                    self._render_device_drag_source(device)
                imgui.tree_pop()

    def _format_area_label(self, area: Area) -> str:
        if area.name:
            return S.DEVICE_AREA_NAMED.format(name=area.name, area=area.number)
        return S.DEVICE_AREA.format(area=area.number)

    def _format_line_label(self, area: Area, line: Line) -> str:
        if line.name:
            return S.DEVICE_LINE_NAMED.format(
                name=line.name, area=area.number, line=line.number
            )
        return S.DEVICE_LINE.format(area=area.number, line=line.number)

    def _render_area_context_menu(self, area: Area, lines: list[Line]) -> None:
        if imgui.begin_popup_context_item(f"##area_ctx_{area.id}"):
            if imgui.menu_item(S.CONTEXT_ADD_LINE, "", False)[0]:
                self._popup_target_area = area
                self._popup_line_number = self._next_line_number(lines)
                self._popup_name = ""
                self._open_new_line_popup = True
            if imgui.menu_item(S.CONTEXT_RENAME, "", False)[0]:
                self._popup_target_area = area
                self._popup_name = area.name
                self._open_rename_popup = True
            imgui.separator()
            if imgui.menu_item(S.CONTEXT_DELETE, "", False)[0]:
                self._on_remove_area(area)
            imgui.end_popup()

    def _render_line_context_menu(self, line: Line) -> None:
        if imgui.begin_popup_context_item(f"##line_ctx_{line.id}"):
            if imgui.menu_item(S.CONTEXT_RENAME, "", False)[0]:
                self._popup_target_line = line
                self._popup_name = line.name
                self._open_rename_popup = True
            imgui.separator()
            if imgui.menu_item(S.CONTEXT_DELETE, "", False)[0]:
                self._on_remove_line(line)
            imgui.end_popup()

    def _render_new_area_popup(self) -> None:
        if imgui.begin_popup_modal(
            S.POPUP_NEW_AREA, flags=imgui.WindowFlags_.always_auto_resize
        )[0]:
            imgui.text(S.POPUP_NAME)
            imgui.same_line(80)
            if imgui.is_window_appearing():
                imgui.set_keyboard_focus_here()
            imgui.set_next_item_width(150)
            _, self._popup_name = imgui.input_text("##area_name", self._popup_name)

            imgui.text(S.POPUP_NUMBER)
            imgui.same_line(80)
            imgui.set_next_item_width(150)
            _, self._popup_area_number = imgui.input_int(
                "##area_num", self._popup_area_number
            )

            imgui.separator()
            if imgui.button(S.BTN_ADD, imgui.ImVec2(75, 0)):
                self._on_create_area(self._popup_area_number, self._popup_name)
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

    def _render_new_line_popup(self) -> None:
        if imgui.begin_popup_modal(
            S.POPUP_NEW_LINE, flags=imgui.WindowFlags_.always_auto_resize
        )[0]:
            imgui.text(S.POPUP_NAME)
            imgui.same_line(80)
            if imgui.is_window_appearing():
                imgui.set_keyboard_focus_here()
            imgui.set_next_item_width(150)
            _, self._popup_name = imgui.input_text("##line_name", self._popup_name)

            imgui.text(S.POPUP_NUMBER)
            imgui.same_line(80)
            imgui.set_next_item_width(150)
            _, self._popup_line_number = imgui.input_int(
                "##line_num", self._popup_line_number
            )

            imgui.separator()
            if imgui.button(S.BTN_ADD, imgui.ImVec2(75, 0)):
                if self._popup_target_area:
                    self._on_create_line(
                        self._popup_target_area.id,
                        self._popup_line_number,
                        self._popup_name,
                    )
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

    def _render_rename_popup(self) -> None:
        if imgui.begin_popup_modal(
            S.POPUP_RENAME, flags=imgui.WindowFlags_.always_auto_resize
        )[0]:
            imgui.text(S.POPUP_NAME)
            imgui.same_line(80)
            if imgui.is_window_appearing():
                imgui.set_keyboard_focus_here()
            imgui.set_next_item_width(150)
            _, self._popup_name = imgui.input_text("##rename_name", self._popup_name)

            imgui.separator()
            if imgui.button(S.BTN_ADD, imgui.ImVec2(75, 0)):
                if self._popup_target_area:
                    self._on_rename_area(self._popup_target_area, self._popup_name)
                    self._popup_target_area = None
                elif self._popup_target_line:
                    self._on_rename_line(self._popup_target_line, self._popup_name)
                    self._popup_target_line = None
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                self._popup_target_area = None
                self._popup_target_line = None
                imgui.close_current_popup()
            imgui.end_popup()

    def _next_area_number(self, areas: list[Area]) -> int:
        if not areas:
            return 1
        return max(a.number for a in areas) + 1

    def _next_line_number(self, lines: list[Line]) -> int:
        if not lines:
            return 1
        return max(ln.number for ln in lines) + 1

    def _build_device_tree(
        self, devices: list[Device]
    ) -> dict[int, dict[int, list[Device]]]:
        tree: dict[int, dict[int, list[Device]]] = {}
        for device in devices:
            if not device.individual_address:
                continue
            parts = device.individual_address.split(".")
            if len(parts) < 3:
                continue
            try:
                area, line = int(parts[0]), int(parts[1])
            except ValueError:
                continue
            if area not in tree:
                tree[area] = {}
            if line not in tree[area]:
                tree[area][line] = []
            tree[area][line].append(device)
        return tree

    def _get_unassigned_devices(
        self, devices: list[Device], areas: list[Area]
    ) -> list[Device]:
        area_numbers = {a.number for a in areas}
        area_lines: dict[int, set[int]] = {}
        for area in areas:
            lines = self._get_lines(area.id)
            area_lines[area.number] = {ln.number for ln in lines}

        unassigned = []
        for device in devices:
            if not device.individual_address:
                unassigned.append(device)
                continue
            parts = device.individual_address.split(".")
            if len(parts) < 3:
                unassigned.append(device)
                continue
            try:
                area, line = int(parts[0]), int(parts[1])
            except ValueError:
                unassigned.append(device)
                continue
            if area not in area_numbers or line not in area_lines.get(area, set()):
                unassigned.append(device)
        return unassigned

    def _render_device_drag_source(self, device: Device) -> None:
        if imgui.begin_drag_drop_source():
            self._dragging_device = device
            imgui.set_drag_drop_payload_py_id("DEVICE", device.node_id)
            imgui.text(device.name)
            imgui.end_drag_drop_source()

    def _render_line_drop_target(self, area: Area, line: Line) -> None:
        if imgui.begin_drag_drop_target():
            payload = imgui.accept_drag_drop_payload_py_id("DEVICE")
            if payload is not None and self._dragging_device is not None:
                self._on_move_device(self._dragging_device, area.number, line.number)
                self._dragging_device = None
            imgui.end_drag_drop_target()
