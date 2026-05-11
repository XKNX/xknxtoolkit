from dataclasses import dataclass
from enum import Enum

from imgui_bundle import imgui


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

DPT_SWITCH_CONTROL = DPT(2, 1, "Switch Control", "switch ctrl")

DPT_DIMMING = DPT(3, 7, "Dimming", "dim")
DPT_BLINDS = DPT(3, 8, "Blinds", "blinds")

DPT_PERCENT = DPT(5, 1, "Percent", "%")
DPT_ANGLE = DPT(5, 3, "Angle", "°")
DPT_PERCENT_U8 = DPT(5, 4, "Percent (uint8)", "%u8")
DPT_DECIMAL_FACTOR = DPT(5, 5, "Decimal Factor", "factor")
DPT_TARIFF = DPT(5, 6, "Tariff", "tariff")
DPT_VALUE_1_UCOUNT = DPT(5, 10, "Counter (uint8)", "count")

DPT_VALUE_1_COUNT = DPT(6, 10, "Counter (int8)", "i8")

DPT_COLOR_TEMP_KELVIN = DPT(7, 600, "Color Temperature", "K")

DPT_TIME_OF_DAY = DPT(10, 1, "Time of Day", "time")
DPT_DATE = DPT(11, 1, "Date", "date")
DPT_DATE_TIME = DPT(19, 1, "Date/Time", "datetime")

DPT_STRING_LATIN1 = DPT(16, 1, "String (ISO 8859-1)", "string")

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

DPT_SCENE = DPT(17, 1, "Scene", "scene")
DPT_SCENE_CONTROL = DPT(18, 1, "Scene Control", "scene ctrl")

DPT_RGB = DPT(232, 600, "RGB", "rgb")
DPT_BRIGHTNESS_COLOR_TEMP_TRANSITION = DPT(
    249, 600, "Brightness/Color Temp/Transition", "bri/K/t"
)


KNOWN_DPTS: dict[tuple[int, int], DPT] = {
    (d.major, d.minor): d
    for d in [
        DPT_SWITCH,
        DPT_BOOL,
        DPT_ENABLE,
        DPT_RAMP,
        DPT_ALARM,
        DPT_BINARY_VALUE,
        DPT_STEP,
        DPT_UP_DOWN,
        DPT_OPEN_CLOSE,
        DPT_STOP,
        DPT_STATE,
        DPT_INVERT,
        DPT_DIM_SEND_STYLE,
        DPT_INPUT_SOURCE,
        DPT_RESET,
        DPT_ACK,
        DPT_TRIGGER,
        DPT_OCCUPANCY,
        DPT_WINDOW_DOOR,
        DPT_LOGICAL_FUNCTION,
        DPT_SCENE_AB,
        DPT_SHUTTER_BLINDS_MODE,
        DPT_DAY_NIGHT,
        DPT_HEAT_COOL,
        DPT_SWITCH_CONTROL,
        DPT_DIMMING,
        DPT_BLINDS,
        DPT_PERCENT,
        DPT_ANGLE,
        DPT_PERCENT_U8,
        DPT_DECIMAL_FACTOR,
        DPT_TARIFF,
        DPT_VALUE_1_UCOUNT,
        DPT_VALUE_1_COUNT,
        DPT_COLOR_TEMP_KELVIN,
        DPT_TIME_OF_DAY,
        DPT_DATE,
        DPT_DATE_TIME,
        DPT_STRING_LATIN1,
        DPT_TEMPERATURE,
        DPT_TEMPERATURE_DELTA,
        DPT_LUX,
        DPT_WIND_SPEED,
        DPT_PRESSURE,
        DPT_HUMIDITY,
        DPT_PARTS_PER_MILLION,
        DPT_TIME_DIFF,
        DPT_VOLT,
        DPT_CURRENT,
        DPT_POWER_DENSITY,
        DPT_KELVIN,
        DPT_POWER,
        DPT_SCENE,
        DPT_SCENE_CONTROL,
        DPT_RGB,
        DPT_BRIGHTNESS_COLOR_TEMP_TRANSITION,
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
