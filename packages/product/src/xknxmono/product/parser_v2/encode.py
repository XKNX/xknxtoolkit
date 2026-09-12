from __future__ import annotations

import ipaddress
import struct
from typing import NamedTuple

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t_options_parameter_byte_order import (
    ApplicationProgramStaticOptionsParameterByteOrder,
)
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
from xknxmono.models.intermediate.parameter_type_t_type_color import (
    ParameterTypeTypeColor,
)
from xknxmono.models.intermediate.parameter_type_t_type_color_space import (
    ParameterTypeTypeColorSpace,
)
from xknxmono.models.intermediate.parameter_type_t_type_date import (
    ParameterTypeTypeDate,
)
from xknxmono.models.intermediate.parameter_type_t_type_float import (
    ParameterTypeTypeFloat,
)
from xknxmono.models.intermediate.parameter_type_t_type_float_encoding import (
    ParameterTypeTypeFloatEncoding,
)
from xknxmono.models.intermediate.parameter_type_t_type_ipaddress import (
    ParameterTypeTypeIpaddress,
)
from xknxmono.models.intermediate.parameter_type_t_type_ipaddress_version import (
    ParameterTypeTypeIpaddressVersion,
)
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_raw_data import (
    ParameterTypeTypeRawData,
)
from xknxmono.models.intermediate.parameter_type_t_type_restriction import (
    ParameterTypeTypeRestriction,
)
from xknxmono.models.intermediate.parameter_type_t_type_text import (
    ParameterTypeTypeText,
)
from xknxmono.models.intermediate.parameter_type_t_type_time import (
    ParameterTypeTypeTime,
)
from xknxmono.models.intermediate.parameter_type_t_type_time_unit import (
    ParameterTypeTypeTimeUnit,
)
from xknxmono.models.intermediate.property_parameter_t import PropertyParameter
from xknxmono.models.intermediate.property_union_t import PropertyUnion
from xknxmono.models.intermediate.union_parameter_t import UnionParameter

from ..errors import EncodingError
from .application_indexer import ApplicationIndexer
from .state import GlobalState, ModuleState


class MemWrite(NamedTuple):
    seg_id: str
    offset: int
    bit_offset: int
    param_id: str
    parameter_type: str
    value: str
    union_size_in_bit: int | None = None


class PropWrite(NamedTuple):
    object_index: int | None
    property_id: int
    occurrence: int
    offset: int
    bit_offset: int
    param_id: str
    parameter_type: str
    value: str
    union_size_in_bit: int | None = None


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


_SIMPLE_TIME_UNITS = frozenset(
    {
        ParameterTypeTypeTimeUnit.HOURS,
        ParameterTypeTypeTimeUnit.MINUTES,
        ParameterTypeTypeTimeUnit.SECONDS,
        ParameterTypeTypeTimeUnit.HUNDRED_MILLISECONDS,
        ParameterTypeTypeTimeUnit.TEN_MILLISECONDS,
        ParameterTypeTypeTimeUnit.MILLISECONDS,
    }
)

_FLOAT_ENCODING_SIZE_IN_BIT = {
    ParameterTypeTypeFloatEncoding.DPT_9: 16,
    ParameterTypeTypeFloatEncoding.IEEE_754_SINGLE: 32,
    ParameterTypeTypeFloatEncoding.IEEE_754_DOUBLE: 64,
}

_DATE_SIZE_IN_BIT = (
    24  # DPT 11: day/month/year octets - the only Date encoding there is
)

_IPADDRESS_SIZE_IN_BIT = {
    ParameterTypeTypeIpaddressVersion.IPV4: 32,
    ParameterTypeTypeIpaddressVersion.IPV6: 128,
}

_COLOR_SIZE_IN_BIT = {
    ParameterTypeTypeColorSpace.RGB: 24,
    ParameterTypeTypeColorSpace.RGBW: 32,
    ParameterTypeTypeColorSpace.HSV: 24,
}


def _size_in_bit(tc: object) -> int | None:
    """Bit-width of a parameter type's encoded value.

    Several types have no size_in_bit field of their own because their encoding fixes
    the width: Float (DPT 9 is 2 bytes, IEEE-754 single/double are 4/8), Date (DPT 11
    is always 3 bytes), IP address (4 bytes for IPv4, 16 for IPv6) and Color (3 bytes
    for RGB/HSV, 4 for RGBW). RawData carries its width as max_size (bytes), not bits.
    Every other type carries size_in_bit directly.
    """
    if isinstance(tc, ParameterTypeTypeFloat):
        return _FLOAT_ENCODING_SIZE_IN_BIT.get(tc.encoding)
    if isinstance(tc, ParameterTypeTypeDate):
        return _DATE_SIZE_IN_BIT
    if isinstance(tc, ParameterTypeTypeIpaddress):
        return _IPADDRESS_SIZE_IN_BIT.get(tc.version)
    if isinstance(tc, ParameterTypeTypeColor):
        return _COLOR_SIZE_IN_BIT.get(tc.space)
    if isinstance(tc, ParameterTypeTypeRawData):
        return tc.max_size * 8
    return getattr(tc, "size_in_bit", None)


def _write_size_in_bit(w: MemWrite | PropWrite, tc: object) -> int | None:
    """Bit-width for one write: the parameter type's own size, or - for a type that
    doesn't carry one - the enclosing union's declared width, which is the only place
    such a type's size is recorded.
    """
    size = _size_in_bit(tc)
    return size if size is not None else w.union_size_in_bit


def _program_little_endian(app: ApplicationProgram) -> bool:
    """Whether the application program encodes multi-octet numeric values little-endian.

    Read from the static section's ParameterByteOrder option (defaults to big-endian
    when the option, or the whole Options section, is absent).
    """
    options = app.static.options
    return (
        options is not None
        and options.parameter_byte_order
        == ApplicationProgramStaticOptionsParameterByteOrder.LITTLE_ENDIAN
    )


def _apply_byte_order(
    value: int | None, size_in_bit: int, little_endian: bool
) -> int | None:
    """Reverse the octet order of a byte-aligned, multi-octet numeric value.

    Only plain numeric encodings (Number/Restriction/Float/Time) are byte-order
    sensitive - a program's ParameterByteOrder option governs how a single number is
    split across octets. Text, Date, IP address, Color and RawData are structured
    byte sequences where each octet's position is fixed by the type itself, not by
    program-wide byte order, so this is never applied to them.
    """
    if value is None or not little_endian or size_in_bit < 16 or size_in_bit % 8 != 0:
        return value
    n = size_in_bit // 8
    return int.from_bytes(value.to_bytes(n, "big")[::-1], "big")


def _encode_number(str_value: str, size_in_bit: int) -> int | None:
    """Signed/unsigned integer, masked to size_in_bit (two's complement)."""
    try:
        v = int(str_value)
    except (ValueError, TypeError):
        return None
    return v & ((1 << size_in_bit) - 1)


def _encode_restriction(str_value: str, size_in_bit: int) -> int | None:
    """Enumeration value of a restricted parameter type, encoded as a plain integer."""
    return _encode_number(str_value, size_in_bit)


def _encode_float(
    str_value: str, size_in_bit: int, tc: ParameterTypeTypeFloat
) -> int | None:
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


def _encode_text(str_value: str, size_in_bit: int) -> int:
    """Code-page (Latin-1) text, truncated and zero-padded to the field width."""
    encoded = str_value.encode("latin-1", errors="replace")
    n_bytes = size_in_bit // 8
    padded = encoded[:n_bytes].ljust(n_bytes, b"\x00")
    return int.from_bytes(padded, "big")


def _encode_time(
    str_value: str, size_in_bit: int, tc: ParameterTypeTypeTime
) -> int | None:
    """Duration as a plain integer count of the type's configured unit.

    Packed variants (e.g. days/hours/minutes/seconds sharing one value) split the
    value across multiple bit fields - that layout isn't implemented, so they're left
    unencodable rather than guessed at.
    """
    if tc.unit not in _SIMPLE_TIME_UNITS:
        return None
    return _encode_number(str_value, size_in_bit)


def _encode_date(str_value: str, tc: ParameterTypeTypeDate) -> int | None:
    """KNX date (DPT 11): 3 octets day, month, year mod 100 (value "YYYY-MM-DD").

    When the type does not display the year, the year octet is written as zero.
    """
    parts = str_value.split("-")
    if len(parts) != 3:
        return None
    try:
        year, month, day = (int(p) for p in parts)
    except ValueError:
        return None
    year_octet = 0 if not tc.display_the_year else year % 100
    return (day << 16) | (month << 8) | year_octet


def _encode_ipaddress(str_value: str) -> int | None:
    """IPv4/IPv6 address string to its network-order octets, as an integer."""
    try:
        return int(ipaddress.ip_address(str_value))
    except ValueError:
        return None


def _rgb_to_hsv(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert an 8-bit RGB triple to an 8-bit-per-component KNX HSV triple."""
    low = min(r, g, b)
    high = max(r, g, b)
    if low == high:
        hue = 0.0
    elif high == r:
        hue = 60.0 * (g - b) / (high - low)
    elif high == g:
        hue = 60.0 * (2.0 + (b - r) / (high - low))
    else:
        hue = 60.0 * (4.0 + (r - g) / (high - low))
    hue %= 360.0
    saturation = 0 if high == 0 else round(255.0 * (high - low) / high)
    return round(255.0 * hue / 360.0), saturation, high


def _encode_color(str_value: str, tc: ParameterTypeTypeColor) -> int | None:
    """Color from a "#RRGGBB"/"#RRGGBBWW" hex string, per the type's color space.

    RGB and RGBW are stored verbatim (3 or 4 octets); HSV is converted from the same
    hex RGB input, since that's the only value format the UI's color picker produces.
    """
    try:
        raw = bytes.fromhex(str_value.lstrip("#"))
    except ValueError:
        return None
    if tc.space == ParameterTypeTypeColorSpace.RGBW:
        if len(raw) < 4:
            return None
        return int.from_bytes(raw[:4], "big")
    if len(raw) < 3:
        return None
    r, g, b = raw[0], raw[1], raw[2]
    if tc.space == ParameterTypeTypeColorSpace.HSV:
        h, s, v = _rgb_to_hsv(r, g, b)
        return (h << 16) | (s << 8) | v
    return (r << 16) | (g << 8) | b


def _encode_raw_data(str_value: str, size_in_bit: int) -> int | None:
    """Raw octets from a hex string, truncated/zero-padded to the field width."""
    try:
        data = bytes.fromhex(str_value)
    except ValueError:
        return None
    n_bytes = size_in_bit // 8
    padded = data[:n_bytes].ljust(n_bytes, b"\x00")
    return int.from_bytes(padded, "big")


def _encode_value(
    str_value: str, size_in_bit: int, tc: object, *, little_endian: bool = False
) -> int | None:
    if isinstance(tc, ParameterTypeTypeNumber):
        return _apply_byte_order(
            _encode_number(str_value, size_in_bit), size_in_bit, little_endian
        )
    if isinstance(tc, ParameterTypeTypeRestriction):
        return _apply_byte_order(
            _encode_restriction(str_value, size_in_bit), size_in_bit, little_endian
        )
    if isinstance(tc, ParameterTypeTypeFloat):
        return _apply_byte_order(
            _encode_float(str_value, size_in_bit, tc), size_in_bit, little_endian
        )
    if isinstance(tc, ParameterTypeTypeText):
        return _encode_text(str_value, size_in_bit)
    if isinstance(tc, ParameterTypeTypeTime):
        return _apply_byte_order(
            _encode_time(str_value, size_in_bit, tc), size_in_bit, little_endian
        )
    if isinstance(tc, ParameterTypeTypeColor):
        return _encode_color(str_value, tc)
    if isinstance(tc, ParameterTypeTypeDate):
        return _encode_date(str_value, tc)
    if isinstance(tc, ParameterTypeTypeIpaddress):
        return _encode_ipaddress(str_value)
    if isinstance(tc, ParameterTypeTypeRawData):
        return _encode_raw_data(str_value, size_in_bit)
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
        if param is None:
            raise EncodingError(
                f"ParameterRef {pr_id!r} has an override but its target parameter "
                f"{pr.ref_id!r} does not exist"
            )
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
        if pr is None:
            raise EncodingError(
                f"Module instance {ms.module_instance_id!r} has an override for "
                f"unknown ParameterRef {pr_id!r}"
            )
        param = idx.parameters.get(pr.ref_id)
        if param is None:
            raise EncodingError(
                f"ParameterRef {pr_id!r} has an override but its target parameter "
                f"{pr.ref_id!r} does not exist"
            )
        overrides[param.id] = value
    return overrides


def _pick_union_param(
    parameters: list[UnionParameter],
    overrides: dict[str, str],
    location: str,
) -> tuple[UnionParameter, str] | None:
    """Return the active override, or the default alternative, or None if neither is
    set - real product data ships unions with no explicit default (relying on none of
    their alternatives being written), so having neither is valid and simply means
    there's nothing to write for this union."""
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
        if base is None:
            raise EncodingError(
                f"module instance {ms.module_instance_id!r} could not resolve base "
                f"offset {choice.base_offset!r} for parameter {item.id!r}"
            )
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
        if bo is None or bi is None or boc is None:
            raise EncodingError(
                f"module instance {ms.module_instance_id!r} could not resolve a base "
                f"offset/index/occurrence for parameter {item.id!r}"
            )
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
        member_ids = ", ".join(up.id for up in item.parameter) or "<no members>"
        raise EncodingError(f"union with members [{member_ids}] has no destination")
    # Check subclasses before parents (module types extend their top-level counterparts)
    if isinstance(choice, ModuleDefStaticParametersUnionMemory):
        assert ms is not None
        base = _resolve_base(choice.base_offset, ms)
        if base is None:
            raise EncodingError(
                f"module instance {ms.module_instance_id!r} could not resolve base "
                f"offset {choice.base_offset!r} for union at {choice.code_segment!r}"
            )
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
                    item.size_in_bit,
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
                    item.size_in_bit,
                )
            )
    elif isinstance(choice, ModuleDefStaticParametersUnionProperty):
        assert ms is not None
        bo = _resolve_base(choice.base_offset, ms)
        bi = _resolve_base(choice.base_index, ms)
        boc = _resolve_base(choice.base_occurrence, ms)
        if bo is None or bi is None or boc is None:
            raise EncodingError(
                f"module instance {ms.module_instance_id!r} could not resolve a base "
                f"offset/index/occurrence for union at property {choice.property_id!r}"
            )
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
                    item.size_in_bit,
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
                    item.size_in_bit,
                )
            )


def _collect_module_writes(
    ms: ModuleState, idx: ApplicationIndexer, out: Writes
) -> None:
    if ms.ref_id is None:
        raise EncodingError(
            f"module instance {ms.module_instance_id!r} has no module def reference"
        )
    md = idx.module_defs.get(ms.ref_id)
    if md is None:
        raise EncodingError(
            f"module instance {ms.module_instance_id!r} references unknown module "
            f"def {ms.ref_id!r}"
        )
    if md.static.parameters is not None:
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
    little_endian = _program_little_endian(app)
    bufs: dict[str, bytearray] = {
        seg_id: bytearray(seg.data) if seg.data else bytearray(seg.size)
        for seg_id, seg in idx.code_segments.items()
    }
    for w in writes.mem:
        buf = bufs.get(w.seg_id)
        if buf is None:
            raise EncodingError(
                f"parameter {w.param_id!r} writes to unknown code segment {w.seg_id!r}"
            )
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            raise EncodingError(
                f"parameter {w.param_id!r} has unknown parameter type "
                f"{w.parameter_type!r}"
            )
        tc = pt.choice
        size_in_bit = _write_size_in_bit(w, tc)
        if size_in_bit is None:
            raise EncodingError(
                f"parameter type {w.parameter_type!r} (used by {w.param_id!r}) has "
                f"no size_in_bit"
            )
        encoded = _encode_value(w.value, size_in_bit, tc, little_endian=little_endian)
        if encoded is None:
            raise EncodingError(
                f"parameter {w.param_id!r} value {w.value!r} could not be encoded "
                f"for type {w.parameter_type!r}"
            )
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
            raise EncodingError(
                f"parameter {w.param_id!r} writes to unknown code segment {w.seg_id!r}"
            )
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            raise EncodingError(
                f"parameter {w.param_id!r} has unknown parameter type "
                f"{w.parameter_type!r}"
            )
        size = _write_size_in_bit(w, pt.choice)
        if not size:
            raise EncodingError(
                f"parameter type {w.parameter_type!r} (used by {w.param_id!r}) has "
                f"no size_in_bit"
            )
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
    little_endian = _program_little_endian(app)
    bufs: dict[PropertyKey, bytearray] = {}
    for w in writes.prop:
        pt = idx.parameter_types.get(w.parameter_type)
        if pt is None:
            raise EncodingError(
                f"parameter {w.param_id!r} has unknown parameter type "
                f"{w.parameter_type!r}"
            )
        tc = pt.choice
        size_in_bit = _write_size_in_bit(w, tc)
        if not size_in_bit:
            raise EncodingError(
                f"parameter type {w.parameter_type!r} (used by {w.param_id!r}) has "
                f"no size_in_bit"
            )
        encoded = _encode_value(w.value, size_in_bit, tc, little_endian=little_endian)
        if encoded is None:
            raise EncodingError(
                f"parameter {w.param_id!r} value {w.value!r} could not be encoded "
                f"for type {w.parameter_type!r}"
            )
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
            raise EncodingError(
                f"parameter {w.param_id!r} has unknown parameter type "
                f"{w.parameter_type!r}"
            )
        size = _write_size_in_bit(w, pt.choice)
        if not size:
            raise EncodingError(
                f"parameter type {w.parameter_type!r} (used by {w.param_id!r}) has "
                f"no size_in_bit"
            )
        key: PropertyKey = (w.object_index, w.property_id, w.occurrence)
        byte_map = maps.setdefault(key, {})
        start_bit = w.offset * 8 + w.bit_offset
        end_bit = start_bit + size - 1
        for b in range(start_bit // 8, end_bit // 8 + 1):
            byte_map[b] = (w.param_id, w.value)
    return maps
