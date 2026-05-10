import copy
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from imgui_bundle import hello_imgui, imgui
from imgui_bundle import imgui_node_editor as ed
from imgui_bundle import portable_file_dialogs as pfd

from knx_gui.knxprod import (
    DeviceApplication,
    ParamType,
    ParamTypeKind,
    parse_archive,
)
from xknx.product.errors import ArchiveError

NODE_PADDING = 8.0
HEADER_INSET = 1.0
HEADER_BOTTOM_PADDING = 4.0
PIN_RADIUS = 5.0
PIN_HEIGHT = PIN_RADIUS * 2 + 4
MIN_PIN_SPACING = 20.0
SETTINGS_LABEL_OFFSET = 120.0
HEADER_COLOR = (0.2, 0.4, 0.7)
LINK_COLOR = imgui.ImVec4(0.6, 0.6, 0.6, 1.0)
LINK_LOOSE_COLOR = imgui.ImVec4(0.9, 0.7, 0.2, 1.0)
LINK_INVALID_COLOR = imgui.ImVec4(0.9, 0.2, 0.2, 1.0)

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

# 1-bit controlled (major 2)
DPT_SWITCH_CONTROL = DPT(2, 1, "Switch Control", "switch ctrl")

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

# 14-byte string (major 16)
DPT_STRING_LATIN1 = DPT(16, 1, "String (ISO 8859-1)", "string")

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
        DPT_SWITCH_CONTROL,
        DPT_DIMMING, DPT_BLINDS,
        DPT_PERCENT, DPT_ANGLE, DPT_PERCENT_U8, DPT_DECIMAL_FACTOR, DPT_TARIFF, DPT_VALUE_1_UCOUNT,
        DPT_VALUE_1_COUNT,
        DPT_COLOR_TEMP_KELVIN,
        DPT_TIME_OF_DAY, DPT_DATE, DPT_DATE_TIME,
        DPT_STRING_LATIN1,
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
    2: imgui.ImVec4(0.9, 0.5, 0.5, 1.0),
    3: imgui.ImVec4(0.9, 0.6, 0.2, 1.0),
    5: imgui.ImVec4(0.2, 0.8, 0.4, 1.0),
    6: imgui.ImVec4(0.2, 0.7, 0.5, 1.0),
    7: imgui.ImVec4(0.6, 0.8, 0.9, 1.0),
    9: imgui.ImVec4(0.2, 0.6, 0.9, 1.0),
    10: imgui.ImVec4(0.7, 0.7, 0.5, 1.0),
    11: imgui.ImVec4(0.7, 0.7, 0.5, 1.0),
    16: imgui.ImVec4(0.5, 0.8, 0.8, 1.0),
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
    read_locked: bool = False
    write_locked: bool = False
    transmit_locked: bool = False
    update_locked: bool = False
    read_on_init_locked: bool = False

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
    id: str
    name: str
    dpt: DPT
    flags: ComObjectFlags
    supported_dpts: list[DPT] = field(default_factory=list)


_co_id_counter = 0


def _next_co_id() -> str:
    global _co_id_counter
    _co_id_counter += 1
    return f"co_{_co_id_counter}"


def listen_obj(
    name: str,
    dpt: DPT,
    supported: list[DPT] | None = None,
    co_id: str | None = None,
    **flag_overrides: bool,
) -> ComObject:
    flags = ComObjectFlags.default_input()
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(co_id or _next_co_id(), name, dpt, flags, supported_dpts=supported or [])


def send_obj(
    name: str,
    dpt: DPT,
    supported: list[DPT] | None = None,
    co_id: str | None = None,
    **flag_overrides: bool,
) -> ComObject:
    flags = ComObjectFlags.default_output()
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(co_id or _next_co_id(), name, dpt, flags, supported_dpts=supported or [])


def bidirectional_obj(name: str, dpt: DPT, co_id: str | None = None, **flag_overrides: bool) -> ComObject:
    flags = ComObjectFlags(communication=True, read=True, write=True, transmit=True)
    for key, value in flag_overrides.items():
        setattr(flags, key, value)
    return ComObject(co_id or _next_co_id(), name, dpt, flags)


FLAG_LABELS = [
    ("communication", "C", "Communication"),
    ("read", "R", "Read"),
    ("write", "W", "Write"),
    ("transmit", "T", "Transmit"),
    ("update", "U", "Update"),
    ("read_on_init", "I", "Read on Init"),
]


def flag_diff_letters(flags: ComObjectFlags, direction: PinDir) -> list[tuple[str, bool]]:
    default = default_flags_for(direction)
    diffs = []
    for attr, letter, _ in FLAG_LABELS:
        if getattr(flags, attr) != getattr(default, attr):
            diffs.append((letter, getattr(flags, attr)))
    return diffs


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
class Parameter:
    id: str
    name: str
    text: str
    value: str
    param_type: ParamType | None = None


@dataclass
class DeviceTemplate:
    name: str
    com_objects: list[ComObject]
    config: DeviceConfig
    parameters: list[Parameter] = field(default_factory=list)


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
    app: DeviceApplication | None = None
    _param_values: dict[str, str] = field(default_factory=dict)
    _cached_visible_params: list[Parameter] = field(default_factory=list)
    _params_dirty: bool = True
    _cached_visible_cos: list[ComObject] = field(default_factory=list)
    _cos_dirty: bool = True

    def __post_init__(self) -> None:
        if not self.com_objects:
            self.com_objects = copy.deepcopy(self.template.com_objects)
        if self.app is not None:
            for p in self.app.parameters:
                self._param_values[p.id] = p.value
        else:
            for p in self.template.parameters:
                self._param_values[p.id] = p.value

    @property
    def rows(self) -> list[PinRow]:
        return generate_rows(self.get_visible_com_objects())

    def get_visible_com_objects(self) -> list[ComObject]:
        if not self._cos_dirty:
            return self._cached_visible_cos
        if self.app is None:
            self._cached_visible_cos = self.com_objects
        else:
            visible_ids = {co.id for co in self.app.visible_com_objects(self._param_values)}
            self._cached_visible_cos = [co for co in self.com_objects if co.id in visible_ids]
        self._cos_dirty = False
        return self._cached_visible_cos

    def get_visible_parameters(self) -> list[Parameter]:
        if not self._params_dirty:
            return self._cached_visible_params
        if self.app is None:
            self._cached_visible_params = self.template.parameters
        else:
            visible_knx = self.app.visible_parameters(self._param_values)
            self._cached_visible_params = [
                Parameter(
                    id=p.id,
                    name=p.name,
                    text=p.text,
                    value=self._param_values.get(p.id, p.value),
                    param_type=p.param_type,
                )
                for p in visible_knx
            ]
        self._params_dirty = False
        return self._cached_visible_params

    def would_hide_com_objects(self, param_id: str, value: str) -> list[ComObject]:
        if self.app is None:
            return []
        test_values = dict(self._param_values)
        test_values[param_id] = value
        new_visible_ids = {co.id for co in self.app.visible_com_objects(test_values)}
        current_visible = self.get_visible_com_objects()
        return [co for co in current_visible if co.id not in new_visible_ids]

    def set_param_value(self, param_id: str, value: str) -> None:
        if self._param_values.get(param_id) != value:
            self._param_values[param_id] = value
            self._params_dirty = True
            self._cos_dirty = True
            for p in self._cached_visible_params:
                if p.id == param_id:
                    p.value = value
                    break


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
        self._next_pin_id: int = 100000
        self._pin_ids: dict[tuple[int, int, str], int] = {}
        self._pin_dpt: dict[int, DPT] = {}
        self._pin_dir: dict[int, PinDir] = {}
        self._devices: list[Device] = []
        self._connected: bool = False
        self._controller_ip: str = "192.168.1.1"
        self._telegrams: list[Telegram] = []
        self._selected_telegrams: set[int] = set()
        self._last_selected_telegram: int = -1
        self._drag_source_pin: int | None = None
        self._open_file_dialog: pfd.open_file | None = None
        self._archive_candidates: list[DeviceApplication] = []
        self._archive_path: str | None = None
        self._archive_load_error: str | None = None
        self._show_archive_popup: bool = False
        self._dpt_popup_target: ComObject | None = None
        self._dpt_popup_request: ComObject | None = None
        self._enum_popup_target: Parameter | None = None
        self._enum_popup_request: Parameter | None = None
        self._enum_popup_device: Device | None = None
        self._pending_param_change: tuple[Device, str, str] | None = None
        self._pending_hidden_cos: list[ComObject] = []
        self._pending_removed_links: list[tuple[int, int, int]] = []
        self._show_link_warning: bool = False
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

    def _render_enum_popup(self) -> None:
        if self._enum_popup_request is not None:
            self._enum_popup_target = self._enum_popup_request
            self._enum_popup_request = None
            imgui.open_popup("##EnumPopup")
        if imgui.begin_popup("##EnumPopup"):
            target = self._enum_popup_target
            device = self._enum_popup_device
            if target is not None and target.param_type is not None and device is not None:
                for opt in target.param_type.options:
                    selected = opt.value == target.value
                    if imgui.menu_item(opt.text, "", selected)[0]:
                        self._try_set_param_value(device, target.id, opt.value)
            imgui.end_popup()
        else:
            self._enum_popup_target = None
            self._enum_popup_device = None

    def _render_link_warning_popup(self) -> None:
        if self._show_link_warning:
            imgui.open_popup("##LinkWarning")
            self._show_link_warning = False
        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing, imgui.ImVec2(0.5, 0.5))
        if imgui.begin_popup_modal("##LinkWarning", None, imgui.WindowFlags_.always_auto_resize)[0]:
            imgui.text("This change will hide the following communication objects:")
            imgui.spacing()
            for co in self._pending_hidden_cos:
                imgui.bullet_text(co.name)
            imgui.spacing()
            imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
            imgui.text(f"{len(self._pending_removed_links)} link(s) will be removed.")
            imgui.pop_style_color()
            imgui.spacing()
            imgui.separator()
            imgui.spacing()
            if imgui.button("Remove Links", imgui.ImVec2(120, 0)):
                if self._pending_param_change:
                    device, param_id, value = self._pending_param_change
                    for link in self._pending_removed_links:
                        if link in self._links:
                            self._links.remove(link)
                    device.set_param_value(param_id, value)
                self._pending_param_change = None
                self._pending_hidden_cos = []
                self._pending_removed_links = []
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button("Cancel", imgui.ImVec2(120, 0)):
                self._pending_param_change = None
                self._pending_hidden_cos = []
                self._pending_removed_links = []
                imgui.close_current_popup()
            imgui.end_popup()

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

    def _get_pin_id(self, device_id: int, co_index: int, direction: str) -> int:
        key = (device_id, co_index, direction)
        if key not in self._pin_ids:
            self._pin_ids[key] = self._next_pin_id
            self._next_pin_id += 1
        return self._pin_ids[key]

    def _render_node_pins(self, device: "Device", layout: NodeLayout) -> None:
        co_indices = {id(co): idx for idx, co in enumerate(device.com_objects)}
        for row in device.rows:
            if row.left and com_object_has_input(row.left):
                pin_id = self._get_pin_id(device.node_id, co_indices[id(row.left)], "in")
                self._render_input_pin(pin_id, row.left, layout)
            else:
                imgui.dummy(imgui.ImVec2(layout.in_total_w, PIN_HEIGHT))
            imgui.same_line(spacing=layout.mid_spacing)
            if row.right and com_object_has_output(row.right):
                pin_id = self._get_pin_id(device.node_id, co_indices[id(row.right)], "out")
                self._render_output_pin(pin_id, row.right, layout)
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
            locked_attr = f"{attr}_locked"
            is_locked = getattr(com_object.flags, locked_attr, False) if attr != "communication" else False
            if is_locked:
                imgui.begin_disabled()
            changed, new_value = imgui.checkbox(f"##{row_id}_{attr}", current)
            if changed and not is_locked:
                setattr(com_object.flags, attr, new_value)
            if is_locked:
                imgui.end_disabled()
            if imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_disabled):
                tooltip = f"{full_name} (locked)" if is_locked else full_name
                imgui.set_tooltip(tooltip)

    def _render_node_com_objects(self, device: "Device") -> None:
        flags = imgui.TableFlags_.borders_inner | imgui.TableFlags_.sizing_fixed_fit
        if not imgui.begin_table(f"##com_objs_{device.node_id}", 1 + len(FLAG_LABELS), flags):
            return
        imgui.table_setup_column("Name")
        for _attr, letter, _name in FLAG_LABELS:
            imgui.table_setup_column(letter)
        imgui.table_headers_row()
        for i, com_obj in enumerate(device.get_visible_com_objects()):
            self._render_com_object_row(com_obj, f"{device.node_id}_{com_obj.id}")
        imgui.end_table()

    def _group_parameters(self, params: list[Parameter]) -> dict[str, list[Parameter]]:
        groups: dict[str, list[Parameter]] = {}
        for param in params:
            text = param.text if param.text else param.name
            prefix = text.split(" - ")[0].strip() if " - " in text else "General"
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(param)
        return groups

    def _try_set_param_value(self, device: Device, param_id: str, value: str) -> None:
        hidden_cos = device.would_hide_com_objects(param_id, value)
        if not hidden_cos:
            device.set_param_value(param_id, value)
            return
        affected_links = self._find_links_for_com_objects(device, hidden_cos)
        if not affected_links:
            device.set_param_value(param_id, value)
            return
        self._pending_param_change = (device, param_id, value)
        self._pending_hidden_cos = hidden_cos
        self._pending_removed_links = affected_links
        self._show_link_warning = True

    def _render_param_widget(self, param: Parameter, device: "Device") -> None:
        pt = param.param_type
        if pt is None:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._try_set_param_value(device, param.id, new_value)
            return

        if pt.kind == ParamTypeKind.ENUM:
            current_idx = 0
            for i, opt in enumerate(pt.options):
                if opt.value == param.value:
                    current_idx = i
                    break
            preview = pt.options[current_idx].text if pt.options else param.value
            if imgui.button(f"{preview}##{param.id}", imgui.ImVec2(-1, 0)):
                self._enum_popup_request = param
                self._enum_popup_device = device
        elif pt.kind == ParamTypeKind.CHECKBOX:
            checked = param.value == "1"
            changed, new_checked = imgui.checkbox(f"##{param.id}", checked)
            if changed:
                self._try_set_param_value(device, param.id, "1" if new_checked else "0")
        elif pt.kind == ParamTypeKind.NUMBER:
            try:
                int_val = int(param.value)
            except ValueError:
                int_val = pt.min_value or 0
            min_v = pt.min_value if pt.min_value is not None else 0
            max_v = pt.max_value if pt.max_value is not None else 65535
            changed, new_val = imgui.drag_int(f"##{param.id}", int_val, 1.0, min_v, max_v)
            if changed:
                self._try_set_param_value(device, param.id, str(new_val))
        elif pt.kind == ParamTypeKind.TIME:
            try:
                int_val = int(param.value)
            except ValueError:
                int_val = pt.min_value or 0
            min_v = pt.min_value if pt.min_value is not None else 0
            max_v = pt.max_value if pt.max_value is not None else 86400
            changed, new_val = imgui.drag_int(f"##{param.id}", int_val, 1.0, min_v, max_v)
            if changed:
                self._try_set_param_value(device, param.id, str(new_val))
        elif pt.kind == ParamTypeKind.TEXT:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._try_set_param_value(device, param.id, new_value)
        elif pt.kind == ParamTypeKind.PICTURE:
            imgui.text_disabled("(image)")
        else:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._try_set_param_value(device, param.id, new_value)

    def _render_node_parameters(self, device: "Device") -> None:
        params = device.get_visible_parameters()
        if not params:
            return
        groups = self._group_parameters(params)
        for group_name, group_params in sorted(groups.items()):
            group_label = f"{group_name}##{device.node_id}_{group_name}"
            is_open = imgui.tree_node(group_label)
            imgui.same_line()
            imgui.text_disabled(f"({len(group_params)})")
            if is_open:
                table_flags = imgui.TableFlags_.no_saved_settings
                if imgui.begin_table(f"##params_{device.node_id}_{group_name}", 2, table_flags):
                    imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch)
                    imgui.table_setup_column("Value", imgui.TableColumnFlags_.width_fixed, 120)
                    for param in group_params:
                        imgui.table_next_row()
                        imgui.table_set_column_index(0)
                        display_text = param.text if param.text else param.name
                        imgui.text(display_text)
                        imgui.table_set_column_index(1)
                        imgui.set_next_item_width(-1)
                        self._render_param_widget(param, device)
                    imgui.end_table()
                imgui.tree_pop()

    def _render_node_settings(self, device: "Device", width: float) -> None:
        config = device.template.config
        if imgui.tree_node(f"Manufacturer##{device.node_id}"):
            self._render_label_value("Manufacturer", config.manufacturer)
            self._render_label_value("Application", config.application)
            self._render_label_value("Hardware", config.hardware)
            self._render_label_value("Firmware", config.firmware)
            imgui.tree_pop()
        params = device.get_visible_parameters()
        if params:
            is_open = imgui.tree_node(f"Parameters##{device.node_id}")
            imgui.same_line()
            imgui.text_disabled(f"({len(params)})")
            if is_open:
                self._render_node_parameters(device)
                imgui.tree_pop()
        if imgui.tree_node(f"Com Flags##{device.node_id}"):
            self._render_node_com_objects(device)
            imgui.tree_pop()

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

    def _find_links_for_com_objects(self, device: Device, cos: list[ComObject]) -> list[tuple[int, int, int]]:
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
        for link in self._links:
            link_id, start, end = link
            if start in pin_ids or end in pin_ids:
                affected.append(link)
        return affected

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
        print(f"[knxprod] parsing {path}")
        try:
            self._archive_candidates = parse_archive(path)
            print(f"[knxprod] parsed {len(self._archive_candidates)} candidate(s)")
            for c in self._archive_candidates:
                print(f"[knxprod]   {c.name}: {len(c.com_objects)} com objects, {len(c.parameters)} parameters")
        except ArchiveError as e:
            print(f"[knxprod] archive error: {e}")
            self._archive_load_error = str(e)
        except (OSError, ValueError) as e:
            print(f"[knxprod] error: {type(e).__name__}: {e}")
            self._archive_load_error = f"{type(e).__name__}: {e}"
        self._show_archive_popup = True

    def _add_candidate_as_device(self, app: DeviceApplication) -> None:
        print(f"[knxprod] adding {app.name} ({len(app.com_objects)} com objects)")
        template = self._app_to_template(app)
        next_id = max((d.node_id for d in self._devices), default=0) + 1
        self._devices.append(
            Device(
                node_id=next_id,
                name=app.name,
                template=template,
                address="",
                app=app,
            )
        )
        print(f"[knxprod] device added; total devices: {len(self._devices)}")

    def _app_to_template(self, app: DeviceApplication) -> DeviceTemplate:
        com_objects: list[ComObject] = []
        for co in app.com_objects:
            flags = ComObjectFlags(
                communication=co.flags.communication,
                read=co.flags.read,
                write=co.flags.write,
                transmit=co.flags.transmit,
                update=co.flags.update,
                read_on_init=co.flags.read_on_init,
                read_locked=co.flags.read_locked,
                write_locked=co.flags.write_locked,
                transmit_locked=co.flags.transmit_locked,
                update_locked=co.flags.update_locked,
                read_on_init_locked=co.flags.read_on_init_locked,
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
                    id=co.id,
                    name=co.name,
                    dpt=primary,
                    flags=flags,
                    supported_dpts=unique_supported,
                )
            )
        visible_params = app.visible_parameters()
        parameters = [
            Parameter(
                id=p.id,
                name=p.name,
                text=p.text,
                value=p.value,
                param_type=p.param_type,
            )
            for p in visible_params
        ]
        return DeviceTemplate(
            name=app.name,
            com_objects=com_objects,
            config=DeviceConfig(
                manufacturer=app.manufacturer_id,
                application=app.application_id,
                hardware="",
                firmware="",
            ),
            parameters=parameters,
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
                    imgui.text_disabled(f"  ({len(candidate.com_objects)} com objects)")
                    imgui.same_line()
                    if imgui.small_button(f"Add##{i}"):
                        self._add_candidate_as_device(candidate)
                        imgui.close_current_popup()
            imgui.spacing()
            if imgui.button("Close", imgui.ImVec2(120, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

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

    def gui_status_bar(self) -> None:
        draw_list = imgui.get_window_draw_list()
        cursor = imgui.get_cursor_screen_pos()
        text_height = imgui.get_text_line_height()
        center = imgui.ImVec2(cursor.x + 5, cursor.y + text_height / 2)
        if self._connected:
            pulse = 0.5 + 0.5 * math.sin(imgui.get_time() * 3.0)
            alpha = 0.4 + 0.6 * pulse
            draw_list.add_circle_filled(center, 4, color_u32(0.2, 0.8, 0.3, alpha))
            draw_list.add_circle_filled(center, 4 + pulse * 3, color_u32(0.2, 0.8, 0.3, 0.15 * (1 - pulse)))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text(f"Connected: {self._controller_ip}")
        else:
            draw_list.add_circle_filled(center, 4, color_u32(0.5, 0.5, 0.5, 1.0))
            imgui.dummy(imgui.ImVec2(12, 0))
            imgui.same_line()
            imgui.text_disabled("Disconnected")
        imgui.same_line()
        imgui.text(f"| Devices: {len(self._devices)} | Links: {len(self._links)}")

    def gui_menu(self) -> None:
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
                hello_imgui.get_runner_params().app_shall_exit = True
            imgui.end_menu()

        if imgui.begin_menu("Edit"):
            if imgui.menu_item("Undo", "Ctrl+Z", False)[0]:
                pass
            if imgui.menu_item("Redo", "Ctrl+Y", False)[0]:
                pass
            imgui.end_menu()

        if imgui.begin_menu("Connection"):
            if self._connected:
                imgui.text(f"Connected to {self._controller_ip}")
                if imgui.menu_item("Disconnect", "", False)[0]:
                    self._connected = False
            else:
                imgui.set_next_item_width(180)
                _, self._controller_ip = imgui.input_text("IP", self._controller_ip)
                if imgui.menu_item("Connect", "", False)[0]:
                    self._connected = True
            imgui.end_menu()

        self._poll_open_file_dialog()

    def gui_devices(self) -> None:
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
                                ed.set_current_editor(self._editor_context)
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
                        ed.set_current_editor(self._editor_context)
                        ed.select_node(ed.NodeId(device.node_id), False)
                        ed.navigate_to_selection(False, 0.3)
                imgui.tree_pop()

    def gui_node_editor(self) -> None:
        if not self._editor_context:
            return

        ed.set_current_editor(self._editor_context)
        ed.begin("##NodeEditorCanvas", imgui.ImVec2(0, 0))

        for device in self._devices:
            self._render_device_node(device)

        self._render_links()
        self._handle_link_creation()
        self._handle_link_deletion()

        ed.end()

        self._render_archive_popup()
        self._render_dpt_popup()
        self._render_enum_popup()
        self._render_link_warning_popup()

    def gui_telegrams(self) -> None:
        self._render_telegrams_header()
        self._handle_telegrams_shortcuts()
        self._render_telegrams_table()


def create_docking_splits() -> list[hello_imgui.DockingSplit]:
    split_left = hello_imgui.DockingSplit()
    split_left.initial_dock = "MainDockSpace"
    split_left.new_dock = "LeftSpace"
    split_left.direction = imgui.Dir.left
    split_left.ratio = 0.2

    split_bottom = hello_imgui.DockingSplit()
    split_bottom.initial_dock = "MainDockSpace"
    split_bottom.new_dock = "BottomSpace"
    split_bottom.direction = imgui.Dir.down
    split_bottom.ratio = 0.25

    return [split_left, split_bottom]


def create_dockable_windows(app: "KnxGuiApp") -> list[hello_imgui.DockableWindow]:
    devices_window = hello_imgui.DockableWindow()
    devices_window.label = "Devices"
    devices_window.dock_space_name = "LeftSpace"
    devices_window.gui_function = app.gui_devices

    editor_window = hello_imgui.DockableWindow()
    editor_window.label = "Node Editor"
    editor_window.dock_space_name = "MainDockSpace"
    editor_window.gui_function = app.gui_node_editor

    telegrams_window = hello_imgui.DockableWindow()
    telegrams_window.label = "Telegrams"
    telegrams_window.dock_space_name = "BottomSpace"
    telegrams_window.gui_function = app.gui_telegrams

    return [devices_window, editor_window, telegrams_window]


def main() -> None:
    app = KnxGuiApp()

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = "XKNX Toolkit"
    runner_params.app_window_params.window_geometry.size = (1280, 720)
    runner_params.app_window_params.restore_previous_geometry = True

    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    runner_params.imgui_window_params.enable_viewports = True

    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.imgui_window_params.show_menu_app = False
    runner_params.imgui_window_params.show_menu_view = True
    runner_params.callbacks.show_menus = app.gui_menu

    runner_params.imgui_window_params.show_status_bar = True
    runner_params.callbacks.show_status = app.gui_status_bar

    runner_params.docking_params.docking_splits = create_docking_splits()
    runner_params.docking_params.dockable_windows = create_dockable_windows(app)

    runner_params.callbacks.post_init = app.setup
    runner_params.callbacks.before_exit = app.shutdown

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
