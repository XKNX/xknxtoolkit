from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from imgui_bundle import imgui

from knx_gui.dpt import DPT
from knx_gui.knxprod import DeviceApplication, ParamType


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
    def default_input(cls) -> ComObjectFlags:
        return cls(communication=True, write=True)

    @classmethod
    def default_output(cls) -> ComObjectFlags:
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
    left: ComObject | None = None
    right: ComObject | None = None


def generate_rows(com_objects: list[ComObject]) -> list[PinRow]:
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


def color_u32(r: float, g: float, b: float, a: float = 1.0) -> int:
    return imgui.get_color_u32(imgui.ImVec4(r, g, b, a))


def color_from_vec4(c: imgui.ImVec4) -> int:
    return imgui.get_color_u32(c)
