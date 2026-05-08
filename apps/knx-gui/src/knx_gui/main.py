import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from imgui_bundle import imgui, hello_imgui, imgui_node_editor as ed

NODE_PADDING = 8.0
HEADER_INSET = 1.0
HEADER_BOTTOM_PADDING = 4.0
PIN_RADIUS = 5.0
PIN_HEIGHT = PIN_RADIUS * 2 + 4
MIN_PIN_SPACING = 20.0
SETTINGS_LABEL_OFFSET = 120.0
SETTINGS_CLIP_HEIGHT = 500.0
HEADER_COLOR = (0.2, 0.4, 0.7)
LINK_COLOR = imgui.ImVec4(0.6, 0.6, 0.6, 1.0)
LINK_INVALID_COLOR = imgui.ImVec4(0.9, 0.2, 0.2, 1.0)

TELEGRAM_PANE_HEIGHT = 200
TELEGRAM_HEADER_BUTTONS_WIDTH = 100
NAVIGATE_TO_NODE_DURATION = 0.3


class DPT(Enum):
    BOOL = "1"
    DIMMING = "3"
    PERCENT = "5"
    FLOAT = "9"
    SCENE = "17"
    RGB = "232"


DPT_COLORS: dict[DPT, imgui.ImVec4] = {
    DPT.BOOL: imgui.ImVec4(0.9, 0.3, 0.3, 1.0),
    DPT.DIMMING: imgui.ImVec4(0.9, 0.6, 0.2, 1.0),
    DPT.PERCENT: imgui.ImVec4(0.2, 0.8, 0.4, 1.0),
    DPT.FLOAT: imgui.ImVec4(0.2, 0.6, 0.9, 1.0),
    DPT.SCENE: imgui.ImVec4(0.7, 0.3, 0.9, 1.0),
    DPT.RGB: imgui.ImVec4(0.9, 0.2, 0.6, 1.0),
}

DPT_LABELS: dict[DPT, str] = {
    DPT.BOOL: "bool",
    DPT.DIMMING: "dim",
    DPT.PERCENT: "%",
    DPT.FLOAT: "°C",
    DPT.SCENE: "scene",
    DPT.RGB: "rgb",
}


class PinDir(Enum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass
class Pin:
    name: str
    dpt: DPT


@dataclass
class PinRow:
    input_pin: Pin | None = None
    output_pin: Pin | None = None


@dataclass
class DeviceConfig:
    manufacturer: str
    application: str
    hardware: str
    firmware: str


@dataclass
class DeviceTemplate:
    name: str
    rows: list[PinRow]
    config: DeviceConfig


DEVICE_TEMPLATES: dict[str, DeviceTemplate] = {
    "switch_actuator": DeviceTemplate(
        name="Switch Actuator",
        rows=[
            PinRow(Pin("Switch", DPT.BOOL), Pin("Status", DPT.BOOL)),
        ],
        config=DeviceConfig("ABB", "SA/S 4.16.2.2", "2CDG110252R0011", "1.2.3"),
    ),
    "dimmer_actuator": DeviceTemplate(
        name="Dimmer Actuator",
        rows=[
            PinRow(Pin("Switch", DPT.BOOL), Pin("Status", DPT.BOOL)),
            PinRow(Pin("Dimming", DPT.DIMMING)),
            PinRow(Pin("Brightness", DPT.PERCENT), Pin("Value", DPT.PERCENT)),
        ],
        config=DeviceConfig("ABB", "DA/S 4.230.2.1", "2CDG110198R0011", "2.1.0"),
    ),
    "temperature_sensor": DeviceTemplate(
        name="Temperature Sensor",
        rows=[
            PinRow(output_pin=Pin("Temperature", DPT.FLOAT)),
        ],
        config=DeviceConfig("Siemens", "QMX3.P37", "5WG1258-3AB13", "3.0.1"),
    ),
    "push_button": DeviceTemplate(
        name="Push Button",
        rows=[
            PinRow(output_pin=Pin("Press", DPT.BOOL)),
            PinRow(output_pin=Pin("Long Press", DPT.BOOL)),
            PinRow(output_pin=Pin("Scene", DPT.SCENE)),
        ],
        config=DeviceConfig("Gira", "Tastsensor 4 Plus", "2104..", "1.0.5"),
    ),
    "rgb_controller": DeviceTemplate(
        name="RGB Controller",
        rows=[
            PinRow(Pin("Switch", DPT.BOOL), Pin("Status", DPT.BOOL)),
            PinRow(Pin("Color", DPT.RGB), Pin("Color Status", DPT.RGB)),
            PinRow(Pin("Brightness", DPT.PERCENT)),
        ],
        config=DeviceConfig("MDT", "AKD-0424R2.02", "R2.02", "1.1.0"),
    ),
    "thermostat": DeviceTemplate(
        name="Thermostat",
        rows=[
            PinRow(Pin("Setpoint", DPT.FLOAT), Pin("Actual Temp", DPT.FLOAT)),
            PinRow(output_pin=Pin("Heating", DPT.BOOL)),
            PinRow(output_pin=Pin("Valve", DPT.PERCENT)),
        ],
        config=DeviceConfig("Theben", "RAMSES 718 P", "7189210", "2.3.1"),
    ),
}


def color_u32(r: float, g: float, b: float, a: float = 1.0) -> int:
    return imgui.get_color_u32(imgui.ImVec4(r, g, b, a))


def color_from_vec4(c: imgui.ImVec4) -> int:
    return imgui.get_color_u32(c)


@dataclass
class Device:
    node_id: int
    name: str
    template: DeviceTemplate
    address: str


@dataclass
class Telegram:
    timestamp: str
    source: str
    destination: str
    service: str
    dpt: str
    value: str


@dataclass
class TelegramColumn:
    name: str
    getter: Callable[[Telegram], str]
    stretch: bool = False
    disabled: bool = False


TELEGRAM_COLUMNS: list[TelegramColumn] = [
    TelegramColumn("Time", lambda t: t.timestamp),
    TelegramColumn("Source", lambda t: t.source),
    TelegramColumn("Destination", lambda t: t.destination),
    TelegramColumn("Service", lambda t: t.service),
    TelegramColumn("DPT", lambda t: t.dpt, disabled=True),
    TelegramColumn("Value", lambda t: t.value, stretch=True),
]


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


class KnxGuiApp:
    def __init__(self) -> None:
        self._editor_context: ed.EditorContext | None = None
        self._links: list[tuple[int, int, int]] = []
        self._next_link_id: int = 1000
        self._pin_dpt: dict[int, DPT] = {}
        self._pin_dir: dict[int, PinDir] = {}
        self._devices: list[Device] = []
        self._show_sidebar: bool = True
        self._connected: bool = False
        self._controller_ip: str = "192.168.1.1"
        self._show_telegrams: bool = False
        self._telegrams: list[Telegram] = []
        self._selected_telegrams: set[int] = set()
        self._last_selected_telegram: int = -1
        self._init_devices()
        self._init_sample_telegrams()

    def _init_devices(self) -> None:
        self._devices = [
            Device(1, "Living Room Light", DEVICE_TEMPLATES["switch_actuator"], "1.1.1"),
            Device(2, "Kitchen Dimmer", DEVICE_TEMPLATES["dimmer_actuator"], "1.1.2"),
            Device(3, "Bedroom Temp", DEVICE_TEMPLATES["temperature_sensor"], "1.1.3"),
            Device(4, "Entry Button", DEVICE_TEMPLATES["push_button"], "1.2.1"),
            Device(5, "Living Room Thermo", DEVICE_TEMPLATES["thermostat"], "1.2.2"),
            Device(6, "RGB Strip", DEVICE_TEMPLATES["rgb_controller"], "2.1.1"),
        ]

    def _init_sample_telegrams(self) -> None:
        self._telegrams = [
            Telegram("12:34:01.123", "1.1.1", "1/0/1", "GroupValueWrite", "1.001", "On"),
            Telegram("12:34:01.456", "1.1.1", "1/0/2", "GroupValueResponse", "1.001", "Off"),
            Telegram("12:34:02.001", "1.2.1", "2/0/1", "GroupValueWrite", "5.001", "75%"),
            Telegram("12:34:02.345", "1.1.3", "3/0/1", "GroupValueWrite", "9.001", "21.5°C"),
            Telegram("12:34:03.012", "1.2.2", "4/0/1", "GroupValueRead", "1.001", ""),
            Telegram("12:34:03.234", "1.2.2", "4/0/1", "GroupValueResponse", "1.001", "On"),
            Telegram("12:34:04.567", "2.1.1", "5/0/1", "GroupValueWrite", "232.600", "#FF8800"),
            Telegram("12:34:05.123", "1.1.2", "1/1/1", "GroupValueWrite", "3.007", "Up"),
        ]

    def setup(self) -> None:
        config = ed.Config()
        config.navigate_button_index = 2
        config.enable_smooth_zoom = True
        self._editor_context = ed.create_editor(config)

    def shutdown(self) -> None:
        if self._editor_context:
            ed.destroy_editor(self._editor_context)
            self._editor_context = None

    def _draw_pin_icon(self, dpt: DPT) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        center = imgui.ImVec2(cursor.x + PIN_RADIUS, cursor.y + PIN_RADIUS + 2)
        color = color_from_vec4(DPT_COLORS[dpt])
        draw_list.add_circle_filled(center, PIN_RADIUS, color)
        draw_list.add_circle(center, PIN_RADIUS, color_u32(1, 1, 1, 0.3), 0, 1.5)
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_HEIGHT))

    def _calc_node_layout(self, template: DeviceTemplate) -> NodeLayout:
        in_dpt_w = in_name_w = out_dpt_w = out_name_w = 0.0
        for row in template.rows:
            if row.input_pin:
                in_dpt_w = max(in_dpt_w, imgui.calc_text_size(f"[{DPT_LABELS[row.input_pin.dpt]}]").x)
                in_name_w = max(in_name_w, imgui.calc_text_size(row.input_pin.name).x)
            if row.output_pin:
                out_dpt_w = max(out_dpt_w, imgui.calc_text_size(f"[{DPT_LABELS[row.output_pin.dpt]}]").x)
                out_name_w = max(out_name_w, imgui.calc_text_size(row.output_pin.name).x)

        spacing = imgui.get_style().item_spacing.x
        in_total_w = PIN_RADIUS * 2 + in_name_w + in_dpt_w + spacing * 4 if in_name_w > 0 else 0
        out_total_w = PIN_RADIUS * 2 + out_name_w + out_dpt_w + spacing * 4 if out_name_w > 0 else 0

        tree_indent = imgui.get_style().indent_spacing
        max_value_w = max(
            imgui.calc_text_size(template.config.manufacturer).x,
            imgui.calc_text_size(template.config.application).x,
            imgui.calc_text_size(template.config.hardware).x,
            imgui.calc_text_size(template.config.firmware).x,
        )
        settings_width = tree_indent + SETTINGS_LABEL_OFFSET + max_value_w

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

    def _render_input_pin(self, pin_id: int, pin: Pin, layout: NodeLayout) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        self._pin_dir[pin_id] = PinDir.INPUT
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.input)
        ed.pin_pivot_alignment(imgui.ImVec2(0.0, 0.5))
        self._draw_pin_icon(pin.dpt)
        imgui.same_line()
        imgui.text_unformatted(pin.name)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.in_name_w - imgui.calc_text_size(pin.name).x, 1))
        imgui.same_line()
        dpt_label = f"[{DPT_LABELS[pin.dpt]}]"
        imgui.text_disabled(dpt_label)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.in_dpt_w - imgui.calc_text_size(dpt_label).x, 1))
        ed.end_pin()

    def _render_output_pin(self, pin_id: int, pin: Pin, layout: NodeLayout) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        self._pin_dir[pin_id] = PinDir.OUTPUT
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.output)
        ed.pin_pivot_alignment(imgui.ImVec2(1.0, 0.5))
        dpt_label = f"[{DPT_LABELS[pin.dpt]}]"
        imgui.text_disabled(dpt_label)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.out_dpt_w - imgui.calc_text_size(dpt_label).x, 1))
        imgui.same_line()
        imgui.text_unformatted(pin.name)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.out_name_w - imgui.calc_text_size(pin.name).x, 1))
        imgui.same_line()
        self._draw_pin_icon(pin.dpt)
        ed.end_pin()

    def _render_node_header(self, template: DeviceTemplate, address: str) -> Rect:
        imgui.begin_group()
        imgui.text(template.name)
        imgui.same_line()
        imgui.text_disabled(f"  {address}")
        imgui.end_group()
        rect_min = imgui.get_item_rect_min()
        rect_max = imgui.get_item_rect_max()
        return Rect(rect_min.x, rect_min.y, rect_max.x, rect_max.y)

    def _render_node_pins(self, node_id: int, template: DeviceTemplate, layout: NodeLayout) -> None:
        pin_base = node_id * 100
        for i, row in enumerate(template.rows):
            if row.input_pin:
                self._render_input_pin(pin_base + i, row.input_pin, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.in_total_w, PIN_HEIGHT))
            imgui.same_line(spacing=layout.mid_spacing)
            if row.output_pin:
                self._render_output_pin(pin_base + 50 + i, row.output_pin, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.out_total_w, PIN_HEIGHT))

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(SETTINGS_LABEL_OFFSET)
        imgui.text(value)

    def _render_node_settings(self, node_id: int, config: DeviceConfig, width: float) -> None:
        cursor = imgui.get_cursor_screen_pos()
        clip_max = imgui.ImVec2(cursor.x + width, cursor.y + SETTINGS_CLIP_HEIGHT)
        imgui.push_clip_rect(cursor, clip_max, True)
        if imgui.tree_node(f"Manufacturer##{node_id}"):
            self._render_label_value("Manufacturer", config.manufacturer)
            self._render_label_value("Application", config.application)
            self._render_label_value("Hardware", config.hardware)
            self._render_label_value("Firmware", config.firmware)
            imgui.tree_pop()
        imgui.pop_clip_rect()

    def _draw_node_header_bg(self, node_id: int, header: Rect, content_max_x: float) -> None:
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

    def _render_device_node(self, node_id: int, template: DeviceTemplate, address: str) -> None:
        ed.begin_node(ed.NodeId(node_id))

        header = self._render_node_header(template, address)
        imgui.spacing()

        layout = self._calc_node_layout(template)
        self._render_node_pins(node_id, template, layout)

        imgui.dummy(imgui.ImVec2(layout.node_width, 1))
        content_max_x = imgui.get_item_rect_max().x

        imgui.spacing()
        self._render_node_settings(node_id, template.config, layout.node_width)

        ed.end_node()
        self._draw_node_header_bg(node_id, header, content_max_x)

    def _are_pins_compatible(self, pin_a: int, pin_b: int) -> bool:
        dpt_a = self._pin_dpt.get(pin_a)
        dpt_b = self._pin_dpt.get(pin_b)
        dir_a = self._pin_dir.get(pin_a)
        dir_b = self._pin_dir.get(pin_b)
        if dpt_a is None or dpt_b is None or dir_a is None or dir_b is None:
            return False
        if dpt_a != dpt_b:
            return False
        return dir_a != dir_b

    def _remove_links_for_pin(self, pin_id: int) -> None:
        self._links = [
            link for link in self._links
            if link[1] != pin_id and link[2] != pin_id
        ]

    def _handle_link_creation(self) -> None:
        if ed.begin_create():
            start_pin_id = ed.PinId()
            end_pin_id = ed.PinId()
            if ed.query_new_link(start_pin_id, end_pin_id):
                if start_pin_id.id() != 0 and end_pin_id.id() != 0:
                    compatible = self._are_pins_compatible(
                        start_pin_id.id(), end_pin_id.id()
                    )
                    if compatible:
                        if ed.accept_new_item(LINK_COLOR, 2.0):
                            self._remove_links_for_pin(start_pin_id.id())
                            self._remove_links_for_pin(end_pin_id.id())
                            self._links.append(
                                (self._next_link_id, start_pin_id.id(), end_pin_id.id())
                            )
                            self._next_link_id += 1
                    else:
                        ed.reject_new_item(LINK_INVALID_COLOR, 3.0)
            ed.end_create()

    def _handle_link_deletion(self) -> None:
        if ed.begin_delete():
            link_id = ed.LinkId()
            while ed.query_deleted_link(link_id):
                if ed.accept_deleted_item():
                    self._links = [
                        link for link in self._links if link[0] != link_id.id()
                    ]
            ed.end_delete()

    def _render_links(self) -> None:
        for link_id, start_pin, end_pin in self._links:
            ed.link(ed.LinkId(link_id), ed.PinId(start_pin), ed.PinId(end_pin))

    def _build_address_tree(self) -> dict[int, dict[int, list[Device]]]:
        tree: dict[int, dict[int, list[Device]]] = {}
        for device in self._devices:
            parts = device.address.split(".")
            area, line = int(parts[0]), int(parts[1])
            if area not in tree:
                tree[area] = {}
            if line not in tree[area]:
                tree[area][line] = []
            tree[area][line].append(device)
        return tree

    def _calc_sidebar_width(self) -> float:
        indent = imgui.get_style().indent_spacing
        max_width = imgui.calc_text_size("Devices").x
        for device in self._devices:
            text = f"{device.name} ({device.address})"
            width = imgui.calc_text_size(text).x + indent * 3
            max_width = max(max_width, width)
        return max_width + imgui.get_style().window_padding.x * 2 + 20

    def _render_connection_status(self) -> None:
        if self._connected:
            label_text = f"Connected ({self._controller_ip})"
            label_width = imgui.calc_text_size(label_text).x + 24
            imgui.same_line(imgui.get_window_width() - label_width - 12)
            draw_list = imgui.get_window_draw_list()
            cursor = imgui.get_cursor_screen_pos()
            center = imgui.ImVec2(cursor.x + 6, cursor.y + imgui.get_frame_height() / 2)
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 5, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(center, 5 + pulse * 4, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse)))
            imgui.dummy(imgui.ImVec2(20, 0))
            imgui.same_line()
            imgui.push_style_color(imgui.Col_.header_hovered, imgui.ImVec4(0, 0, 0, 0))
            imgui.push_style_color(imgui.Col_.header_active, imgui.ImVec4(0, 0, 0, 0))
            if imgui.menu_item(label_text, "", False)[0]:
                imgui.open_popup("##ConnectedPopup")
            imgui.pop_style_color(2)
        else:
            label_width = imgui.calc_text_size("Connect").x + 16
            imgui.same_line(imgui.get_window_width() - label_width - 12)
            if imgui.menu_item("Connect", "", False)[0]:
                imgui.open_popup("##ConnectPopup")

        if imgui.begin_popup("##ConnectPopup"):
            imgui.text("KNX Controller IP")
            imgui.spacing()
            imgui.set_next_item_width(180)
            _, self._controller_ip = imgui.input_text("##ip", self._controller_ip)
            imgui.spacing()
            if imgui.button("Connect", imgui.ImVec2(180, 0)):
                self._connected = True
                imgui.close_current_popup()
            imgui.end_popup()

        if imgui.begin_popup("##ConnectedPopup"):
            imgui.text(f"Disconnect from {self._controller_ip}?")
            imgui.spacing()
            if imgui.button("Disconnect", imgui.ImVec2(180, 0)):
                self._connected = False
                imgui.close_current_popup()
            imgui.end_popup()

    def _render_menu_bar(self) -> None:
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("New Project", "", False)[0]:
                    pass
                if imgui.menu_item("Open Project", "", False)[0]:
                    pass
                if imgui.menu_item("Save Project", "", False)[0]:
                    pass
                imgui.separator()
                if imgui.menu_item("Exit", "", False)[0]:
                    pass
                imgui.end_menu()

            if imgui.begin_menu("Edit"):
                if imgui.menu_item("Undo", "Ctrl+Z", False)[0]:
                    pass
                if imgui.menu_item("Redo", "Ctrl+Y", False)[0]:
                    pass
                imgui.end_menu()

            if imgui.begin_menu("View"):
                clicked, self._show_sidebar = imgui.menu_item(
                    "Sidebar", "", self._show_sidebar
                )
                imgui.end_menu()

            self._render_connection_status()

            imgui.end_main_menu_bar()

    def _focus_device_by_address(self, address: str) -> None:
        for device in self._devices:
            if device.address == address:
                ed.select_node(ed.NodeId(device.node_id), False)
                ed.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)
                return

    def _telegram_to_row(self, telegram: Telegram) -> str:
        return "\t".join(col.getter(telegram) for col in TELEGRAM_COLUMNS)

    def _copy_telegrams(self) -> None:
        if self._selected_telegrams:
            indices = sorted(self._selected_telegrams)
        else:
            indices = range(len(self._telegrams))
        if not indices:
            return
        header = "\t".join(col.name for col in TELEGRAM_COLUMNS)
        rows = [self._telegram_to_row(self._telegrams[i]) for i in indices]
        imgui.set_clipboard_text("\n".join([header, *rows]))

    def _select_telegram_range(self, start: int, end: int, additive: bool) -> None:
        if not additive:
            self._selected_telegrams.clear()
        lo, hi = min(start, end), max(start, end)
        self._selected_telegrams.update(range(lo, hi + 1))

    def _toggle_telegram(self, index: int) -> None:
        self._selected_telegrams.symmetric_difference_update({index})
        self._last_selected_telegram = index

    def _select_single_telegram(self, index: int) -> None:
        self._selected_telegrams = {index}
        self._last_selected_telegram = index
        self._focus_device_by_address(self._telegrams[index].source)

    def _handle_telegram_click(self, index: int) -> None:
        io = imgui.get_io()
        ctrl = io.key_ctrl or io.key_super
        shift = io.key_shift
        if shift and self._last_selected_telegram >= 0:
            self._select_telegram_range(self._last_selected_telegram, index, additive=ctrl)
        elif ctrl:
            self._toggle_telegram(index)
        else:
            self._select_single_telegram(index)

    def _handle_telegrams_shortcuts(self) -> None:
        if not imgui.is_window_focused():
            return
        io = imgui.get_io()
        if (io.key_ctrl or io.key_super) and imgui.is_key_pressed(imgui.Key.c):
            self._copy_telegrams()

    def _render_telegrams_header(self) -> None:
        imgui.text("Telegrams")
        if self._selected_telegrams:
            imgui.same_line()
            imgui.text_disabled(f"  ({len(self._selected_telegrams)} selected)")
        imgui.same_line(imgui.get_window_width() - TELEGRAM_HEADER_BUTTONS_WIDTH)
        if imgui.small_button("Copy"):
            self._copy_telegrams()
        imgui.same_line()
        if imgui.small_button("Clear"):
            self._selected_telegrams.clear()
        imgui.separator()

    def _render_telegram_row(self, index: int, telegram: Telegram) -> None:
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        selected = index in self._selected_telegrams
        flags = imgui.SelectableFlags_.span_all_columns | imgui.SelectableFlags_.allow_overlap
        if imgui.selectable(f"{telegram.timestamp}##row{index}", selected, flags)[0]:
            self._handle_telegram_click(index)
        for col_index, column in enumerate(TELEGRAM_COLUMNS[1:], start=1):
            imgui.table_set_column_index(col_index)
            text = column.getter(telegram)
            if column.disabled:
                imgui.text_disabled(text)
            else:
                imgui.text(text)

    def _render_telegrams_table(self) -> None:
        flags = (
            imgui.TableFlags_.borders_inner_h
            | imgui.TableFlags_.row_bg
            | imgui.TableFlags_.scroll_y
            | imgui.TableFlags_.sizing_fixed_fit
        )
        if not imgui.begin_table("##telegrams_table", len(TELEGRAM_COLUMNS), flags):
            return
        for column in TELEGRAM_COLUMNS:
            col_flags = imgui.TableColumnFlags_.width_stretch if column.stretch else imgui.TableColumnFlags_.none
            imgui.table_setup_column(column.name, col_flags)
        imgui.table_headers_row()
        for i, telegram in enumerate(self._telegrams):
            self._render_telegram_row(i, telegram)
        imgui.end_table()

    def _render_telegrams_pane(self) -> None:
        imgui.begin_child("##TelegramsPane", imgui.ImVec2(0, 0), imgui.ChildFlags_.borders)
        self._render_telegrams_header()
        self._handle_telegrams_shortcuts()
        self._render_telegrams_table()
        imgui.end_child()

    def _render_bottom_bar(self) -> None:
        bar_height = 30
        viewport = imgui.get_main_viewport()
        imgui.set_next_window_pos(
            imgui.ImVec2(viewport.pos.x, viewport.pos.y + viewport.size.y - bar_height)
        )
        imgui.set_next_window_size(imgui.ImVec2(viewport.size.x, bar_height))
        imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(12, 4))
        imgui.push_style_var(imgui.StyleVar_.window_border_size, 0.0)
        flags = (
            imgui.WindowFlags_.no_decoration
            | imgui.WindowFlags_.no_move
            | imgui.WindowFlags_.no_saved_settings
        )
        imgui.begin("##BottomBar", None, flags)

        _, self._show_sidebar = imgui.checkbox("Sidebar", self._show_sidebar)
        imgui.same_line(spacing=20)
        _, self._show_telegrams = imgui.checkbox("Telegrams", self._show_telegrams)

        stats_text = f"Devices: {len(self._devices)} | Links: {len(self._links)}"
        text_width = imgui.calc_text_size(stats_text).x
        imgui.same_line(imgui.get_window_width() - text_width - 12)
        imgui.text(stats_text)

        imgui.end()
        imgui.pop_style_var(2)

    def render(self) -> None:
        if not self._editor_context:
            return

        self._render_menu_bar()
        self._render_bottom_bar()

        menu_bar_height = imgui.get_frame_height()
        bottom_bar_height = 26
        viewport = imgui.get_main_viewport()

        imgui.set_next_window_pos(imgui.ImVec2(viewport.pos.x, viewport.pos.y + menu_bar_height))
        imgui.set_next_window_size(imgui.ImVec2(viewport.size.x, viewport.size.y - menu_bar_height - bottom_bar_height))
        imgui.push_style_var(imgui.StyleVar_.window_border_size, 0.0)
        main_flags = imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_resize | imgui.WindowFlags_.no_title_bar
        imgui.begin("##MainArea", None, main_flags)
        imgui.pop_style_var()

        if self._show_sidebar:
            sidebar_width = self._calc_sidebar_width()
            imgui.begin_child("##Sidebar", imgui.ImVec2(sidebar_width, 0), imgui.ChildFlags_.borders)
            imgui.text("Devices")
            imgui.separator()
            tree = self._build_address_tree()
            for area in sorted(tree.keys()):
                area_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                if imgui.tree_node_ex(f"Area {area}", area_flags):
                    for line in sorted(tree[area].keys()):
                        line_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                        if imgui.tree_node_ex(f"Line {area}.{line}", line_flags):
                            for device in tree[area][line]:
                                flags = (
                                    imgui.TreeNodeFlags_.leaf
                                    | imgui.TreeNodeFlags_.no_tree_push_on_open
                                    | imgui.TreeNodeFlags_.span_avail_width
                                )
                                imgui.tree_node_ex(f"{device.name} ({device.address})", flags)
                                if imgui.is_item_clicked():
                                    ed.select_node(ed.NodeId(device.node_id), False)
                                    ed.navigate_to_selection(False, 0.3)
                            imgui.tree_pop()
                    imgui.tree_pop()
            imgui.end_child()
            imgui.same_line()

        imgui.begin_child("##RightArea", imgui.ImVec2(0, 0))

        telegram_pane_height = TELEGRAM_PANE_HEIGHT if self._show_telegrams else 0
        editor_height = imgui.get_content_region_avail().y - telegram_pane_height

        ed.set_current_editor(self._editor_context)
        ed.begin("##NodeEditorCanvas", imgui.ImVec2(0, editor_height))

        for device in self._devices:
            self._render_device_node(device.node_id, device.template, device.address)

        self._render_links()
        self._handle_link_creation()
        self._handle_link_deletion()

        ed.end()

        if self._show_telegrams:
            self._render_telegrams_pane()

        imgui.end_child()

        imgui.end()


def main() -> None:
    app = KnxGuiApp()

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "XKNX Toolkit"
    runner_params.app_window_params.window_geometry.size = (1280, 720)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown
    runner_params.callbacks.show_gui = app.render

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
