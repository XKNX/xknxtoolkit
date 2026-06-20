from __future__ import annotations

import struct

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


def _encode_module_params(ms: ModuleState, idx: ApplicationIndexer, bufs: dict[str, bytearray]) -> None:
    """Encode parameters for one module instance and recurse into sub-module children."""
    if ms.def_id is not None:
        md = idx.module_defs.get(ms.def_id)
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
                    buf = bufs.get(mem.code_segment)
                    if buf is None:
                        continue
                    base = _resolve_base_offset(mem.base_offset, ms)
                    if base is None:
                        continue
                    _write_param(
                        item.id, item.parameter_type,
                        base + mem.offset, mem.bit_offset,
                        instance_overrides.get(item.id) or item.value,
                        idx, buf,
                    )
                else:
                    assert isinstance(item, ModuleDefStaticParametersUnion)
                    mem = item.choice
                    if not isinstance(mem, ModuleDefStaticParametersUnionMemory):
                        continue
                    buf = bufs.get(mem.code_segment)
                    if buf is None:
                        continue
                    base = _resolve_base_offset(mem.base_offset, ms)
                    if base is None:
                        continue

                    active = [up for up in item.parameter if up.id in instance_overrides]
                    assert len(active) <= 1, (
                        f"module union at {mem.code_segment}+{base + mem.offset} has {len(active)} active alternatives: "
                        + ", ".join(up.id for up in active)
                    )

                    if active:
                        up = active[0]
                        _write_param(
                            up.id, up.parameter_type,
                            base + mem.offset + up.offset, mem.bit_offset + up.bit_offset,
                            instance_overrides[up.id], idx, buf,
                        )
                    else:
                        default_up = next((up for up in item.parameter if up.default_union_parameter), None)
                        if default_up is not None:
                            _write_param(
                                default_up.id, default_up.parameter_type,
                                base + mem.offset + default_up.offset, mem.bit_offset + default_up.bit_offset,
                                default_up.value, idx, buf,
                            )

    for child in ms.module_children():
        _encode_module_params(child, idx, bufs)


def encode_to_memory(
    app: ApplicationProgram,
    idx: ApplicationIndexer,
    overrides: dict[str, str],
    state: GlobalState | None = None,
) -> dict[str, bytes]:
    """Encode parameter values into code segment byte buffers by iterating the static parameter model.

    Returns {segment_id: bytes} for every AbsoluteSegment, starting from zeros.
    Pass state to also encode module instance parameters (base_offset resolved via NumericArg).

    Notes:
    - Bit layout: bit_offset=0 is the MSB of each byte; values stored big-endian.
    - Standalone parameters: state override takes priority over param.value.
    - Union parameters: asserts at most one alternative has an override; falls back to
      the DefaultUnionParameter's param.value when none does.
    """
    # TODO: the iteration over app.static.parameters below repeats work that ApplicationIndexer
    # already does at build time. Consider pre-computing a flat list of (param_id, type_id,
    # seg_id, abs_offset, abs_bit_offset) tuples in the indexer so encode_to_memory just
    # iterates a single pre-built structure rather than re-walking the static model each call.
    bufs: dict[str, bytearray] = {
        seg_id: bytearray(seg.size) for seg_id, seg in idx.code_segments.items()
    }

    s = app.static
    if s.parameters is None:
        return {seg_id: bytes(buf) for seg_id, buf in bufs.items()}

    for item in s.parameters.choice:
        if isinstance(item, ApplicationProgramStaticParametersParameter):
            mem = item.choice
            if not isinstance(mem, MemoryParameter):
                continue
            buf = bufs.get(mem.code_segment)
            if buf is None:
                continue
            _write_param(item.id, item.parameter_type, mem.offset, mem.bit_offset, overrides.get(item.id) or item.value, idx, buf)

        else:
            mem = item.choice
            if not isinstance(mem, MemoryUnion):
                continue
            buf = bufs.get(mem.code_segment)
            if buf is None:
                continue

            active = [up for up in item.parameter if up.id in overrides]
            assert len(active) <= 1, (
                f"union at {mem.code_segment}+{mem.offset} has {len(active)} active alternatives: "
                + ", ".join(up.id for up in active)
            )

            if active:
                up = active[0]
                _write_param(
                    up.id, up.parameter_type,
                    mem.offset + up.offset, mem.bit_offset + up.bit_offset,
                    overrides[up.id], idx, buf,
                )
            else:
                default_up = next((up for up in item.parameter if up.default_union_parameter), None)
                if default_up is not None:
                    _write_param(
                        default_up.id, default_up.parameter_type,
                        mem.offset + default_up.offset, mem.bit_offset + default_up.bit_offset,
                        default_up.value, idx, buf,
                    )

    if state is not None:
        for ms in state.module_children():
            _encode_module_params(ms, idx, bufs)

    return {seg_id: bytes(buf) for seg_id, buf in bufs.items()}
