from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui
from imgui_bundle import imgui_node_editor as ed

from knx_gui.dpt import DPT, DPTMatch, dpt_color, dpt_match
from knx_gui.strings import S
from knx_gui.types import (
    FLAG_LABELS,
    ComObject,
    ComObjectFlags,
    Device,
    PinDir,
    color_u32,
    com_object_has_input,
    com_object_has_output,
    default_flags_for,
    flag_diff_letters,
)
from knx_gui.widgets import (
    ComFlagsTable,
    EnumPopup,
    render_parameters_grouped,
)

NODE_PADDING = 8.0
HEADER_INSET = 1.0
HEADER_BOTTOM_PADDING = 4.0
PIN_RADIUS = 5.0
PIN_HEIGHT = PIN_RADIUS * 2 + 4
MIN_PIN_SPACING = 20.0
SETTINGS_LABEL_OFFSET = 120.0
HEADER_COLOR = (0.2, 0.4, 0.7)
GA_NODE_COLOR = (0.3, 0.5, 0.3)
GA_NODE_ID_OFFSET = 1000000
GA_PIN_ID_OFFSET = 2000000
LINK_COLOR = imgui.ImVec4(0.6, 0.6, 0.6, 1.0)
LINK_LOOSE_COLOR = imgui.ImVec4(0.9, 0.7, 0.2, 1.0)
LINK_INVALID_COLOR = imgui.ImVec4(0.9, 0.2, 0.2, 1.0)


@dataclass
class NodeLayout:
    node_width: float
    in_total_w: float
    out_total_w: float
    mid_spacing: float
    in_dpt_w: float
    in_name_w: float
    out_dpt_w: float
    out_name_w: float


@dataclass
class Rect:
    min_x: float
    min_y: float
    max_x: float
    max_y: float


class NodeEditorPanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        get_group_addresses: Callable[[], list],
        get_assignments_for_ga: Callable[[int], list],
        add_link: Callable[[int, int], int | None],
        remove_link: Callable[[int], None],
        on_param_change: Callable[[Device, str, str], None],
        set_flag: Callable[[Device, str, str, bool], None],
        get_show_ga_nodes: Callable[[], bool],
    ) -> None:
        self._get_devices = get_devices
        self._get_group_addresses = get_group_addresses
        self._get_assignments_for_ga = get_assignments_for_ga
        self._add_link = add_link
        self._remove_link = remove_link
        self._on_param_change = on_param_change
        self._get_show_ga_nodes = get_show_ga_nodes

        self._editor_context: ed.EditorContext | None = None
        self._next_pin_id: int = 100000
        self._pin_ids: dict[tuple[int, int, str], int] = {}
        self._pin_to_co_db_id: dict[int, int] = {}
        self._co_db_id_to_pins: dict[int, dict[str, int]] = {}
        self._pin_dpt: dict[int, DPT] = {}
        self._pin_dir: dict[int, PinDir] = {}
        self._drag_source_pin: int | None = None

        self._dpt_popup_target: ComObject | None = None
        self._dpt_popup_request: ComObject | None = None
        self._enum_popup = EnumPopup("##NodeEnumPopup", on_param_change)
        self._com_flags_table = ComFlagsTable(set_flag)
        self._ga_pins: dict[int, tuple[int, int]] = {}
        self._ga_nodes_positioned: set[int] = set()
        self._ga_position_offsets: dict[tuple[int, ...], int] = {}

    def setup(self) -> None:
        config = ed.Config()
        config.navigate_button_index = 2
        config.enable_smooth_zoom = True
        config.force_window_content_width_to_node_width = True
        self._editor_context = ed.create_editor(config)

    def shutdown(self) -> None:
        if self._editor_context:
            ed.destroy_editor(self._editor_context)
            self._editor_context = None

    @property
    def editor_context(self) -> ed.EditorContext | None:
        return self._editor_context

    def render(self) -> None:
        if not self._editor_context:
            return

        ed.set_current_editor(self._editor_context)
        ed.begin("##NodeEditorCanvas", imgui.ImVec2(0, 0))

        for device in self._get_devices():
            self._render_device_node(device)

        if self._get_show_ga_nodes():
            self._ga_pins.clear()
            for ga in self._get_group_addresses():
                self._render_ga_node(ga)
        else:
            self._ga_nodes_positioned.clear()
            self._ga_position_offsets.clear()

        self._render_links()
        self._handle_link_creation()
        self._handle_link_deletion()

        ed.end()

        self._render_dpt_popup()
        self._render_enum_popup()

    def select_node(self, node_id: int, clear_selection: bool = False) -> None:
        if self._editor_context:
            ed.set_current_editor(self._editor_context)
            ed.select_node(ed.NodeId(node_id), clear_selection)

    def navigate_to_selection(
        self, zoom_in: bool = False, duration: float = 0.3
    ) -> None:
        if self._editor_context:
            ed.navigate_to_selection(zoom_in, duration)

    def get_selected_node_ids(self) -> list[int]:
        if not self._editor_context:
            return []
        ed.set_current_editor(self._editor_context)
        selected = ed.get_selected_nodes()
        return [n.id() for n in selected]

    def find_links_for_com_objects(
        self, device: Device, cos: list[ComObject]
    ) -> list[tuple[int, int, int]]:
        co_to_idx = {id(co): idx for idx, co in enumerate(device.com_objects)}
        pin_ids: set[int] = set()
        for co in cos:
            idx = co_to_idx.get(id(co))
            if idx is not None:
                for direction in ("in", "out"):
                    key = (device.node_id, idx, direction)
                    if key in self._pin_ids:
                        pin_ids.add(self._pin_ids[key])
        affected: list[tuple[int, int, int]] = []
        for link in self._compute_visual_links():
            _link_id, start, end = link
            if start in pin_ids or end in pin_ids:
                affected.append(link)
        return affected

    def _get_pin_id(
        self, device_id: int, co_index: int, direction: str, co_db_id: int | None = None
    ) -> int:
        key = (device_id, co_index, direction)
        if key not in self._pin_ids:
            self._pin_ids[key] = self._next_pin_id
            self._next_pin_id += 1
        pin_id = self._pin_ids[key]
        if co_db_id is not None:
            self._pin_to_co_db_id[pin_id] = co_db_id
            if co_db_id not in self._co_db_id_to_pins:
                self._co_db_id_to_pins[co_db_id] = {}
            self._co_db_id_to_pins[co_db_id][direction] = pin_id
        return pin_id

    def _calc_pin_highlight(
        self, pin: ComObject, direction: PinDir
    ) -> tuple[float, bool]:
        if self._drag_source_pin is None:
            return 1.0, False
        src_dpt = self._pin_dpt.get(self._drag_source_pin)
        src_dir = self._pin_dir.get(self._drag_source_pin)
        if src_dpt is None or src_dir is None:
            return 1.0, False
        if src_dir == direction:
            return 0.2, False
        match = dpt_match(src_dpt, pin.dpt)
        if match == DPTMatch.EXACT:
            return 1.0, True
        if match == DPTMatch.LOOSE:
            return 0.7, False
        return 0.2, False

    def _draw_pin_icon(self, dpt: DPT, alpha: float = 1.0, glow: bool = False) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(cursor.x + PIN_RADIUS, cursor.y + PIN_RADIUS + 2)
        base_color = dpt_color(dpt)
        color = color_u32(base_color.x, base_color.y, base_color.z, alpha)
        if glow:
            draw_list.add_circle_filled(
                center,
                PIN_RADIUS + 4,
                color_u32(base_color.x, base_color.y, base_color.z, 0.3),
            )
            draw_list.add_circle_filled(
                center,
                PIN_RADIUS + 2,
                color_u32(base_color.x, base_color.y, base_color.z, 0.5),
            )
        draw_list.add_circle_filled(center, PIN_RADIUS, color)
        draw_list.add_circle(
            center, PIN_RADIUS, color_u32(1, 1, 1, 0.3 * alpha), 0, 1.5
        )
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_HEIGHT))

    def _draw_flag_badges(self, flags: ComObjectFlags, direction: PinDir) -> None:
        diffs = flag_diff_letters(flags, direction)
        if not diffs:
            return
        for letter, is_set in diffs:
            color = (
                imgui.ImVec4(0.4, 0.7, 0.3, 1.0)
                if is_set
                else imgui.ImVec4(0.7, 0.3, 0.3, 1.0)
            )
            imgui.push_style_color(imgui.Col_.text, color)
            imgui.text(letter if is_set else f"!{letter}")
            imgui.pop_style_color()
            if imgui.is_item_hovered():
                self._show_flags_tooltip(flags, direction)
            imgui.same_line()

    def _show_flags_tooltip(self, flags: ComObjectFlags, direction: PinDir) -> None:
        ed.suspend()
        imgui.begin_tooltip()
        imgui.text(S.NODE_DEFAULT_FOR.format(direction=direction.value))
        default = default_flags_for(direction)
        for attr, letter, name in FLAG_LABELS:
            current = getattr(flags, attr)
            default_val = getattr(default, attr)
            symbol = "+" if current else "-"
            label = f"{symbol} {letter}  {name}"
            if current != default_val:
                color = (
                    imgui.ImVec4(0.4, 0.7, 0.3, 1.0)
                    if current
                    else imgui.ImVec4(0.7, 0.3, 0.3, 1.0)
                )
                imgui.push_style_color(imgui.Col_.text, color)
                imgui.text(label + "  " + S.NODE_MODIFIED)
                imgui.pop_style_color()
            else:
                imgui.text_disabled(label)
        imgui.end_tooltip()
        ed.resume()

    def _calc_node_layout(self, device: Device) -> NodeLayout:
        in_dpt_w = in_name_w = out_dpt_w = out_name_w = 0.0
        for row in device.rows:
            if row.left and com_object_has_input(row.left):
                in_dpt_w = max(
                    in_dpt_w, imgui.calc_text_size(f"[{row.left.dpt.label}]").x
                )
                in_name_w = max(in_name_w, imgui.calc_text_size(row.left.name).x)
            if row.right and com_object_has_output(row.right):
                out_dpt_w = max(
                    out_dpt_w, imgui.calc_text_size(f"[{row.right.dpt.label}]").x
                )
                out_name_w = max(out_name_w, imgui.calc_text_size(row.right.name).x)

        spacing = imgui.get_style().item_spacing.x
        in_total_w = (
            PIN_RADIUS * 2 + in_name_w + in_dpt_w + spacing * 4 if in_name_w > 0 else 0
        )
        out_total_w = (
            PIN_RADIUS * 2 + out_name_w + out_dpt_w + spacing * 4
            if out_name_w > 0
            else 0
        )

        tree_indent = imgui.get_style().indent_spacing
        max_value_w = max(
            imgui.calc_text_size(device.app.manufacturer_id).x,
            imgui.calc_text_size(device.app.application_id).x,
        )
        manufacturer_width = tree_indent + SETTINGS_LABEL_OFFSET + max_value_w

        max_pin_name_w = imgui.calc_text_size("Object").x
        for co in device.com_objects:
            max_pin_name_w = max(max_pin_name_w, imgui.calc_text_size(co.name).x)
        item_spacing = imgui.get_style().item_spacing.x
        checkbox_w = imgui.get_frame_height()
        com_objects_width = (
            tree_indent
            + max_pin_name_w
            + 8
            + len(FLAG_LABELS) * (checkbox_w + item_spacing)
        )

        settings_width = max(manufacturer_width, com_objects_width)
        pin_row_width = in_total_w + MIN_PIN_SPACING + out_total_w
        node_width = max(pin_row_width, settings_width)
        mid_spacing = node_width - in_total_w - out_total_w

        return NodeLayout(
            node_width=node_width,
            in_total_w=in_total_w,
            out_total_w=out_total_w,
            mid_spacing=mid_spacing,
            in_dpt_w=in_dpt_w,
            in_name_w=in_name_w,
            out_dpt_w=out_dpt_w,
            out_name_w=out_name_w,
        )

    def _render_dpt_label(self, pin: ComObject, pin_id: int) -> None:
        label = f"[{pin.dpt.label}]"
        if len(pin.supported_dpts) > 1:
            text_size = imgui.calc_text_size(label)
            imgui.push_style_color(
                imgui.Col_.text, imgui.get_style().color_(imgui.Col_.text_disabled)
            )
            clicked = imgui.selectable(
                f"{label}##dpt_{pin_id}",
                False,
                imgui.SelectableFlags_.no_auto_close_popups,
                imgui.ImVec2(text_size.x, 0),
            )[0]
            imgui.pop_style_color()
            if clicked:
                self._dpt_popup_request = pin
        else:
            imgui.text_disabled(label)

    def _render_dpt_popup(self) -> None:
        if self._dpt_popup_request is not None:
            self._dpt_popup_target = self._dpt_popup_request
            self._dpt_popup_request = None
            imgui.open_popup("##DptPopup")
        if imgui.begin_popup("##DptPopup"):
            target = self._dpt_popup_target
            if target is not None:
                imgui.text_disabled(S.NODE_SELECT_DPT)
                imgui.separator()
                for dpt in target.supported_dpts:
                    selected = (
                        dpt.major == target.dpt.major and dpt.minor == target.dpt.minor
                    )
                    if imgui.menu_item(f"{dpt.code}  {dpt.name}", "", selected)[0]:
                        target.dpt = dpt
            imgui.end_popup()
        else:
            self._dpt_popup_target = None

    def _render_input_pin(
        self, pin_id: int, pin: ComObject, layout: NodeLayout
    ) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        self._pin_dir[pin_id] = PinDir.INPUT
        alpha, glow = self._calc_pin_highlight(pin, PinDir.INPUT)
        if not pin.flags.communication:
            alpha *= 0.4
            glow = False
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.input)
        ed.pin_pivot_alignment(imgui.ImVec2(0.0, 0.5))
        self._draw_pin_icon(pin.dpt, alpha, glow)
        imgui.same_line()
        if pin.flags.communication:
            imgui.text_unformatted(pin.name)
        else:
            imgui.text_disabled(pin.name)
        imgui.same_line()
        imgui.dummy(
            imgui.ImVec2(layout.in_name_w - imgui.calc_text_size(pin.name).x, 1)
        )
        ed.end_pin()
        imgui.same_line()
        self._render_dpt_label(pin, pin_id)
        imgui.same_line()
        dpt_label = f"[{pin.dpt.label}]"
        imgui.dummy(
            imgui.ImVec2(layout.in_dpt_w - imgui.calc_text_size(dpt_label).x, 1)
        )

    def _render_output_pin(
        self, pin_id: int, pin: ComObject, layout: NodeLayout
    ) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        self._pin_dir[pin_id] = PinDir.OUTPUT
        alpha, glow = self._calc_pin_highlight(pin, PinDir.OUTPUT)
        if not pin.flags.communication:
            alpha *= 0.4
            glow = False
        dpt_label = f"[{pin.dpt.label}]"
        self._render_dpt_label(pin, pin_id)
        imgui.same_line()
        imgui.dummy(
            imgui.ImVec2(layout.out_dpt_w - imgui.calc_text_size(dpt_label).x, 1)
        )
        imgui.same_line()
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.output)
        ed.pin_pivot_alignment(imgui.ImVec2(1.0, 0.5))
        if pin.flags.communication:
            imgui.text_unformatted(pin.name)
        else:
            imgui.text_disabled(pin.name)
        imgui.same_line()
        imgui.dummy(
            imgui.ImVec2(layout.out_name_w - imgui.calc_text_size(pin.name).x, 1)
        )
        imgui.same_line()
        self._draw_pin_icon(pin.dpt, alpha, glow)
        ed.end_pin()

    def _render_node_header(self, device: Device, width: float) -> Rect:
        cursor_x = imgui.get_cursor_pos_x()
        imgui.begin_group()
        imgui.text(device.name)
        if device.individual_address:
            imgui.same_line()
            address_width = imgui.calc_text_size(device.individual_address).x
            imgui.set_cursor_pos_x(cursor_x + width - address_width)
            imgui.text_disabled(device.individual_address)
        imgui.end_group()
        rect_min = imgui.get_item_rect_min()
        rect_max = imgui.get_item_rect_max()
        return Rect(rect_min.x, rect_min.y, rect_max.x, rect_max.y)

    def _render_node_pins(self, device: Device, layout: NodeLayout) -> None:
        co_indices = {id(co): idx for idx, co in enumerate(device.com_objects)}
        for row in device.rows:
            if row.left and com_object_has_input(row.left):
                pin_id = self._get_pin_id(
                    device.node_id, co_indices[id(row.left)], "in", row.left.db_id
                )
                self._render_input_pin(pin_id, row.left, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.in_total_w, PIN_HEIGHT))
            imgui.same_line(spacing=layout.mid_spacing)
            if row.right and com_object_has_output(row.right):
                pin_id = self._get_pin_id(
                    device.node_id, co_indices[id(row.right)], "out", row.right.db_id
                )
                self._render_output_pin(pin_id, row.right, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.out_total_w, PIN_HEIGHT))

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(SETTINGS_LABEL_OFFSET)
        imgui.text(value)

    def _render_node_settings(self, device: Device, width: float) -> None:
        if imgui.tree_node(f"{S.CONFIGURE_MANUFACTURER}##{device.node_id}"):
            self._render_label_value(
                S.CONFIGURE_MANUFACTURER, device.app.manufacturer_id
            )
            self._render_label_value(S.CONFIGURE_APPLICATION, device.app.application_id)
            imgui.tree_pop()
        params = device.get_visible_parameters()
        if params:
            is_open = imgui.tree_node(f"{S.NODE_PARAMETERS}##{device.node_id}")
            imgui.same_line()
            imgui.text_disabled(f"({len(params)})")
            if is_open:
                req = render_parameters_grouped(
                    device, params, self._on_param_change, deferred_enum=True
                )
                if req is not None:
                    self._enum_popup.request(device, req.param)
                imgui.tree_pop()
        if imgui.tree_node(f"{S.NODE_COM_FLAGS}##{device.node_id}"):
            self._com_flags_table.render(device, device.get_visible_com_objects())
            imgui.tree_pop()

    def _render_enum_popup(self) -> None:
        self._enum_popup.render()

    def _draw_node_header_bg(
        self, node_id: int, header: Rect, content_max_x: float
    ) -> None:
        draw_list = ed.get_node_background_draw_list(ed.NodeId(node_id))
        if not draw_list:
            return
        left = header.min_x - NODE_PADDING + HEADER_INSET
        right = content_max_x + NODE_PADDING - HEADER_INSET
        top = header.min_y - NODE_PADDING + HEADER_INSET
        bottom = header.max_y + HEADER_BOTTOM_PADDING
        rounding = ed.get_style().node_rounding - HEADER_INSET
        draw_list.add_rect_filled(
            imgui.ImVec2(left, top),
            imgui.ImVec2(right, bottom),
            color_u32(*HEADER_COLOR),
            rounding,
            imgui.ImDrawFlags_.round_corners_top,
        )

    def _render_device_node(self, device: Device) -> None:
        ed.begin_node(ed.NodeId(device.node_id))

        layout = self._calc_node_layout(device)
        header = self._render_node_header(device, layout.node_width)
        imgui.spacing()

        self._render_node_pins(device, layout)

        imgui.dummy(imgui.ImVec2(layout.node_width, 1))
        content_max_x = imgui.get_item_rect_max().x

        imgui.spacing()
        self._render_node_settings(device, layout.node_width)

        ed.end_node()
        self._draw_node_header_bg(device.node_id, header, content_max_x)

    def _pins_match_quality(self, pin_a: int, pin_b: int) -> DPTMatch:
        dpt_a = self._pin_dpt.get(pin_a)
        dpt_b = self._pin_dpt.get(pin_b)
        dir_a = self._pin_dir.get(pin_a)
        dir_b = self._pin_dir.get(pin_b)
        if dpt_a is None or dpt_b is None or dir_a is None or dir_b is None:
            return DPTMatch.NONE
        if dir_a == dir_b:
            return DPTMatch.NONE
        return dpt_match(dpt_a, dpt_b)

    def _are_pins_compatible(self, pin_a: int, pin_b: int) -> bool:
        return self._pins_match_quality(pin_a, pin_b) != DPTMatch.NONE

    def _link_exists(self, pin_a: int, pin_b: int) -> bool:
        for _, start, end in self._compute_visual_links():
            if (start == pin_a and end == pin_b) or (start == pin_b and end == pin_a):
                return True
        return False

    def _show_link_tooltip(self, pin_a: int, pin_b: int) -> None:
        dpt_a = self._pin_dpt.get(pin_a)
        dpt_b = self._pin_dpt.get(pin_b)
        dir_a = self._pin_dir.get(pin_a)
        dir_b = self._pin_dir.get(pin_b)
        if dpt_a is None or dpt_b is None or dir_a is None or dir_b is None:
            return

        ed.suspend()
        imgui.begin_tooltip()
        if dir_a == dir_b:
            imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
            msg = (
                S.LINK_CANNOT_CONNECT_OUTPUTS
                if dir_a == PinDir.OUTPUT
                else S.LINK_CANNOT_CONNECT_INPUTS
            )
            imgui.text(msg)
            imgui.pop_style_color()
        else:
            match = dpt_match(dpt_a, dpt_b)
            if match == DPTMatch.EXACT:
                imgui.text(S.LINK_DPT_INFO.format(code=dpt_a.code, name=dpt_a.name))
            elif match == DPTMatch.LOOSE:
                imgui.push_style_color(imgui.Col_.text, LINK_LOOSE_COLOR)
                imgui.text(S.LINK_WARNING_LOOSE_MATCH)
                imgui.pop_style_color()
                imgui.text(S.LINK_FROM_DPT.format(code=dpt_a.code, name=dpt_a.name))
                imgui.text(S.LINK_TO_DPT.format(code=dpt_b.code, name=dpt_b.name))
            else:
                imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
                imgui.text(S.LINK_INCOMPATIBLE_DPTS)
                imgui.pop_style_color()
                imgui.text(S.LINK_FROM_DPT.format(code=dpt_a.code, name=dpt_a.name))
                imgui.text(S.LINK_TO_DPT.format(code=dpt_b.code, name=dpt_b.name))
        imgui.end_tooltip()
        ed.resume()

    def _handle_link_creation(self) -> None:
        new_drag_source: int | None = self._drag_source_pin
        if ed.begin_create():
            start_pin_id = ed.PinId()
            end_pin_id = ed.PinId()
            if ed.query_new_link(start_pin_id, end_pin_id):
                if start_pin_id.id() != 0:
                    new_drag_source = start_pin_id.id()
                if start_pin_id.id() != 0 and end_pin_id.id() != 0:
                    match = self._pins_match_quality(start_pin_id.id(), end_pin_id.id())
                    duplicate = self._link_exists(start_pin_id.id(), end_pin_id.id())
                    self._show_link_tooltip(start_pin_id.id(), end_pin_id.id())
                    if match == DPTMatch.NONE or duplicate:
                        ed.reject_new_item(LINK_INVALID_COLOR, 3.0)
                    else:
                        preview_color = (
                            LINK_COLOR if match == DPTMatch.EXACT else LINK_LOOSE_COLOR
                        )
                        if ed.accept_new_item(preview_color, 2.0):
                            start_co_id = self._pin_to_co_db_id.get(start_pin_id.id())
                            end_co_id = self._pin_to_co_db_id.get(end_pin_id.id())
                            start_dir = self._pin_dir.get(start_pin_id.id())
                            if start_co_id is not None and end_co_id is not None:
                                start_is_output = start_dir == PinDir.OUTPUT
                                if start_is_output:
                                    self._add_link(start_co_id, end_co_id)
                                else:
                                    self._add_link(end_co_id, start_co_id)
            else:
                drag_pin_id = ed.PinId()
                if ed.query_new_node(drag_pin_id):
                    if drag_pin_id.id() != 0:
                        new_drag_source = drag_pin_id.id()
                    ed.reject_new_item()
            ed.end_create()
        if not imgui.is_mouse_down(0):
            new_drag_source = None
        self._drag_source_pin = new_drag_source

    def _handle_link_deletion(self) -> None:
        if ed.begin_delete():
            link_id = ed.LinkId()
            while ed.query_deleted_link(link_id):
                if ed.accept_deleted_item():
                    self._remove_link(link_id.id())
            ed.end_delete()

    def _calc_ga_node_position(self, ga) -> imgui.ImVec2 | None:
        assignments = self._get_assignments_for_ga(ga.id)
        if not assignments:
            return None

        device_node_ids: set[int] = set()
        for assignment in assignments:
            pins = self._co_db_id_to_pins.get(assignment.com_object_id)
            if pins:
                for _direction, pin_id in pins.items():
                    key = next(
                        (k for k, v in self._pin_ids.items() if v == pin_id), None
                    )
                    if key:
                        device_node_ids.add(key[0])

        if not device_node_ids:
            return None

        total_x, total_y = 0.0, 0.0
        count = 0
        for device_node_id in device_node_ids:
            pos = ed.get_node_position(ed.NodeId(device_node_id))
            size = ed.get_node_size(ed.NodeId(device_node_id))
            total_x += pos.x + size.x / 2
            total_y += pos.y + size.y / 2
            count += 1

        if count == 0:
            return None

        device_key = tuple(sorted(device_node_ids))
        offset_idx = self._ga_position_offsets.get(device_key, 0)
        self._ga_position_offsets[device_key] = offset_idx + 1

        y_offset = offset_idx * 50.0

        return imgui.ImVec2(total_x / count, total_y / count + y_offset)

    def _render_ga_node(self, ga) -> None:
        node_id = GA_NODE_ID_OFFSET + ga.id
        in_pin_id = GA_PIN_ID_OFFSET + ga.id * 2
        out_pin_id = GA_PIN_ID_OFFSET + ga.id * 2 + 1
        self._ga_pins[ga.id] = (in_pin_id, out_pin_id)

        if ga.id not in self._ga_nodes_positioned:
            pos = self._calc_ga_node_position(ga)
            if pos:
                ed.set_node_position(ed.NodeId(node_id), pos)
                self._ga_nodes_positioned.add(ga.id)

        ed.begin_node(ed.NodeId(node_id))
        ed.push_style_color(ed.StyleColor.node_bg, imgui.ImVec4(*GA_NODE_COLOR, 1.0))

        imgui.text(ga.address)
        if ga.name:
            imgui.same_line()
            imgui.text_disabled(ga.name)
        imgui.spacing()

        ed.begin_pin(ed.PinId(in_pin_id), ed.PinKind.input)
        ed.pin_pivot_alignment(imgui.ImVec2(0.0, 0.5))
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(cursor.x + PIN_RADIUS, cursor.y + PIN_RADIUS + 2)
        draw_list.add_circle_filled(center, PIN_RADIUS, color_u32(0.8, 0.8, 0.8, 1.0))
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_HEIGHT))
        ed.end_pin()

        imgui.same_line(spacing=20)

        ed.begin_pin(ed.PinId(out_pin_id), ed.PinKind.output)
        ed.pin_pivot_alignment(imgui.ImVec2(1.0, 0.5))
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(cursor.x + PIN_RADIUS, cursor.y + PIN_RADIUS + 2)
        draw_list.add_circle_filled(center, PIN_RADIUS, color_u32(0.8, 0.8, 0.8, 1.0))
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_HEIGHT))
        ed.end_pin()

        ed.pop_style_color()
        ed.end_node()

    def _compute_visual_links(self) -> list[tuple[int, int, int]]:
        links: list[tuple[int, int, int]] = []
        show_ga_nodes = self._get_show_ga_nodes()

        for ga in self._get_group_addresses():
            assignments = self._get_assignments_for_ga(ga.id)
            if not assignments:
                continue

            sending_pins = []
            receiving_pins = []
            for assignment in assignments:
                pins = self._co_db_id_to_pins.get(assignment.com_object_id)
                if pins is None:
                    continue
                if assignment.is_sending:
                    pin_id = pins.get("out")
                    if pin_id is not None:
                        sending_pins.append(pin_id)
                else:
                    pin_id = pins.get("in")
                    if pin_id is not None:
                        receiving_pins.append(pin_id)

            if show_ga_nodes and ga.id in self._ga_pins:
                ga_in_pin, ga_out_pin = self._ga_pins[ga.id]
                link_id_base = ga.id * 10000
                for idx, send_pin in enumerate(sending_pins):
                    links.append((link_id_base + idx, send_pin, ga_in_pin))
                for idx, recv_pin in enumerate(receiving_pins):
                    links.append((link_id_base + 5000 + idx, ga_out_pin, recv_pin))
            else:
                if len(assignments) < 2:
                    continue
                for send_pin in sending_pins:
                    for recv_pin in receiving_pins:
                        links.append((ga.id, send_pin, recv_pin))
        return links

    def _render_links(self) -> None:
        for ga_id, start_pin, end_pin in self._compute_visual_links():
            match = self._pins_match_quality(start_pin, end_pin)
            color = LINK_LOOSE_COLOR if match == DPTMatch.LOOSE else LINK_COLOR
            ed.link(ed.LinkId(ga_id), ed.PinId(start_pin), ed.PinId(end_pin), color)
