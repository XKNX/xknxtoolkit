import copy
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from imgui_bundle import imgui, hello_imgui, imgui_node_editor as ed, portable_file_dialogs as pfd

from xknx.product.errors import ArchiveError

from knx_gui.knxprod_loader import ParsedComObject, ParsedDeviceCandidate, parse_archive

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
LINK_LOOSE_COLOR = imgui.ImVec4(0.9, 0.7, 0.2, 1.0)
LINK_INVALID_COLOR = imgui.ImVec4(0.9, 0.2, 0.2, 1.0)

TELEGRAM_PANE_HEIGHT = 200
TELEGRAM_HEADER_BUTTONS_WIDTH = 100
NAVIGATE_TO_NODE_DURATION = 0.3


@dataclass(frozen=True)
class DPT:
    major: int
    minor: int
    name: str
    label: str

    @property
    def code(self) -> str:
        return f"{self.major}.{self.minor:03d}"


DPT_UNKNOWN = DPT(0, 0, "Unknown", "?")

# 1-bit (major 1) - boolean concepts
DPT_SWITCH = DPT(1, 1, "Switch", "switch")
DPT_BOOL = DPT(1, 2, "Boolean", "bool")
DPT_ENABLE = DPT(1, 3, "Enable", "enable")
DPT_RAMP = DPT(1, 4, "Ramp", "ramp")
DPT_ALARM = DPT(1, 5, "Alarm", "alarm")
DPT_BINARY_VALUE = DPT(1, 6, "Binary Value", "binary")
DPT_STEP = DPT(1, 7, "Step", "step")
DPT_UP_DOWN = DPT(1, 8, "Up/Down", "up/down")
DPT_OPEN_CLOSE = DPT(1, 9, "Open/Close", "open/close")
DPT_STOP = DPT(1, 10, "Start/Stop", "start/stop")
DPT_STATE = DPT(1, 11, "State", "state")
DPT_INVERT = DPT(1, 12, "Invert", "invert")
DPT_DIM_SEND_STYLE = DPT(1, 13, "Dim Send Style", "dim style")
DPT_INPUT_SOURCE = DPT(1, 14, "Input Source", "src")
DPT_RESET = DPT(1, 15, "Reset", "reset")
DPT_ACK = DPT(1, 16, "Acknowledge", "ack")
DPT_TRIGGER = DPT(1, 17, "Trigger", "trigger")
DPT_OCCUPANCY = DPT(1, 18, "Occupancy", "occupancy")
DPT_WINDOW_DOOR = DPT(1, 19, "Window/Door", "win/door")
DPT_LOGICAL_FUNCTION = DPT(1, 21, "Logical Function", "logic")
DPT_SCENE_AB = DPT(1, 22, "Scene A/B", "scene a/b")
DPT_SHUTTER_BLINDS_MODE = DPT(1, 23, "Shutter/Blinds Mode", "blinds mode")
DPT_DAY_NIGHT = DPT(1, 24, "Day/Night", "day/night")
DPT_HEAT_COOL = DPT(1, 100, "Heat/Cool", "heat/cool")

# 4-bit dimming
DPT_DIMMING = DPT(3, 7, "Dimming", "dim")
DPT_BLINDS = DPT(3, 8, "Blinds", "blinds")

# 8-bit unsigned (major 5)
DPT_PERCENT = DPT(5, 1, "Percent", "%")
DPT_ANGLE = DPT(5, 3, "Angle", "°")
DPT_PERCENT_U8 = DPT(5, 4, "Percent (uint8)", "%u8")
DPT_DECIMAL_FACTOR = DPT(5, 5, "Decimal Factor", "factor")
DPT_TARIFF = DPT(5, 6, "Tariff", "tariff")
DPT_VALUE_1_UCOUNT = DPT(5, 10, "Counter (uint8)", "count")

# 8-bit signed (major 6)
DPT_VALUE_1_COUNT = DPT(6, 10, "Counter (int8)", "i8")

# 16-bit unsigned (major 7)
DPT_COLOR_TEMP_KELVIN = DPT(7, 600, "Color Temperature", "K")

# Time / Date (majors 10, 11, 19)
DPT_TIME_OF_DAY = DPT(10, 1, "Time of Day", "time")
DPT_DATE = DPT(11, 1, "Date", "date")
DPT_DATE_TIME = DPT(19, 1, "Date/Time", "datetime")

# 16-bit float (major 9) - common physical quantities
DPT_TEMPERATURE = DPT(9, 1, "Temperature", "°C")
DPT_TEMPERATURE_DELTA = DPT(9, 2, "Temperature Delta", "ΔK")
DPT_LUX = DPT(9, 4, "Illuminance", "lux")
DPT_WIND_SPEED = DPT(9, 5, "Wind Speed", "m/s")
DPT_PRESSURE = DPT(9, 6, "Pressure", "Pa")
DPT_HUMIDITY = DPT(9, 7, "Humidity", "%RH")
DPT_PARTS_PER_MILLION = DPT(9, 8, "ppm", "ppm")
DPT_TIME_DIFF = DPT(9, 10, "Time Difference (s)", "s")
DPT_VOLT = DPT(9, 20, "Voltage", "mV")
DPT_CURRENT = DPT(9, 21, "Current", "mA")
DPT_POWER_DENSITY = DPT(9, 22, "Power Density", "W/m²")
DPT_KELVIN = DPT(9, 23, "Kelvin/%", "K/%")
DPT_POWER = DPT(9, 24, "Power", "kW")

# Scenes / control
DPT_SCENE = DPT(17, 1, "Scene", "scene")
DPT_SCENE_CONTROL = DPT(18, 1, "Scene Control", "scene ctrl")

# Color (major 232 / 249)
DPT_RGB = DPT(232, 600, "RGB", "rgb")
DPT_BRIGHTNESS_COLOR_TEMP_TRANSITION = DPT(249, 600, "Brightness/Color Temp/Transition", "bri/K/t")


KNOWN_DPTS: dict[tuple[int, int], DPT] = {
    (d.major, d.minor): d
    for d in [
        DPT_SWITCH, DPT_BOOL, DPT_ENABLE, DPT_RAMP, DPT_ALARM, DPT_BINARY_VALUE,
        DPT_STEP, DPT_UP_DOWN, DPT_OPEN_CLOSE, DPT_STOP, DPT_STATE, DPT_INVERT,
        DPT_DIM_SEND_STYLE, DPT_INPUT_SOURCE, DPT_RESET, DPT_ACK, DPT_TRIGGER,
        DPT_OCCUPANCY, DPT_WINDOW_DOOR, DPT_LOGICAL_FUNCTION, DPT_SCENE_AB,
        DPT_SHUTTER_BLINDS_MODE, DPT_DAY_NIGHT, DPT_HEAT_COOL,
        DPT_DIMMING, DPT_BLINDS,
        DPT_PERCENT, DPT_ANGLE, DPT_PERCENT_U8, DPT_DECIMAL_FACTOR, DPT_TARIFF, DPT_VALUE_1_UCOUNT,
        DPT_VALUE_1_COUNT,
        DPT_COLOR_TEMP_KELVIN,
        DPT_TIME_OF_DAY, DPT_DATE, DPT_DATE_TIME,
        DPT_TEMPERATURE, DPT_TEMPERATURE_DELTA, DPT_LUX, DPT_WIND_SPEED, DPT_PRESSURE,
        DPT_HUMIDITY, DPT_PARTS_PER_MILLION, DPT_TIME_DIFF, DPT_VOLT, DPT_CURRENT,
        DPT_POWER_DENSITY, DPT_KELVIN, DPT_POWER,
        DPT_SCENE, DPT_SCENE_CONTROL,
        DPT_RGB, DPT_BRIGHTNESS_COLOR_TEMP_TRANSITION,
    ]
}


def lookup_or_make_dpt(code: str | None) -> DPT:
    if not code:
        return DPT_UNKNOWN
    parts = code.split(".")
    if len(parts) != 2:
        return DPT_UNKNOWN
    try:
        major = int(parts[0])
        minor = int(parts[1])
    except ValueError:
        return DPT_UNKNOWN
    known = KNOWN_DPTS.get((major, minor))
    if known is not None:
        return known
    return DPT(major, minor, f"DPT {major}.{minor:03d}", code)


DPT_MAJOR_COLORS: dict[int, imgui.ImVec4] = {
    1: imgui.ImVec4(0.9, 0.3, 0.3, 1.0),
    3: imgui.ImVec4(0.9, 0.6, 0.2, 1.0),
    5: imgui.ImVec4(0.2, 0.8, 0.4, 1.0),
    6: imgui.ImVec4(0.2, 0.7, 0.5, 1.0),
    7: imgui.ImVec4(0.6, 0.8, 0.9, 1.0),
    9: imgui.ImVec4(0.2, 0.6, 0.9, 1.0),
    10: imgui.ImVec4(0.7, 0.7, 0.5, 1.0),
    11: imgui.ImVec4(0.7, 0.7, 0.5, 1.0),
    17: imgui.ImVec4(0.7, 0.3, 0.9, 1.0),
    18: imgui.ImVec4(0.7, 0.3, 0.9, 1.0),
    19: imgui.ImVec4(0.7, 0.7, 0.5, 1.0),
    232: imgui.ImVec4(0.9, 0.2, 0.6, 1.0),
    249: imgui.ImVec4(0.95, 0.4, 0.7, 1.0),
}


def dpt_color(dpt: DPT) -> imgui.ImVec4:
    return DPT_MAJOR_COLORS.get(dpt.major, imgui.ImVec4(0.5, 0.5, 0.5, 1.0))


class DPTMatch(Enum):
    NONE = "none"
    LOOSE = "loose"
    EXACT = "exact"


def dpt_match(a: DPT, b: DPT) -> DPTMatch:
    if a.major != b.major:
        return DPTMatch.NONE
    if a.minor == b.minor:
        return DPTMatch.EXACT
    return DPTMatch.LOOSE


class PinDir(Enum):
    INPUT = "input"
    OUTPUT = "output"


@dataclass
class ComObjectFlags:
    communication: bool = True
    read: bool = False
    write: bool = False
    transmit: bool = False
    update: bool = False
    read_on_init: bool = False

    @classmethod
    def default_input(cls) -> "ComObjectFlags":
        return cls(communication=True, write=True)

    @classmethod
    def default_output(cls) -> "ComObjectFlags":
        return cls(communication=True, read=True, transmit=True)


def default_flags_for(direction: PinDir) -> ComObjectFlags:
    if direction == PinDir.INPUT:
        return ComObjectFlags.default_input()
    return ComObjectFlags.default_output()


def is_default_flags(flags: ComObjectFlags, direction: PinDir) -> bool:
    return flags == default_flags_for(direction)


@dataclass
class ComObject:
    name: str
    dpt: DPT
    flags: ComObjectFlags
    supported_dpts: list[DPT] = field(default_factory=list)


def listen_obj(
    name: str,
    dpt: DPT,
    supported: list[DPT] | None = None,
    **flag_overrides: bool,
) -> ComObject:
    flags = ComObjectFlags.default_input()
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(name, dpt, flags, supported_dpts=supported or [])


def send_obj(
    name: str,
    dpt: DPT,
    supported: list[DPT] | None = None,
    **flag_overrides: bool,
) -> ComObject:
    flags = ComObjectFlags.default_output()
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(name, dpt, flags, supported_dpts=supported or [])


def bidirectional_obj(name: str, dpt: DPT, **flag_overrides: bool) -> ComObject:
    flags = ComObjectFlags(communication=True, read=True, write=True, transmit=True)
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(name, dpt, flags)


FLAG_LABELS = [
    ("communication", "C", "Communication"),
    ("read", "R", "Read"),
    ("write", "W", "Write"),
    ("transmit", "T", "Transmit"),
    ("update", "U", "Update"),
    ("read_on_init", "I", "Read on Init"),
]


def com_object_has_input(co: ComObject) -> bool:
    return co.flags.write or co.flags.update


def com_object_has_output(co: ComObject) -> bool:
    return co.flags.transmit or co.flags.read


@dataclass
class PinRow:
    """A computed visual row containing 1 or 2 com objects.

    - Single bidirectional com object: left and right reference the same instance.
    - Single input-only or output-only: only one of left/right is set.
    - Two com objects (input-only + output-only): left and right reference different instances.
    """
    left: ComObject | None = None
    right: ComObject | None = None


def generate_rows(com_objects: list[ComObject]) -> list[PinRow]:
    """Pair com objects into visual rows based on their current flag state.

    Walks the list in order:
    - Bidirectional (both input + output): own row, same instance both sides
    - Input-only: tries to pair with the next output-only encountered
    - Output-only: tries to pair with a pending input-only
    - No pins: skipped (still shown in com object table)
    """
    rows: list[PinRow] = []
    pending_input: ComObject | None = None

    for co in com_objects:
        has_in = com_object_has_input(co)
        has_out = com_object_has_output(co)
        if has_in and has_out:
            if pending_input is not None:
                rows.append(PinRow(left=pending_input))
                pending_input = None
            rows.append(PinRow(left=co, right=co))
        elif has_in:
            if pending_input is not None:
                rows.append(PinRow(left=pending_input))
            pending_input = co
        elif has_out:
            if pending_input is not None:
                rows.append(PinRow(left=pending_input, right=co))
                pending_input = None
            else:
                rows.append(PinRow(right=co))
    if pending_input is not None:
        rows.append(PinRow(left=pending_input))
    return rows


@dataclass
class DeviceConfig:
    manufacturer: str
    application: str
    hardware: str
    firmware: str


@dataclass
class DeviceTemplate:
    name: str
    com_objects: list[ComObject]
    config: DeviceConfig


DEVICE_TEMPLATES: dict[str, DeviceTemplate] = {
    "switch_actuator": DeviceTemplate(
        name="Switch Actuator",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
        ],
        config=DeviceConfig("ABB", "SA/S 4.16.2.2", "2CDG110252R0011", "1.2.3"),
    ),
    "dimmer_actuator": DeviceTemplate(
        name="Dimmer Actuator",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
            listen_obj("Dimming", DPT_DIMMING),
            listen_obj("Brightness", DPT_PERCENT),
            send_obj("Value", DPT_PERCENT),
        ],
        config=DeviceConfig("ABB", "DA/S 4.230.2.1", "2CDG110198R0011", "2.1.0"),
    ),
    "temperature_sensor": DeviceTemplate(
        name="Temperature Sensor",
        com_objects=[
            send_obj("Temperature", DPT_TEMPERATURE),
        ],
        config=DeviceConfig("Siemens", "QMX3.P37", "5WG1258-3AB13", "3.0.1"),
    ),
    "push_button": DeviceTemplate(
        name="Push Button",
        com_objects=[
            send_obj("Press", DPT_SWITCH),
            send_obj("Long Press", DPT_SWITCH),
            send_obj("Scene", DPT_SCENE),
        ],
        config=DeviceConfig("Gira", "Tastsensor 4 Plus", "2104..", "1.0.5"),
    ),
    "blinds_actuator": DeviceTemplate(
        name="Blinds Actuator",
        com_objects=[
            listen_obj("Move", DPT_UP_DOWN),
            send_obj("Position", DPT_PERCENT),
            listen_obj("Stop", DPT_STOP),
            listen_obj("Slat", DPT_PERCENT),
            send_obj("Slat Pos", DPT_PERCENT),
        ],
        config=DeviceConfig("MDT", "JAL-0410M.02", "JAL-0410M", "2.5.1"),
    ),
    "shutter_button": DeviceTemplate(
        name="Shutter Button",
        com_objects=[
            send_obj("Up/Down", DPT_UP_DOWN),
            send_obj("Stop", DPT_STOP),
        ],
        config=DeviceConfig("Gira", "Jalousie Button", "2104J", "1.0.2"),
    ),
    "rgb_controller": DeviceTemplate(
        name="RGB Controller",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
            listen_obj("Color", DPT_RGB),
            send_obj("Color Status", DPT_RGB),
            listen_obj("Brightness", DPT_PERCENT),
        ],
        config=DeviceConfig("MDT", "AKD-0424R2.02", "R2.02", "1.1.0"),
    ),
    "logic_gate": DeviceTemplate(
        name="Logic Gate",
        com_objects=[
            listen_obj(
                "Input A",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
            listen_obj(
                "Input B",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
            send_obj(
                "Output",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
        ],
        config=DeviceConfig("MDT", "Logic AKK-04UP.03", "AKK-04UP", "1.0.0"),
    ),
    "thermostat": DeviceTemplate(
        name="Thermostat",
        com_objects=[
            listen_obj("Setpoint", DPT_TEMPERATURE, read_on_init=True),
            send_obj("Actual Temp", DPT_TEMPERATURE),
            send_obj("Heating", DPT_SWITCH, read=False),
            send_obj("Valve", DPT_PERCENT),
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
    com_objects: list[ComObject] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.com_objects:
            self.com_objects = copy.deepcopy(self.template.com_objects)

    @property
    def rows(self) -> list[PinRow]:
        return generate_rows(self.com_objects)


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
        self._drag_source_pin: int | None = None
        self._open_file_dialog: pfd.open_file | None = None
        self._archive_candidates: list[ParsedDeviceCandidate] = []
        self._archive_path: str | None = None
        self._archive_load_error: str | None = None
        self._show_archive_popup: bool = False
        self._dpt_popup_target: ComObject | None = None
        self._dpt_popup_request: ComObject | None = None
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
            Device(7, "Bedroom Blinds", DEVICE_TEMPLATES["blinds_actuator"], "1.2.3"),
            Device(8, "Shutter Button", DEVICE_TEMPLATES["shutter_button"], "1.2.4"),
            Device(9, "Logic AND", DEVICE_TEMPLATES["logic_gate"], "1.3.1"),
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
        config.force_window_content_width_to_node_width = True
        self._editor_context = ed.create_editor(config)

    def shutdown(self) -> None:
        if self._editor_context:
            ed.destroy_editor(self._editor_context)
            self._editor_context = None

    def _draw_flag_badges(self, flags: ComObjectFlags, direction: PinDir) -> None:
        diffs = flag_diff_letters(flags, direction)
        if not diffs:
            return
        for letter, is_set in diffs:
            color = imgui.ImVec4(0.4, 0.7, 0.3, 1.0) if is_set else imgui.ImVec4(0.7, 0.3, 0.3, 1.0)
            imgui.push_style_color(imgui.Col_.text, color)
            imgui.text(letter if is_set else f"!{letter}")
            imgui.pop_style_color()
            if imgui.is_item_hovered():
                self._show_flags_tooltip(flags, direction)
            imgui.same_line()

    def _show_flags_tooltip(self, flags: ComObjectFlags, direction: PinDir) -> None:
        ed.suspend()
        imgui.begin_tooltip()
        imgui.text(f"Default for {direction.value}:")
        default = default_flags_for(direction)
        for attr, letter, name in FLAG_LABELS:
            current = getattr(flags, attr)
            default_val = getattr(default, attr)
            symbol = "✓" if current else "✗"
            label = f"{symbol} {letter}  {name}"
            if current != default_val:
                color = imgui.ImVec4(0.4, 0.7, 0.3, 1.0) if current else imgui.ImVec4(0.7, 0.3, 0.3, 1.0)
                imgui.push_style_color(imgui.Col_.text, color)
                imgui.text(label + "  (modified)")
                imgui.pop_style_color()
            else:
                imgui.text_disabled(label)
        imgui.end_tooltip()
        ed.resume()

    def _calc_pin_highlight(self, pin: ComObject, direction: PinDir) -> tuple[float, bool]:
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
            draw_list.add_circle_filled(center, PIN_RADIUS + 4, color_u32(base_color.x, base_color.y, base_color.z, 0.3))
            draw_list.add_circle_filled(center, PIN_RADIUS + 2, color_u32(base_color.x, base_color.y, base_color.z, 0.5))
        draw_list.add_circle_filled(center, PIN_RADIUS, color)
        draw_list.add_circle(center, PIN_RADIUS, color_u32(1, 1, 1, 0.3 * alpha), 0, 1.5)
        imgui.dummy(imgui.ImVec2(PIN_RADIUS * 2, PIN_HEIGHT))

    def _calc_node_layout(self, device: "Device") -> NodeLayout:
        in_dpt_w = in_name_w = out_dpt_w = out_name_w = 0.0
        for row in device.rows:
            if row.left and com_object_has_input(row.left):
                in_dpt_w = max(in_dpt_w, imgui.calc_text_size(f"[{row.left.dpt.label}]").x)
                in_name_w = max(in_name_w, imgui.calc_text_size(row.left.name).x)
            if row.right and com_object_has_output(row.right):
                out_dpt_w = max(out_dpt_w, imgui.calc_text_size(f"[{row.right.dpt.label}]").x)
                out_name_w = max(out_name_w, imgui.calc_text_size(row.right.name).x)

        spacing = imgui.get_style().item_spacing.x
        in_total_w = PIN_RADIUS * 2 + in_name_w + in_dpt_w + spacing * 4 if in_name_w > 0 else 0
        out_total_w = PIN_RADIUS * 2 + out_name_w + out_dpt_w + spacing * 4 if out_name_w > 0 else 0

        config = device.template.config
        tree_indent = imgui.get_style().indent_spacing
        max_value_w = max(
            imgui.calc_text_size(config.manufacturer).x,
            imgui.calc_text_size(config.application).x,
            imgui.calc_text_size(config.hardware).x,
            imgui.calc_text_size(config.firmware).x,
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
            imgui.push_style_color(imgui.Col_.text, imgui.get_style().color_(imgui.Col_.text_disabled))
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
                imgui.text_disabled("Select DPT")
                imgui.separator()
                for dpt in target.supported_dpts:
                    selected = dpt.major == target.dpt.major and dpt.minor == target.dpt.minor
                    if imgui.menu_item(f"{dpt.code}  {dpt.name}", "", selected)[0]:
                        target.dpt = dpt
            imgui.end_popup()
        else:
            self._dpt_popup_target = None

    def _render_input_pin(self, pin_id: int, pin: ComObject, layout: NodeLayout) -> None:
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
        imgui.dummy(imgui.ImVec2(layout.in_name_w - imgui.calc_text_size(pin.name).x, 1))
        ed.end_pin()
        imgui.same_line()
        dpt_label = f"[{pin.dpt.label}]"
        self._render_dpt_label(pin, pin_id)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.in_dpt_w - imgui.calc_text_size(dpt_label).x, 1))

    def _render_output_pin(self, pin_id: int, pin: ComObject, layout: NodeLayout) -> None:
        self._pin_dpt[pin_id] = pin.dpt
        self._pin_dir[pin_id] = PinDir.OUTPUT
        alpha, glow = self._calc_pin_highlight(pin, PinDir.OUTPUT)
        if not pin.flags.communication:
            alpha *= 0.4
            glow = False
        dpt_label = f"[{pin.dpt.label}]"
        self._render_dpt_label(pin, pin_id)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.out_dpt_w - imgui.calc_text_size(dpt_label).x, 1))
        imgui.same_line()
        ed.begin_pin(ed.PinId(pin_id), ed.PinKind.output)
        ed.pin_pivot_alignment(imgui.ImVec2(1.0, 0.5))
        if pin.flags.communication:
            imgui.text_unformatted(pin.name)
        else:
            imgui.text_disabled(pin.name)
        imgui.same_line()
        imgui.dummy(imgui.ImVec2(layout.out_name_w - imgui.calc_text_size(pin.name).x, 1))
        imgui.same_line()
        self._draw_pin_icon(pin.dpt, alpha, glow)
        ed.end_pin()

    def _render_node_header(self, template: DeviceTemplate, address: str, width: float) -> Rect:
        cursor_x = imgui.get_cursor_pos_x()
        imgui.begin_group()
        imgui.text(template.name)
        if address:
            imgui.same_line()
            address_width = imgui.calc_text_size(address).x
            imgui.set_cursor_pos_x(cursor_x + width - address_width)
            imgui.text_disabled(address)
        imgui.end_group()
        rect_min = imgui.get_item_rect_min()
        rect_max = imgui.get_item_rect_max()
        return Rect(rect_min.x, rect_min.y, rect_max.x, rect_max.y)

    def _render_node_pins(self, device: "Device", layout: NodeLayout) -> None:
        pin_base = device.node_id * 100
        co_indices = {id(co): idx for idx, co in enumerate(device.com_objects)}
        for row in device.rows:
            if row.left and com_object_has_input(row.left):
                self._render_input_pin(pin_base + co_indices[id(row.left)], row.left, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.in_total_w, PIN_HEIGHT))
            imgui.same_line(spacing=layout.mid_spacing)
            if row.right and com_object_has_output(row.right):
                self._render_output_pin(pin_base + 50 + co_indices[id(row.right)], row.right, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.out_total_w, PIN_HEIGHT))

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(SETTINGS_LABEL_OFFSET)
        imgui.text(value)

    def _render_com_object_row(self, com_object: ComObject, row_id: str) -> None:
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        imgui.text(com_object.name)
        for col, (attr, _letter, full_name) in enumerate(FLAG_LABELS, start=1):
            imgui.table_set_column_index(col)
            current = getattr(com_object.flags, attr)
            changed, new_value = imgui.checkbox(f"##{row_id}_{attr}", current)
            if changed:
                setattr(com_object.flags, attr, new_value)
            if imgui.is_item_hovered():
                imgui.set_tooltip(full_name)

    def _render_node_com_objects(self, device: "Device") -> None:
        flags = imgui.TableFlags_.borders_inner | imgui.TableFlags_.sizing_fixed_fit
        if not imgui.begin_table(f"##com_objs_{device.node_id}", 1 + len(FLAG_LABELS), flags):
            return
        imgui.table_setup_column("Name")
        for _attr, letter, _name in FLAG_LABELS:
            imgui.table_setup_column(letter)
        imgui.table_headers_row()
        for i, com_obj in enumerate(device.com_objects):
            self._render_com_object_row(com_obj, f"{device.node_id}_{i}")
        imgui.end_table()

    def _render_node_settings(self, device: "Device", width: float) -> None:
        cursor = imgui.get_cursor_screen_pos()
        clip_max = imgui.ImVec2(cursor.x + width, cursor.y + SETTINGS_CLIP_HEIGHT)
        imgui.push_clip_rect(cursor, clip_max, True)
        config = device.template.config
        if imgui.tree_node(f"Manufacturer##{device.node_id}"):
            self._render_label_value("Manufacturer", config.manufacturer)
            self._render_label_value("Application", config.application)
            self._render_label_value("Hardware", config.hardware)
            self._render_label_value("Firmware", config.firmware)
            imgui.tree_pop()
        if imgui.tree_node(f"Com Flags##{device.node_id}"):
            self._render_node_com_objects(device)
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

    def _render_device_node(self, device: "Device") -> None:
        ed.begin_node(ed.NodeId(device.node_id))

        layout = self._calc_node_layout(device)
        header = self._render_node_header(device.template, device.address, layout.node_width)
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
        for _, start, end in self._links:
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
            label = "outputs" if dir_a == PinDir.OUTPUT else "inputs"
            imgui.text(f"Cannot connect two {label}")
            imgui.pop_style_color()
        else:
            match = dpt_match(dpt_a, dpt_b)
            if match == DPTMatch.EXACT:
                imgui.text(f"DPT {dpt_a.code} - {dpt_a.name}")
            elif match == DPTMatch.LOOSE:
                imgui.push_style_color(imgui.Col_.text, LINK_LOOSE_COLOR)
                imgui.text("Warning: same byte format, different semantics")
                imgui.pop_style_color()
                imgui.text(f"From: DPT {dpt_a.code} - {dpt_a.name}")
                imgui.text(f"To:   DPT {dpt_b.code} - {dpt_b.name}")
            else:
                imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
                imgui.text("Incompatible DPTs")
                imgui.pop_style_color()
                imgui.text(f"From: DPT {dpt_a.code} - {dpt_a.name}")
                imgui.text(f"To:   DPT {dpt_b.code} - {dpt_b.name}")
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
                        preview_color = LINK_COLOR if match == DPTMatch.EXACT else LINK_LOOSE_COLOR
                        if ed.accept_new_item(preview_color, 2.0):
                            self._links.append(
                                (self._next_link_id, start_pin_id.id(), end_pin_id.id())
                            )
                            self._next_link_id += 1
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
                    self._links = [
                        link for link in self._links if link[0] != link_id.id()
                    ]
            ed.end_delete()

    def _render_links(self) -> None:
        for link_id, start_pin, end_pin in self._links:
            match = self._pins_match_quality(start_pin, end_pin)
            color = LINK_LOOSE_COLOR if match == DPTMatch.LOOSE else LINK_COLOR
            ed.link(ed.LinkId(link_id), ed.PinId(start_pin), ed.PinId(end_pin), color)

    def _build_address_tree(self) -> tuple[dict[int, dict[int, list[Device]]], list[Device]]:
        tree: dict[int, dict[int, list[Device]]] = {}
        unassigned: list[Device] = []
        for device in self._devices:
            if not device.address:
                unassigned.append(device)
                continue
            parts = device.address.split(".")
            if len(parts) < 2:
                unassigned.append(device)
                continue
            try:
                area, line = int(parts[0]), int(parts[1])
            except ValueError:
                unassigned.append(device)
                continue
            if area not in tree:
                tree[area] = {}
            if line not in tree[area]:
                tree[area][line] = []
            tree[area][line].append(device)
        return tree, unassigned

    def _calc_sidebar_width(self) -> float:
        indent = imgui.get_style().indent_spacing
        max_width = imgui.calc_text_size("Devices").x
        for device in self._devices:
            label = f"{device.name} ({device.address})" if device.address else device.name
            width = imgui.calc_text_size(label).x + indent * 3
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

    def _poll_open_file_dialog(self) -> None:
        if self._open_file_dialog is None:
            return
        if not self._open_file_dialog.ready():
            return
        result = self._open_file_dialog.result()
        self._open_file_dialog = None
        if not result:
            return
        self._load_knxprod(result[0])

    def _load_knxprod(self, path: str) -> None:
        self._archive_load_error = None
        self._archive_candidates = []
        self._archive_path = path
        try:
            self._archive_candidates = parse_archive(path)
        except ArchiveError as e:
            self._archive_load_error = str(e)
        except (OSError, ValueError) as e:
            self._archive_load_error = f"{type(e).__name__}: {e}"
        self._show_archive_popup = True

    def _candidate_to_template(self, candidate: ParsedDeviceCandidate) -> DeviceTemplate:
        com_objects: list[ComObject] = []
        for co in candidate.raw_com_objects:
            flags = ComObjectFlags(
                communication=co.flags["communication"],
                read=co.flags["read"],
                write=co.flags["write"],
                transmit=co.flags["transmit"],
                update=co.flags["update"],
                read_on_init=co.flags["read_on_init"],
            )
            supported = [lookup_or_make_dpt(code) for code in co.dpt_codes]
            seen: set[tuple[int, int]] = set()
            unique_supported: list[DPT] = []
            for dpt in supported:
                key = (dpt.major, dpt.minor)
                if key in seen:
                    continue
                seen.add(key)
                unique_supported.append(dpt)
            primary = unique_supported[0] if unique_supported else DPT_UNKNOWN
            com_objects.append(
                ComObject(
                    name=co.name,
                    dpt=primary,
                    flags=flags,
                    supported_dpts=unique_supported,
                )
            )
        return DeviceTemplate(
            name=candidate.name,
            com_objects=com_objects,
            config=DeviceConfig(
                manufacturer=candidate.manufacturer_id,
                application=candidate.application_id,
                hardware="",
                firmware="",
            ),
        )

    def _add_candidate_as_device(self, candidate: ParsedDeviceCandidate) -> None:
        template = self._candidate_to_template(candidate)
        next_id = max((d.node_id for d in self._devices), default=0) + 1
        self._devices.append(
            Device(
                node_id=next_id,
                name=candidate.name,
                template=template,
                address="",
            )
        )

    def _render_archive_popup(self) -> None:
        if self._show_archive_popup:
            imgui.open_popup("##ArchivePopup")
            self._show_archive_popup = False
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing, imgui.ImVec2(0.5, 0.5))
        imgui.set_next_window_size_constraints(imgui.ImVec2(400, 0), imgui.ImVec2(800, 600))
        if imgui.begin_popup("##ArchivePopup"):
            if self._archive_load_error:
                imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
                imgui.text("Failed to load archive")
                imgui.pop_style_color()
                imgui.text(self._archive_load_error)
            else:
                imgui.text(f"Loaded: {self._archive_path}")
                imgui.text(f"Found {len(self._archive_candidates)} application(s)")
                imgui.separator()
                for i, candidate in enumerate(self._archive_candidates):
                    imgui.text(candidate.name)
                    imgui.same_line()
                    imgui.text_disabled(f"  ({len(candidate.raw_com_objects)} com objects)")
                    imgui.same_line()
                    if imgui.small_button(f"Add##{i}"):
                        self._add_candidate_as_device(candidate)
            imgui.spacing()
            if imgui.button("Close", imgui.ImVec2(120, 0)):
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
                if imgui.menu_item("Load .knxprod...", "", False)[0]:
                    self._open_file_dialog = pfd.open_file(
                        "Open KNX product archive",
                        "",
                        ["KNX product (*.knxprod)", "*.knxprod", "All files", "*"],
                    )
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
        self._poll_open_file_dialog()
        self._render_archive_popup()
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
            tree, unassigned = self._build_address_tree()
            leaf_flags = (
                imgui.TreeNodeFlags_.leaf
                | imgui.TreeNodeFlags_.no_tree_push_on_open
                | imgui.TreeNodeFlags_.span_avail_width
            )
            for area in sorted(tree.keys()):
                area_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                if imgui.tree_node_ex(f"Area {area}", area_flags):
                    for line in sorted(tree[area].keys()):
                        line_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                        if imgui.tree_node_ex(f"Line {area}.{line}", line_flags):
                            for device in tree[area][line]:
                                imgui.tree_node_ex(f"{device.name} ({device.address})", leaf_flags)
                                if imgui.is_item_clicked():
                                    ed.select_node(ed.NodeId(device.node_id), False)
                                    ed.navigate_to_selection(False, 0.3)
                            imgui.tree_pop()
                    imgui.tree_pop()
            if unassigned:
                unassigned_flags = imgui.TreeNodeFlags_.default_open | imgui.TreeNodeFlags_.span_avail_width
                if imgui.tree_node_ex(f"Unassigned ({len(unassigned)})", unassigned_flags):
                    for device in unassigned:
                        imgui.tree_node_ex(device.name, leaf_flags)
                        if imgui.is_item_clicked():
                            ed.select_node(ed.NodeId(device.node_id), False)
                            ed.navigate_to_selection(False, 0.3)
                    imgui.tree_pop()
            imgui.end_child()
            imgui.same_line()

        imgui.begin_child("##RightArea", imgui.ImVec2(0, 0))

        telegram_pane_height = TELEGRAM_PANE_HEIGHT if self._show_telegrams else 0
        editor_height = imgui.get_content_region_avail().y - telegram_pane_height

        ed.set_current_editor(self._editor_context)
        ed.begin("##NodeEditorCanvas", imgui.ImVec2(0, editor_height))

        for device in self._devices:
            self._render_device_node(device)

        self._render_links()
        self._handle_link_creation()
        self._handle_link_deletion()

        ed.end()
        self._render_dpt_popup()

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
