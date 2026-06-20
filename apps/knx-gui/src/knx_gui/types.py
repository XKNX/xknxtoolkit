from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from imgui_bundle import imgui
from xknx.telegram import Telegram as XknxTelegram

from knx_gui.dpt import DPT
from xknxmono.product import Application

if TYPE_CHECKING:
    from xknxmono.models.intermediate.com_object_instance_ref_t import (
        ComObjectInstanceRef,
    )
    from xknxmono.models.intermediate.module_instance_t import ModuleInstance
    from xknxmono.models.intermediate.parameter_instance_ref_t import (
        ParameterInstanceRef,
    )
    from xknxmono.product.parser_v2.dynamic import DynamicUI
    from xknxmono.product.parser_v2.ui import UiComObject, UiNode


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
    supported_dpts: list[DPT] = field(default_factory=list[DPT])
    db_id: int | None = None


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
    return ComObject(
        co_id or _next_co_id(), name, dpt, flags, supported_dpts=supported or []
    )


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
    return ComObject(
        co_id or _next_co_id(), name, dpt, flags, supported_dpts=supported or []
    )


def bidirectional_obj(
    name: str, dpt: DPT, co_id: str | None = None, **flag_overrides: bool
) -> ComObject:
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


def flag_diff_letters(
    flags: ComObjectFlags, direction: PinDir
) -> list[tuple[str, bool]]:
    default = default_flags_for(direction)
    diffs: list[tuple[str, bool]] = []
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


def _collect_ui_com_objects(nodes: list[UiNode] | tuple[UiNode, ...]) -> list[UiComObject]:
    from xknxmono.product.parser_v2.ui import UiComObject as _UiComObject
    from xknxmono.product.parser_v2.ui import UiParameterBlock as _UiParameterBlock
    from xknxmono.product.parser_v2.ui import UiTab as _UiTab

    result: list[UiComObject] = []
    for node in nodes:
        if isinstance(node, _UiComObject):
            result.append(node)
        elif isinstance(node, (_UiTab, _UiParameterBlock)):
            result.extend(_collect_ui_com_objects(node.children))
    return result


@dataclass
class Device:
    node_id: int
    name: str
    app: Application
    individual_address: str
    com_objects: list[ComObject] = field(default_factory=list[ComObject])
    parameter_instance_refs: list[ParameterInstanceRef] = field(default_factory=list, repr=False, compare=False)
    module_instances: list[ModuleInstance] = field(default_factory=list, repr=False, compare=False)
    com_object_instance_refs: list[ComObjectInstanceRef] = field(default_factory=list, repr=False, compare=False)
    _dynamic_ui: DynamicUI | None = field(default=None, repr=False, compare=False, init=False)
    _cached_visible_cos: list[ComObject] | None = field(default=None, repr=False, compare=False, init=False)
    _cached_rows: list[PinRow] | None = field(default=None, repr=False, compare=False, init=False)

    def __post_init__(self) -> None:
        if self.app.program.dynamic is not None:
            from xknxmono.product.parser_v2.dynamic import DynamicUI as _DynamicUI
            self._dynamic_ui = _DynamicUI(
                self.app.program,
                parameter_instance_refs=self.parameter_instance_refs or None,
                module_instances=self.module_instances or None,
                com_object_instance_refs=self.com_object_instance_refs or None,
            )
        if not self.com_objects:
            self.com_objects = self._create_com_objects_from_app()

    def _create_com_objects_from_app(self) -> list[ComObject]:
        if self._dynamic_ui is None:
            return []
        from knx_gui.dpt import DPT_UNKNOWN, lookup_or_make_dpt

        ui_cos = _collect_ui_com_objects(self._dynamic_ui.ui())
        result: list[ComObject] = []
        for ui_co in ui_cos:
            supported = [lookup_or_make_dpt(code) for code in ui_co.dpt_codes]
            seen: set[tuple[int, int]] = set()
            unique_supported: list[DPT] = []
            for dpt in supported:
                key = (dpt.major, dpt.minor)
                if key not in seen:
                    seen.add(key)
                    unique_supported.append(dpt)
            primary = unique_supported[0] if unique_supported else DPT_UNKNOWN
            result.append(
                ComObject(
                    id=ui_co.ref_id,
                    name=ui_co.name,
                    dpt=primary,
                    flags=ComObjectFlags(
                        communication=ui_co.communication,
                        read=ui_co.read,
                        write=ui_co.write,
                        transmit=ui_co.transmit,
                        update=ui_co.update,
                        read_on_init=ui_co.read_on_init,
                        read_locked=ui_co.read_locked,
                        write_locked=ui_co.write_locked,
                        transmit_locked=ui_co.transmit_locked,
                        update_locked=ui_co.update_locked,
                        read_on_init_locked=ui_co.read_on_init_locked,
                    ),
                    supported_dpts=unique_supported,
                )
            )
        return result

    @property
    def rows(self) -> list[PinRow]:
        if self._cached_rows is None:
            self._cached_rows = generate_rows(self.get_visible_com_objects())
        return self._cached_rows

    def get_ui(self) -> list[UiNode]:
        if self._dynamic_ui is None:
            return []
        return self._dynamic_ui.ui()

    def get_visible_com_objects(self) -> list[ComObject]:
        if self._cached_visible_cos is not None:
            return self._cached_visible_cos
        if self._dynamic_ui is None:
            return list(self.com_objects)
        ui_cos = _collect_ui_com_objects(self._dynamic_ui.ui())
        ui_by_id = {co.ref_id: co for co in ui_cos}
        result: list[ComObject] = []
        for co in self.com_objects:
            ui_co = ui_by_id.get(co.id)
            if ui_co is None:
                continue
            co.name = ui_co.name
            co.flags.communication = ui_co.communication
            co.flags.read = ui_co.read
            co.flags.write = ui_co.write
            co.flags.transmit = ui_co.transmit
            co.flags.update = ui_co.update
            co.flags.read_on_init = ui_co.read_on_init
            result.append(co)
        self._cached_visible_cos = result
        return result

    def encode_to_memory(self) -> dict[str, bytes]:
        """Encode current parameter state into {segment_id: bytes} for programming."""
        if self._dynamic_ui is None:
            return {}
        return self._dynamic_ui.encode_to_memory()

    def set_com_obj_instance_ref(self, ref_id: str, coir: ComObjectInstanceRef) -> None:
        if self._dynamic_ui is not None:
            self._dynamic_ui.set_com_obj_instance_ref(ref_id, coir)
            self._cached_visible_cos = None
            self._cached_rows = None

    def set_param_value(self, ref_id: str, value: str) -> None:
        if self._dynamic_ui is not None:
            self._dynamic_ui.set_parameter_ref(ref_id, value)
            self._cached_visible_cos = None
            self._cached_rows = None

    def get_module_instances(self) -> list[tuple[str, str]]:
        """Return ``(instance_id, ref_id)`` for every top-level module instance."""
        if self._dynamic_ui is None:
            return []
        return self._dynamic_ui.get_module_instances()

    def find_com_object(self, co_id: str) -> ComObject | None:
        for co in self.com_objects:
            if co.id == co_id:
                return co
        return None


@dataclass
class TelegramRecord:
    telegram: XknxTelegram
    timestamp: datetime

    @property
    def source(self) -> str:
        return str(self.telegram.source_address)

    @property
    def destination(self) -> str:
        return str(self.telegram.destination_address)

    @property
    def service(self) -> str:
        if self.telegram.payload is None:
            return ""
        return type(self.telegram.payload).__name__

    @property
    def tpci(self) -> str:
        tpci = self.telegram.tpci
        if not tpci:
            return ""
        return type(tpci).__name__

    @property
    def dpt(self) -> str:
        if self.telegram.decoded_data is not None:
            return self.telegram.decoded_data.transcoder.__name__
        return ""

    @property
    def value(self) -> str:
        if self.telegram.decoded_data is not None:
            return str(self.telegram.decoded_data.value)
        payload = self.telegram.payload
        if payload is None:
            return ""
        return self._format_payload_value(payload)

    def _format_payload_value(self, payload: Any) -> str:
        name = type(payload).__name__

        if name == "DeviceDescriptorRead":
            return f"Desc{payload.descriptor}"
        if name == "DeviceDescriptorResponse":
            return f"Desc{payload.descriptor}: {payload.value:#06x}"
        if name == "IndividualAddressWrite":
            return str(payload.address)
        if name == "IndividualAddressSerialRead":
            return payload.serial.hex()
        if name == "IndividualAddressSerialResponse":
            return f"{payload.serial.hex()} -> {payload.address}"
        if name == "IndividualAddressSerialWrite":
            return f"{payload.serial.hex()} -> {payload.address}"
        if name == "MemoryRead":
            return f"@{payload.address:#06x} x{payload.count}"
        if name == "MemoryResponse":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "MemoryWrite":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "MemoryExtendedRead":
            return f"@{payload.address:#08x} x{payload.count}"
        if name == "MemoryExtendedReadResponse":
            return f"@{payload.address:#08x}: {payload.data.hex()} (rc={payload.return_code})"
        if name == "MemoryExtendedWrite":
            return f"@{payload.address:#08x}: {payload.data.hex()}"
        if name == "MemoryExtendedWriteResponse":
            return f"@{payload.address:#08x} (rc={payload.return_code})"
        if name == "UserMemoryRead":
            return f"@{payload.address:#06x} x{payload.count}"
        if name == "UserMemoryResponse":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "UserMemoryWrite":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "PropertyValueRead":
            return f"Obj{payload.object_index}/P{payload.property_id}[{payload.start_index}]"
        if name == "PropertyValueResponse":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "PropertyValueWrite":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "PropertyDescriptionRead":
            return f"Obj{payload.object_index}/P{payload.property_id}"
        if name == "PropertyDescriptionResponse":
            return f"Obj{payload.object_index}/P{payload.property_id} type={payload.type_:#x} max={payload.max_count}"
        if name == "FunctionPropertyCommand":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "FunctionPropertyStateRead":
            return f"Obj{payload.object_index}/P{payload.property_id}"
        if name == "FunctionPropertyStateResponse":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()} (rc={payload.return_code})"
        if name == "ADCRead":
            return f"Ch{payload.channel} x{payload.count}"
        if name == "ADCResponse":
            return f"Ch{payload.channel}: {payload.value}"
        if name == "AuthorizeRequest":
            return f"key={payload.key:#010x}"
        if name == "AuthorizeResponse":
            return f"level={payload.level}"
        if name == "UserManufacturerInfoRead":
            return ""
        if name == "UserManufacturerInfoResponse":
            return f"MfId={payload.manufacturer_id:#06x} {payload.data.hex()}"
        if name in ("IndividualAddressRead", "IndividualAddressResponse", "Restart"):
            return ""

        if hasattr(payload, "value"):
            payload_value = payload.value
            if payload_value is not None and hasattr(payload_value, "value"):
                return str(payload_value.value)
            return str(payload_value) if payload_value is not None else ""
        return ""

    @property
    def timestamp_str(self) -> str:
        return self.timestamp.strftime("%H:%M:%S")


def color_u32(r: float, g: float, b: float, a: float = 1.0) -> int:
    return imgui.get_color_u32(imgui.ImVec4(r, g, b, a))


def color_from_vec4(c: imgui.ImVec4) -> int:
    return imgui.get_color_u32(c)
