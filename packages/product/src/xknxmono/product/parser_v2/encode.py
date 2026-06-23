from __future__ import annotations

import struct
from collections.abc import Generator

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t_parameters_parameter import (
    ApplicationProgramStaticParametersParameter,
)
from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter
from xknxmono.models.intermediate.memory_union_t import MemoryUnion
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter import (
    ModuleDefStaticParametersParameter,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter_memory import (
    ModuleDefStaticParametersParameterMemory,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_union import (
    ModuleDefStaticParametersUnion,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_union_memory import (
    ModuleDefStaticParametersUnionMemory,
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

from .application_indexer import ApplicationIndexer
from .state import GlobalState, ModuleState

# (seg_id, byte_offset, bit_offset, param_id, parameter_type, value)
_ParamWrite = tuple[str, int, int, str, str, str]


def _write_bits(buf: bytearray, offset: int, bit_offset: int, size_in_bit: int, value: int) -> None:
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

    Does not include static defaults — encode_to_memory reads those directly from the
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


def _write_param(
    param_id: str,
    parameter_type: str,
    offset: int,
    bit_offset: int,
    value_str: str,
    idx: ApplicationIndexer,
    buf: bytearray,
) -> None:
    pt = idx.parameter_types.get(parameter_type)
    if pt is None:
        return
    tc = pt.choice
    size_in_bit = getattr(tc, "size_in_bit", None)
    if size_in_bit is None:
        return
    value = _encode_value(value_str, size_in_bit, tc)
    if value is None:
        return
    _write_bits(buf, offset, bit_offset, size_in_bit, value)


def _resolve_base_offset(base_offset_id: str | None, ms: ModuleState) -> int | None:
    if base_offset_id is None:
        return 0
    arg = ms.arguments.get(base_offset_id)
    if not isinstance(arg, ModuleNumericArg) or arg.value is None:
        return None
    return arg.value


def _iter_module_writes(ms: ModuleState, idx: ApplicationIndexer) -> Generator[_ParamWrite, None, None]:
    if ms.ref_id is not None:
        md = idx.module_defs.get(ms.ref_id)
        if md is not None and md.static.parameters is not None:
            instance_overrides: dict[str, str] = {}
            for pr_id, value in ms.param_ref_id_to_value.items():
                pr = idx.parameter_refs.get(pr_id)
                if pr is not None:
                    param = idx.parameters.get(pr.ref_id)
                    if param is not None:
                        instance_overrides[param.id] = value

            for item in md.static.parameters.choice:
                if isinstance(item, ModuleDefStaticParametersParameter):
                    mem = item.choice
                    if not isinstance(mem, ModuleDefStaticParametersParameterMemory):
                        continue
                    base = _resolve_base_offset(mem.base_offset, ms)
                    if base is None:
                        continue
                    yield (
                        mem.code_segment,
                        base + mem.offset,
                        mem.bit_offset,
                        item.id,
                        item.parameter_type,
                        instance_overrides.get(item.id) or item.value,
                    )
                else:
                    assert isinstance(item, ModuleDefStaticParametersUnion)
                    mem = item.choice
                    if not isinstance(mem, ModuleDefStaticParametersUnionMemory):
                        continue
                    base = _resolve_base_offset(mem.base_offset, ms)
                    if base is None:
                        continue

                    active = [up for up in item.parameter if up.id in instance_overrides]
                    assert len(active) <= 1, (
                        f"module union at {mem.code_segment}+{base + mem.offset} has "
                        f"{len(active)} active alternatives: "
                        + ", ".join(up.id for up in active)
                    )

                    if active:
                        up = active[0]
                        yield (
                            mem.code_segment,
                            base + mem.offset + up.offset,
                            mem.bit_offset + up.bit_offset,
                            up.id,
                            up.parameter_type,
                            instance_overrides[up.id],
                        )
                    else:
                        default_up = next(
                            (up for up in item.parameter if up.default_union_parameter), None
                        )
                        if default_up is not None:
                            yield (
                                mem.code_segment,
                                base + mem.offset + default_up.offset,
                                mem.bit_offset + default_up.bit_offset,
                                default_up.id,
                                default_up.parameter_type,
                                default_up.value,
                            )

    for child in ms.module_children():
        yield from _iter_module_writes(child, idx)


def _iter_param_writes(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> Generator[_ParamWrite, None, None]:
    """Yield (seg_id, offset, bit_offset, param_id, parameter_type, value) for every parameter."""
    s = app.static
    if s.parameters is not None:
        for item in s.parameters.choice:
            if isinstance(item, ApplicationProgramStaticParametersParameter):
                mem = item.choice
                if not isinstance(mem, MemoryParameter):
                    continue
                yield (
                    mem.code_segment,
                    mem.offset,
                    mem.bit_offset,
                    item.id,
                    item.parameter_type,
                    overrides.get(item.id) or item.value,
                )
            else:
                mem = item.choice
                if not isinstance(mem, MemoryUnion):
                    continue

                active = [up for up in item.parameter if up.id in overrides]
                assert len(active) <= 1, (
                    f"union at {mem.code_segment}+{mem.offset} has {len(active)} active alternatives: "
                    + ", ".join(up.id for up in active)
                )

                if active:
                    up = active[0]
                    yield (
                        mem.code_segment,
                        mem.offset + up.offset,
                        mem.bit_offset + up.bit_offset,
                        up.id,
                        up.parameter_type,
                        overrides[up.id],
                    )
                else:
                    default_up = next(
                        (up for up in item.parameter if up.default_union_parameter), None
                    )
                    if default_up is not None:
                        yield (
                            mem.code_segment,
                            mem.offset + default_up.offset,
                            mem.bit_offset + default_up.bit_offset,
                            default_up.id,
                            default_up.parameter_type,
                            default_up.value,
                        )

    if state is not None:
        for ms in state.module_children():
            yield from _iter_module_writes(ms, idx)


def encode_to_memory(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[str, bytes]:
    """Encode parameter values into code segment byte buffers by iterating the static parameter model.

    Returns {segment_id: bytes} for every code segment, seeded from seg.data if present.
    Pass state to also encode module instance parameters (base_offset resolved via NumericArg).

    Notes:
    - Bit layout: bit_offset=0 is the MSB of each byte; values stored big-endian.
    - Standalone parameters: state override takes priority over param.value.
    - Union parameters: asserts at most one alternative has an override; falls back to
      the DefaultUnionParameter's param.value when none does.
    """
    # TODO: the iteration over app.static.parameters repeats work that ApplicationIndexer
    # already does at build time. Consider pre-computing a flat list of (param_id, type_id,
    # seg_id, abs_offset, abs_bit_offset) tuples in the indexer so encode_to_memory just
    # iterates a single pre-built structure rather than re-walking the static model each call.
    bufs: dict[str, bytearray] = {
        seg_id: bytearray(seg.data) if seg.data else bytearray(seg.size)
        for seg_id, seg in idx.code_segments.items()
    }
    for seg_id, offset, bit_offset, param_id, parameter_type, value in _iter_param_writes(app, idx, overrides, state):
        buf = bufs.get(seg_id)
        if buf is not None:
            _write_param(param_id, parameter_type, offset, bit_offset, value, idx, buf)
    return {seg_id: bytes(buf) for seg_id, buf in bufs.items()}


def build_memory_param_map(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[str, dict[int, tuple[str, str]]]:
    """Build {seg_id: {byte_offset: (param_id, value)}} for hex viewer hover lookups."""
    maps: dict[str, dict[int, tuple[str, str]]] = {seg_id: {} for seg_id in idx.code_segments}
    for seg_id, offset, bit_offset, param_id, parameter_type, value in _iter_param_writes(app, idx, overrides, state):
        seg_map = maps.get(seg_id)
        if seg_map is None:
            continue
        pt = idx.parameter_types.get(parameter_type)
        if pt is None:
            continue
        size = getattr(pt.choice, "size_in_bit", None)
        if not size:
            continue
        start_bit = offset * 8 + bit_offset
        end_bit = start_bit + size - 1
        for b in range(start_bit // 8, end_bit // 8 + 1):
            seg_map[b] = (param_id, value)
    return maps
