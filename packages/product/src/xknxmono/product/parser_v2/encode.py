from __future__ import annotations

import struct
from typing import NamedTuple

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t_parameters_parameter import (
    ApplicationProgramStaticParametersParameter,
)
from xknxmono.models.intermediate.application_program_static_t_parameters_union import (
    ApplicationProgramStaticParametersUnion,
)
from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter
from xknxmono.models.intermediate.memory_union_t import MemoryUnion
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter import (
    ModuleDefStaticParametersParameter,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter_memory import (
    ModuleDefStaticParametersParameterMemory,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter_property import (
    ModuleDefStaticParametersParameterProperty,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_union import (
    ModuleDefStaticParametersUnion,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_union_memory import (
    ModuleDefStaticParametersUnionMemory,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_union_property import (
    ModuleDefStaticParametersUnionProperty,
)
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg
from xknxmono.models.intermediate.parameter_type_t_type_float import (
    ParameterTypeTypeFloat,
)
from xknxmono.models.intermediate.parameter_type_t_type_float_encoding import (
    ParameterTypeTypeFloatEncoding,
)
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_restriction import (
    ParameterTypeTypeRestriction,
)
from xknxmono.models.intermediate.parameter_type_t_type_text import (
    ParameterTypeTypeText,
)
from xknxmono.models.intermediate.property_parameter_t import PropertyParameter
from xknxmono.models.intermediate.property_union_t import PropertyUnion
from xknxmono.models.intermediate.union_parameter_t import UnionParameter

from .application_indexer import ApplicationIndexer
from .state import GlobalState, ModuleState


class MemWrite(NamedTuple):
    seg_id: str
    offset: int
    bit_offset: int
    param_id: str
    parameter_type: str
    value: str


class PropWrite(NamedTuple):
    object_index: int | None
    property_id: int
    occurrence: int
    offset: int
    bit_offset: int
    param_id: str
    parameter_type: str
    value: str


class Writes:
    __slots__ = ("mem", "prop")

    def __init__(self) -> None:
        self.mem: list[MemWrite] = []
        self.prop: list[PropWrite] = []


PropertyKey = tuple[int | None, int, int]  # (object_index, property_id, occurrence)


def _write_bits(
    buf: bytearray, offset: int, bit_offset: int, size_in_bit: int, value: int
) -> None:
    """Write value into buf at byte offset + bit_offset (0 = MSB of byte), big-endian."""
    start = offset * 8 + bit_offset
    for i in range(size_in_bit):
        pos = start + i
        bit_mask = 1 << (7 - pos % 8)
        if (value >> (size_in_bit - 1 - i)) & 1:
            buf[pos // 8] |= bit_mask
        else:
            buf[pos // 8] &= ~bit_mask


def _encode_value(str_value: str, size_in_bit: int, tc: object) -> int | None:
    if isinstance(tc, (ParameterTypeTypeNumber, ParameterTypeTypeRestriction)):
        try:
            v = int(str_value)
        except (ValueError, TypeError):
            return None
        return v & ((1 << size_in_bit) - 1)

    if isinstance(tc, ParameterTypeTypeFloat):
        try:
            f = float(str_value)
        except (ValueError, TypeError):
            return None
        if tc.encoding == ParameterTypeTypeFloatEncoding.DPT_9:
            mantissa = round(f * 100)
            exp = 0
            while mantissa < -2048 or mantissa > 2047:
                mantissa >>= 1
                exp += 1
            if exp > 15:
                return None
            sign = 1 if mantissa < 0 else 0
            return (sign << 15) | (exp << 11) | (mantissa & 0x7FF)
        if tc.encoding == ParameterTypeTypeFloatEncoding.IEEE_754_SINGLE:
            return struct.unpack(">I", struct.pack(">f", f))[0]
        if tc.encoding == ParameterTypeTypeFloatEncoding.IEEE_754_DOUBLE:
            return struct.unpack(">Q", struct.pack(">d", f))[0]
        return None

    if isinstance(tc, ParameterTypeTypeText):
        encoded = str_value.encode("latin-1", errors="replace")
        n_bytes = size_in_bit // 8
        padded = encoded[:n_bytes].ljust(n_bytes, b"\x00")
        result = 0
        for b in padded:
            result = (result << 8) | b
        return result

    return None


def resolve_param_values(idx: ApplicationIndexer, state: GlobalState) -> dict[str, str]:
    """Build {param_id: state_value} for parameters with an explicit user override in state.

    Does not include static defaults — collect_writes reads those directly from the
    parameter objects as it iterates the static model.
    """
    state_values = dict(state.relative_param_values())
    overrides: dict[str, str] = {}
    for pr_id, pr in idx.parameter_refs.items():
        state_val = state_values.get(pr_id)
        if state_val is None:
            continue
        param = idx.parameters.get(pr.ref_id)
        if param is not None:
            overrides[param.id] = state_val
    return overrides


def _resolve_base(base_id: str | None, ms: ModuleState) -> int | None:
    if base_id is None:
        return 0
    arg = ms.arguments.get(base_id)
    if not isinstance(arg, ModuleNumericArg) or arg.value is None:
        return None
    return arg.value


def _build_instance_overrides(
    ms: ModuleState, idx: ApplicationIndexer
) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for pr_id, value in ms.param_ref_id_to_value.items():
        pr = idx.parameter_refs.get(pr_id)
        if pr is not None:
            param = idx.parameters.get(pr.ref_id)
            if param is not None:
                overrides[param.id] = value
    return overrides


def _pick_union_param(
    parameters: list[UnionParameter],
    overrides: dict[str, str],
    location: str,
) -> tuple[UnionParameter, str] | None:
    active = [up for up in parameters if up.id in overrides]
    assert len(active) <= 1, (
        f"union at {location} has {len(active)} active alternatives: "
        + ", ".join(up.id for up in active)
    )
    if active:
        return active[0], overrides[active[0].id]
    default_up = next((up for up in parameters if up.default_union_parameter), None)
    if default_up is not None:
        return default_up, default_up.value
    return None


def _collect_param(
    item: ApplicationProgramStaticParametersParameter
    | ModuleDefStaticParametersParameter,
    overrides: dict[str, str],
    ms: ModuleState | None,
    out: Writes,
) -> None:
    choice = item.choice
    value = overrides.get(item.id) or item.value
    # base_value on a module parameter shifts the encoded value by an arg-resolved offset.
    if (
        isinstance(item, ModuleDefStaticParametersParameter)
        and item.base_value is not None
        and ms is not None
    ):
        bv = _resolve_base(item.base_value, ms)
        if bv is not None and bv != 0:
            value = str(int(value) + bv)
    # Check subclasses before parents (module types extend their top-level counterparts)
    if isinstance(choice, ModuleDefStaticParametersParameterMemory):
        assert ms is not None
        base = _resolve_base(choice.base_offset, ms)
        if base is not None:
            out.mem.append(
                MemWrite(
                    choice.code_segment,
                    base + choice.offset,
                    choice.bit_offset,
                    item.id,
                    item.parameter_type,
                    value,
                )
            )
    elif isinstance(choice, MemoryParameter):
        out.mem.append(
            MemWrite(
                choice.code_segment,
                choice.offset,
                choice.bit_offset,
                item.id,
                item.parameter_type,
                value,
            )
        )
    elif isinstance(choice, ModuleDefStaticParametersParameterProperty):
        assert ms is not None
        bo = _resolve_base(choice.base_offset, ms)
        bi = _resolve_base(choice.base_index, ms)
        boc = _resolve_base(choice.base_occurrence, ms)
        if bo is not None and bi is not None and boc is not None:
            obj_idx = (choice.object_index or 0) + bi if bi else choice.object_index
            out.prop.append(
                PropWrite(
                    obj_idx,
                    choice.property_id,
                    choice.occurrence + boc,
                    bo + choice.offset,
                    choice.bit_offset,
                    item.id,
                    item.parameter_type,
                    value,
                )
            )
    elif isinstance(choice, PropertyParameter):
        out.prop.append(
            PropWrite(
                choice.object_index,
                choice.property_id,
                choice.occurrence,
                choice.offset,
                choice.bit_offset,
                item.id,
                item.parameter_type,
                value,
            )
        )
    # IoPointParameter and None: skip


def _collect_union(
    item: ApplicationProgramStaticParametersUnion | ModuleDefStaticParametersUnion,
    overrides: dict[str, str],
    ms: ModuleState | None,
    out: Writes,
) -> None:
    choice = item.choice
    if choice is None:
        return
    # Check subclasses before parents (module types extend their top-level counterparts)
    if isinstance(choice, ModuleDefStaticParametersUnionMemory):
        assert ms is not None
        base = _resolve_base(choice.base_offset, ms)
        if base is not None:
            picked = _pick_union_param(
                item.parameter,
                overrides,
                f"{choice.code_segment}+{base + choice.offset}",
            )
            if picked is not None:
                up, value = picked
                out.mem.append(
                    MemWrite(
                        choice.code_segment,
                        base + choice.offset + up.offset,
                        choice.bit_offset + up.bit_offset,
                        up.id,
                        up.parameter_type,
                        value,
                    )
                )
    elif isinstance(choice, MemoryUnion):
        picked = _pick_union_param(
            item.parameter, overrides, f"{choice.code_segment}+{choice.offset}"
        )
        if picked is not None:
            up, value = picked
            out.mem.append(
                MemWrite(
                    choice.code_segment,
                    choice.offset + up.offset,
                    choice.bit_offset + up.bit_offset,
                    up.id,
                    up.parameter_type,
                    value,
                )
            )
    elif isinstance(choice, ModuleDefStaticParametersUnionProperty):
        assert ms is not None
        bo = _resolve_base(choice.base_offset, ms)
        bi = _resolve_base(choice.base_index, ms)
        boc = _resolve_base(choice.base_occurrence, ms)
        if bo is not None and bi is not None and boc is not None:
            obj_idx = (choice.object_index or 0) + bi if bi else choice.object_index
            picked = _pick_union_param(
                item.parameter,
                overrides,
                f"prop_id={choice.property_id}+{bo + choice.offset}",
            )
            if picked is not None:
                up, value = picked
                out.prop.append(
                    PropWrite(
                        obj_idx,
                        choice.property_id,
                        choice.occurrence + boc,
                        bo + choice.offset + up.offset,
                        choice.bit_offset + up.bit_offset,
                        up.id,
                        up.parameter_type,
                        value,
                    )
                )
    else:
        assert isinstance(choice, PropertyUnion)
        picked = _pick_union_param(
            item.parameter, overrides, f"prop_id={choice.property_id}+{choice.offset}"
        )
        if picked is not None:
            up, value = picked
            out.prop.append(
                PropWrite(
                    choice.object_index,
                    choice.property_id,
                    choice.occurrence,
                    choice.offset + up.offset,
                    choice.bit_offset + up.bit_offset,
                    up.id,
                    up.parameter_type,
                    value,
                )
            )


def _collect_module_writes(
    ms: ModuleState, idx: ApplicationIndexer, out: Writes
) -> None:
    if ms.ref_id is not None:
        md = idx.module_defs.get(ms.ref_id)
        if md is not None and md.static.parameters is not None:
            instance_overrides = _build_instance_overrides(ms, idx)
            for item in md.static.parameters.choice:
                if isinstance(item, ModuleDefStaticParametersParameter):
                    _collect_param(item, instance_overrides, ms, out)
                else:
                    assert isinstance(item, ModuleDefStaticParametersUnion)
                    _collect_union(item, instance_overrides, ms, out)
    for child in ms.module_children():
        _collect_module_writes(child, idx, out)


def collect_writes(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> Writes:
    """Collect all parameter writes into a Writes container (mem + prop), separated by destination type."""
    out = Writes()
    s = app.static
    if s.parameters is not None:
        for item in s.parameters.choice:
            if isinstance(item, ApplicationProgramStaticParametersParameter):
                _collect_param(item, overrides, None, out)
            else:
                assert isinstance(item, ApplicationProgramStaticParametersUnion)
                _collect_union(item, overrides, None, out)
    if state is not None:
        for ms in state.module_children():
            _collect_module_writes(ms, idx, out)
    return out


def encode_to_memory(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[str, bytes]:
    """Encode parameter values into code segment byte buffers.

    Returns {segment_id: bytes} for every code segment, seeded from seg.data if present.
    Bit layout: bit_offset=0 is the MSB of each byte; values stored big-endian.
    """
    writes = collect_writes(app, idx, overrides, state)
    bufs: dict[str, bytearray] = {
        seg_id: bytearray(seg.data) if seg.data else bytearray(seg.size)
        for seg_id, seg in idx.code_segments.items()
    }
    for w in writes.mem:
        buf = bufs.get(w.seg_id)
        if buf is None:
            continue
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            continue
        tc = pt.choice
        size_in_bit = getattr(tc, "size_in_bit", None)
        if size_in_bit is None:
            continue
        encoded = _encode_value(w.value, size_in_bit, tc)
        if encoded is None:
            continue
        _write_bits(buf, w.offset, w.bit_offset, size_in_bit, encoded)
    return {seg_id: bytes(buf) for seg_id, buf in bufs.items()}


def build_memory_param_map(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[str, dict[int, tuple[str, str]]]:
    """Build {seg_id: {byte_offset: (param_id, value)}} for hex viewer hover lookups."""
    writes = collect_writes(app, idx, overrides, state)
    maps: dict[str, dict[int, tuple[str, str]]] = {
        seg_id: {} for seg_id in idx.code_segments
    }
    for w in writes.mem:
        seg_map = maps.get(w.seg_id)
        if seg_map is None:
            continue
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            continue
        size = getattr(pt.choice, "size_in_bit", None)
        if not size:
            continue
        start_bit = w.offset * 8 + w.bit_offset
        end_bit = start_bit + size - 1
        for b in range(start_bit // 8, end_bit // 8 + 1):
            seg_map[b] = (w.param_id, w.value)
    return maps


def encode_to_properties(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[PropertyKey, bytes]:
    """Encode PropertyParameter-backed parameters into interface object property data.

    Returns {(object_index, property_id, occurrence): bytes}.
    Bit layout: bit_offset=0 is the MSB of each byte; values stored big-endian.
    Buffers are sized dynamically to fit all writes.
    """
    writes = collect_writes(app, idx, overrides, state)
    bufs: dict[PropertyKey, bytearray] = {}
    for w in writes.prop:
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            continue
        tc = pt.choice
        size_in_bit = getattr(tc, "size_in_bit", None)
        if not size_in_bit:
            continue
        encoded = _encode_value(w.value, size_in_bit, tc)
        if encoded is None:
            continue
        key: PropertyKey = (w.object_index, w.property_id, w.occurrence)
        needed = w.offset + (w.bit_offset + size_in_bit + 7) // 8
        buf = bufs.get(key)
        if buf is None:
            bufs[key] = buf = bytearray(needed)
        elif len(buf) < needed:
            buf.extend(bytearray(needed - len(buf)))
        _write_bits(buf, w.offset, w.bit_offset, size_in_bit, encoded)
    return {key: bytes(buf) for key, buf in bufs.items()}


def build_property_param_map(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[PropertyKey, dict[int, tuple[str, str]]]:
    """Build {(object_index, property_id, occurrence): {byte_offset: (param_id, value)}} for lookups."""
    writes = collect_writes(app, idx, overrides, state)
    maps: dict[PropertyKey, dict[int, tuple[str, str]]] = {}
    for w in writes.prop:
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            continue
        size = getattr(pt.choice, "size_in_bit", None)
        if not size:
            continue
        key: PropertyKey = (w.object_index, w.property_id, w.occurrence)
        byte_map = maps.setdefault(key, {})
        start_bit = w.offset * 8 + w.bit_offset
        end_bit = start_bit + size - 1
        for b in range(start_bit // 8, end_bit // 8 + 1):
            byte_map[b] = (w.param_id, w.value)
    return maps
