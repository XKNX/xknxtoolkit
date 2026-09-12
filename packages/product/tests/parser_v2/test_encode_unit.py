"""Unit tests for collect_writes / encode_to_memory / encode_to_properties.

All tests build minimal ApplicationProgram IR structures in-process — no fixture files.
"""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_code import (
    ApplicationProgramStaticCode,
)
from xknxmono.models.intermediate.application_program_static_t_code_absolute_segment import (
    ApplicationProgramStaticCodeAbsoluteSegment,
)
from xknxmono.models.intermediate.application_program_static_t_options import (
    ApplicationProgramStaticOptions,
)
from xknxmono.models.intermediate.application_program_static_t_options_parameter_byte_order import (
    ApplicationProgramStaticOptionsParameterByteOrder,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_refs import (
    ApplicationProgramStaticParameterRefs,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_types import (
    ApplicationProgramStaticParameterTypes,
)
from xknxmono.models.intermediate.application_program_static_t_parameters import (
    ApplicationProgramStaticParameters,
)
from xknxmono.models.intermediate.application_program_static_t_parameters_parameter import (
    ApplicationProgramStaticParametersParameter,
)
from xknxmono.models.intermediate.application_program_static_t_parameters_union import (
    ApplicationProgramStaticParametersUnion,
)
from xknxmono.models.intermediate.application_program_t_module_defs import (
    ApplicationProgramModuleDefs,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.io_tpoint_parameter_t import IoPointParameter
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter
from xknxmono.models.intermediate.memory_union_t import MemoryUnion
from xknxmono.models.intermediate.module_def_static_t import ModuleDefStatic
from xknxmono.models.intermediate.module_def_static_t_parameters import (
    ModuleDefStaticParameters,
)
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
from xknxmono.models.intermediate.module_def_t import ModuleDef
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.models.intermediate.parameter_type_t import ParameterType
from xknxmono.models.intermediate.parameter_type_t_type_color import (
    ParameterTypeTypeColor,
)
from xknxmono.models.intermediate.parameter_type_t_type_color_space import (
    ParameterTypeTypeColorSpace,
)
from xknxmono.models.intermediate.parameter_type_t_type_date import (
    ParameterTypeTypeDate,
)
from xknxmono.models.intermediate.parameter_type_t_type_date_encoding import (
    ParameterTypeTypeDateEncoding,
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
from xknxmono.models.intermediate.parameter_type_t_type_ipaddress_address_type import (
    ParameterTypeTypeIpaddressAddressType,
)
from xknxmono.models.intermediate.parameter_type_t_type_ipaddress_version import (
    ParameterTypeTypeIpaddressVersion,
)
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_number_type import (
    ParameterTypeTypeNumberType,
)
from xknxmono.models.intermediate.parameter_type_t_type_raw_data import (
    ParameterTypeTypeRawData,
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
from xknxmono.product.errors import EncodingError
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.encode import (
    Writes,
    _encode_value,  # pyright: ignore[reportPrivateUsage]
    _size_in_bit,  # pyright: ignore[reportPrivateUsage]
    build_memory_param_map,
    build_property_param_map,
    collect_writes,
    encode_to_memory,
    encode_to_properties,
    resolve_param_values,
)
from xknxmono.product.parser_v2.state import GlobalState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PT_ID = "PT1"
_SEG_ID = "SEG1"


def _num_type(size_in_bit: int = 8) -> ParameterTypeTypeNumber:
    return ParameterTypeTypeNumber(
        size_in_bit=size_in_bit,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=(1 << size_in_bit) - 1,
    )


def _param_type(size_in_bit: int = 8) -> ParameterType:
    return ParameterType(id=_PT_ID, name="T", choice=_num_type(size_in_bit))


def _segment(
    size: int = 8, data: bytes | None = None
) -> ApplicationProgramStaticCodeAbsoluteSegment:
    return ApplicationProgramStaticCodeAbsoluteSegment(
        id=_SEG_ID, size=size, address=0, data=data
    )


def _param(
    param_id: str,
    choice: MemoryParameter | PropertyParameter | IoPointParameter | None,
    value: str = "0",
) -> ApplicationProgramStaticParametersParameter:
    return ApplicationProgramStaticParametersParameter(
        id=param_id, name="", text="", parameter_type=_PT_ID, value=value, choice=choice
    )


def _union_param(
    param_id: str,
    offset: int,
    value: str,
    default: bool = False,
    parameter_type: str = _PT_ID,
) -> UnionParameter:
    return UnionParameter(
        id=param_id,
        name="",
        text="",
        parameter_type=parameter_type,
        value=value,
        offset=offset,
        bit_offset=0,
        default_union_parameter=default,
    )


def _app(
    params: list[
        ApplicationProgramStaticParametersParameter
        | ApplicationProgramStaticParametersUnion
    ],
    seg_size: int = 8,
    seg_data: bytes | None = None,
    pt_size: int = 8,
    extra_param_types: list[ParameterType] | None = None,
    module_defs: list[ModuleDef] | None = None,
    parameter_refs: list[ParameterRef] | None = None,
    options: ApplicationProgramStaticOptions | None = None,
) -> tuple[ApplicationProgram, ApplicationIndexer]:
    app = ApplicationProgram(
        id="APP",
        name="",
        application_number=1,
        application_version=1,
        program_type=ApplicationProgramType.APPLICATION_PROGRAM,
        mask_version="BV20",
        load_procedure_style=LoadProcedureStyle.DEFAULT_PROCEDURE,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=ApplicationProgramStatic(
            code=ApplicationProgramStaticCode(
                absolute_segment=[_segment(seg_size, seg_data)]
            ),
            parameter_types=ApplicationProgramStaticParameterTypes(
                parameter_type=[_param_type(pt_size), *(extra_param_types or [])]
            ),
            parameters=ApplicationProgramStaticParameters(choice=params),
            parameter_refs=(
                ApplicationProgramStaticParameterRefs(parameter_ref=parameter_refs)
                if parameter_refs is not None
                else None
            ),
            options=options,
        ),
        module_defs=(
            ApplicationProgramModuleDefs(module_def=module_defs)
            if module_defs is not None
            else None
        ),
    )
    return app, ApplicationIndexer(app)


def _module_param(
    param_id: str,
    choice: ModuleDefStaticParametersParameterMemory
    | ModuleDefStaticParametersParameterProperty
    | None,
    value: str = "0",
    base_value: str | None = None,
) -> ModuleDefStaticParametersParameter:
    return ModuleDefStaticParametersParameter(
        id=param_id,
        name="",
        text="",
        parameter_type=_PT_ID,
        value=value,
        choice=choice,
        base_value=base_value,
    )


def _module_def(
    md_id: str,
    params: list[ModuleDefStaticParametersParameter | ModuleDefStaticParametersUnion]
    | None,
) -> ModuleDef:
    return ModuleDef(
        id=md_id,
        name="",
        static=ModuleDefStatic(
            parameters=(
                ModuleDefStaticParameters(choice=params) if params is not None else None
            )
        ),
    )


# ---------------------------------------------------------------------------
# collect_writes — memory parameter
# ---------------------------------------------------------------------------


def test_collect_mem_param() -> None:
    p = _param(
        "P1", MemoryParameter(code_segment=_SEG_ID, offset=2, bit_offset=0), value="42"
    )
    app, idx = _app([p])
    w = collect_writes(app, idx, {})
    assert len(w.mem) == 1
    assert len(w.prop) == 0
    assert w.mem[0].seg_id == _SEG_ID
    assert w.mem[0].offset == 2
    assert w.mem[0].value == "42"
    assert w.mem[0].param_id == "P1"


def test_collect_mem_param_override() -> None:
    p = _param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))
    app, idx = _app([p])
    w = collect_writes(app, idx, {"P1": "7"})
    assert w.mem[0].value == "7"


# ---------------------------------------------------------------------------
# collect_writes — property parameter
# ---------------------------------------------------------------------------


def test_collect_prop_param() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=1, property_id=53, occurrence=0, offset=0, bit_offset=0
        ),
        value="5",
    )
    app, idx = _app([p])
    w = collect_writes(app, idx, {})
    assert len(w.mem) == 0
    assert len(w.prop) == 1
    pw = w.prop[0]
    assert pw.object_index == 1
    assert pw.property_id == 53
    assert pw.occurrence == 0
    assert pw.value == "5"


# ---------------------------------------------------------------------------
# collect_writes — memory union
# ---------------------------------------------------------------------------


def test_collect_mem_union_default() -> None:
    union = ApplicationProgramStaticParametersUnion(
        choice=MemoryUnion(code_segment=_SEG_ID, offset=0, bit_offset=0),
        size_in_bit=8,
        parameter=[
            _union_param("U1", 0, "10", default=True),
            _union_param("U2", 0, "20"),
        ],
    )
    app, idx = _app([union])
    w = collect_writes(app, idx, {})
    assert len(w.mem) == 1
    assert w.mem[0].param_id == "U1"
    assert w.mem[0].value == "10"


def test_encode_to_memory_color_union_member_uses_union_declared_size() -> None:
    # ParameterTypeTypeColor has no size_in_bit of its own - real product data (a Gira
    # device) stores it as the sole member of a union whose own SizeInBit is the only
    # place that width is recorded.
    color_pt = ParameterType(
        id="PT-COLOR",
        name="Colour",
        choice=ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB),
    )
    union = ApplicationProgramStaticParametersUnion(
        choice=MemoryUnion(code_segment=_SEG_ID, offset=0, bit_offset=0),
        size_in_bit=24,
        parameter=[
            _union_param("U1", 0, "#1A2B3C", default=True, parameter_type="PT-COLOR")
        ],
    )
    app, idx = _app([union], seg_size=4, extra_param_types=[color_pt])
    mem = encode_to_memory(app, idx, {})
    assert mem[_SEG_ID][:3] == bytes.fromhex("1A2B3C")


def test_collect_mem_union_active_override() -> None:
    union = ApplicationProgramStaticParametersUnion(
        choice=MemoryUnion(code_segment=_SEG_ID, offset=0, bit_offset=0),
        size_in_bit=8,
        parameter=[
            _union_param("U1", 0, "10", default=True),
            _union_param("U2", 0, "20"),
        ],
    )
    app, idx = _app([union])
    w = collect_writes(app, idx, {"U2": "99"})
    assert w.mem[0].param_id == "U2"
    assert w.mem[0].value == "99"


# ---------------------------------------------------------------------------
# collect_writes — property union
# ---------------------------------------------------------------------------


def test_collect_prop_union_default() -> None:
    union = ApplicationProgramStaticParametersUnion(
        choice=PropertyUnion(
            object_index=0, property_id=10, occurrence=0, offset=0, bit_offset=0
        ),
        size_in_bit=8,
        parameter=[
            _union_param("U1", 0, "3", default=True),
            _union_param("U2", 0, "4"),
        ],
    )
    app, idx = _app([union])
    w = collect_writes(app, idx, {})
    assert len(w.prop) == 1
    assert w.prop[0].param_id == "U1"
    assert w.prop[0].property_id == 10


# ---------------------------------------------------------------------------
# encode_to_memory
# ---------------------------------------------------------------------------


def test_encode_to_memory_writes_value() -> None:
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=3, bit_offset=0))]
    )
    mem = encode_to_memory(app, idx, {"P1": "255"})
    assert mem[_SEG_ID][3] == 255


def test_encode_to_memory_default_value() -> None:
    app, idx = _app(
        [
            _param(
                "P1",
                MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
                value="42",
            )
        ]
    )
    mem = encode_to_memory(app, idx, {})
    assert mem[_SEG_ID][0] == 42


def test_encode_to_memory_seeded_from_seg_data() -> None:
    p = _param("P1", MemoryParameter(code_segment=_SEG_ID, offset=1, bit_offset=0))
    app, idx = _app([p], seg_data=b"\xff\x00\xff\xff")
    mem = encode_to_memory(app, idx, {"P1": "7"})
    assert mem[_SEG_ID][0] == 0xFF  # seeded from data
    assert mem[_SEG_ID][1] == 7  # overwritten by param
    assert mem[_SEG_ID][2] == 0xFF  # seeded from data


def test_encode_to_memory_sub_byte() -> None:
    # 4-bit param at bit_offset=4 of byte 0 — value 3 should land in lower nibble
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=4))],
        pt_size=4,
    )
    mem = encode_to_memory(app, idx, {"P1": "3"})
    assert mem[_SEG_ID][0] == 0x03  # bits 4-7 = 0b0011


def test_encode_to_memory_big_endian_is_default() -> None:
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))],
        pt_size=16,
    )
    mem = encode_to_memory(app, idx, {"P1": "4660"})  # 0x1234
    assert mem[_SEG_ID][0:2] == bytes([0x12, 0x34])


def test_encode_to_memory_little_endian_reverses_multi_byte_number() -> None:
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))],
        pt_size=16,
        options=ApplicationProgramStaticOptions(
            parameter_byte_order=(
                ApplicationProgramStaticOptionsParameterByteOrder.LITTLE_ENDIAN
            )
        ),
    )
    mem = encode_to_memory(app, idx, {"P1": "4660"})  # 0x1234
    assert mem[_SEG_ID][0:2] == bytes([0x34, 0x12])


def test_encode_to_memory_little_endian_does_not_reverse_single_byte() -> None:
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))],
        options=ApplicationProgramStaticOptions(
            parameter_byte_order=(
                ApplicationProgramStaticOptionsParameterByteOrder.LITTLE_ENDIAN
            )
        ),
    )
    mem = encode_to_memory(app, idx, {"P1": "255"})
    assert mem[_SEG_ID][0] == 255


# ---------------------------------------------------------------------------
# encode_to_properties
# ---------------------------------------------------------------------------


def test_encode_to_properties_basic() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=2, property_id=57, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p])
    props = encode_to_properties(app, idx, {"P1": "200"})
    assert props[(2, 57, 0)][0] == 200


def test_encode_to_properties_default_value() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=10, occurrence=0, offset=0, bit_offset=0
        ),
        value="99",
    )
    app, idx = _app([p])
    props = encode_to_properties(app, idx, {})
    assert props[(0, 10, 0)][0] == 99


def test_encode_to_properties_empty_when_no_prop_params() -> None:
    app, idx = _app(
        [
            _param(
                "P1",
                MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
                value="1",
            )
        ]
    )
    assert encode_to_properties(app, idx, {}) == {}


def test_encode_to_memory_empty_when_no_mem_params() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=10, occurrence=0, offset=0, bit_offset=0
        ),
        value="1",
    )
    app, idx = _app([p])
    mem = encode_to_memory(app, idx, {})
    assert all(b == 0 for b in mem[_SEG_ID])


def test_encode_to_properties_multiple_params_same_property() -> None:
    # Two params writing to the same property at different offsets
    p1 = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=5, occurrence=0, offset=0, bit_offset=0
        ),
    )
    p2 = _param(
        "P2",
        PropertyParameter(
            object_index=0, property_id=5, occurrence=0, offset=1, bit_offset=0
        ),
    )
    app, idx = _app([p1, p2])
    props = encode_to_properties(app, idx, {"P1": "11", "P2": "22"})
    key = (0, 5, 0)
    assert props[key][0] == 11
    assert props[key][1] == 22


# ---------------------------------------------------------------------------
# Writes container
# ---------------------------------------------------------------------------


def test_writes_starts_empty() -> None:
    w = Writes()
    assert w.mem == []
    assert w.prop == []


# ---------------------------------------------------------------------------
# _encode_value
# ---------------------------------------------------------------------------


def test_encode_number_non_numeric_value_raises() -> None:
    app, idx = _app(
        [_param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))]
    )
    with pytest.raises(EncodingError, match="P1"):
        encode_to_memory(app, idx, {"P1": "not-a-number"})


def _float_tc(encoding: ParameterTypeTypeFloatEncoding) -> ParameterTypeTypeFloat:
    return ParameterTypeTypeFloat(
        encoding=encoding, min_inclusive=-1e10, max_inclusive=1e10
    )


def test_encode_value_float_dpt9() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.DPT_9)
    assert _encode_value("1.0", 16, tc) == 0x0064


def test_encode_value_float_ieee754_single() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.IEEE_754_SINGLE)
    assert _encode_value("1.0", 32, tc) == 0x3F800000


def test_encode_value_float_ieee754_double() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.IEEE_754_DOUBLE)
    assert _encode_value("1.0", 64, tc) == 0x3FF0000000000000


def test_encode_value_float_non_numeric_value_returns_none() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.DPT_9)
    assert _encode_value("not-a-float", 16, tc) is None


def test_encode_value_float_dpt9_shifts_mantissa_when_out_of_range() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.DPT_9)
    assert _encode_value("100.0", 16, tc) == 0x1CE2


def test_encode_value_float_dpt9_returns_none_when_exponent_overflows() -> None:
    tc = _float_tc(ParameterTypeTypeFloatEncoding.DPT_9)
    assert _encode_value("1000000000.0", 16, tc) is None


def _time_tc(unit: ParameterTypeTypeTimeUnit) -> ParameterTypeTypeTime:
    return ParameterTypeTypeTime(
        size_in_bit=16, unit=unit, min_inclusive=0, max_inclusive=65535
    )


def test_encode_value_time_seconds() -> None:
    tc = _time_tc(ParameterTypeTypeTimeUnit.SECONDS)
    assert _encode_value("2", 16, tc) == 2


def test_encode_value_time_non_numeric_value_returns_none() -> None:
    tc = _time_tc(ParameterTypeTypeTimeUnit.SECONDS)
    assert _encode_value("not-a-number", 16, tc) is None


def test_encode_value_time_packed_unit_not_yet_supported() -> None:
    tc = _time_tc(ParameterTypeTypeTimeUnit.PACKED_DAYS_HOURS_MINUTES_AND_SECONDS)
    assert _encode_value("2", 16, tc) is None


def test_encode_value_color_rgb() -> None:
    tc = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB)
    assert _encode_value("#1A2B3C", 24, tc) == 0x1A2B3C


def test_encode_value_color_non_hex_value_returns_none() -> None:
    tc = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB)
    assert _encode_value("not-a-color", 24, tc) is None


def test_encode_value_color_rgbw() -> None:
    tc = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGBW)
    assert _encode_value("#1A2B3C4D", 32, tc) == 0x1A2B3C4D


def test_encode_value_color_hsv_from_pure_red() -> None:
    tc = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.HSV)
    # Pure red -> hue 0, full saturation and value.
    assert _encode_value("#FF0000", 24, tc) == 0x00FFFF


def test_encode_value_color_too_short_returns_none() -> None:
    tc = ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB)
    assert _encode_value("#1A2B", 24, tc) is None


def test_encode_value_date() -> None:
    tc = ParameterTypeTypeDate(encoding=ParameterTypeTypeDateEncoding.DPT_11)
    assert _encode_value("2024-03-05", 24, tc) == (5 << 16) | (3 << 8) | 24


def test_encode_value_date_hides_year_when_not_displayed() -> None:
    tc = ParameterTypeTypeDate(
        encoding=ParameterTypeTypeDateEncoding.DPT_11, display_the_year=False
    )
    assert _encode_value("2024-03-05", 24, tc) == (5 << 16) | (3 << 8)


def test_encode_value_date_invalid_format_returns_none() -> None:
    tc = ParameterTypeTypeDate(encoding=ParameterTypeTypeDateEncoding.DPT_11)
    assert _encode_value("not-a-date", 24, tc) is None


def test_encode_value_ipaddress_v4() -> None:
    tc = ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS
    )
    assert _encode_value("192.168.1.10", 32, tc) == 0xC0A8010A


def test_encode_value_ipaddress_invalid_returns_none() -> None:
    tc = ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS
    )
    assert _encode_value("not-an-address", 32, tc) is None


def test_encode_value_raw_data() -> None:
    tc = ParameterTypeTypeRawData(max_size=4)
    assert _encode_value("DEADBEEF", 32, tc) == 0xDEADBEEF


def test_encode_value_raw_data_pads_short_input() -> None:
    tc = ParameterTypeTypeRawData(max_size=4)
    assert _encode_value("AB", 32, tc) == 0xAB000000


def test_encode_value_raw_data_invalid_hex_returns_none() -> None:
    tc = ParameterTypeTypeRawData(max_size=4)
    assert _encode_value("not-hex", 32, tc) is None


def test_size_in_bit_date() -> None:
    tc = ParameterTypeTypeDate(encoding=ParameterTypeTypeDateEncoding.DPT_11)
    assert _size_in_bit(tc) == 24


def test_size_in_bit_ipaddress_v4_and_v6() -> None:
    v4 = ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS,
        version=ParameterTypeTypeIpaddressVersion.IPV4,
    )
    v6 = ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS,
        version=ParameterTypeTypeIpaddressVersion.IPV6,
    )
    assert _size_in_bit(v4) == 32
    assert _size_in_bit(v6) == 128


def test_size_in_bit_color_rgb_rgbw_hsv() -> None:
    assert (
        _size_in_bit(ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGB))
        == 24
    )
    assert (
        _size_in_bit(ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.RGBW))
        == 32
    )
    assert (
        _size_in_bit(ParameterTypeTypeColor(space=ParameterTypeTypeColorSpace.HSV))
        == 24
    )


def test_size_in_bit_raw_data_uses_max_size() -> None:
    assert _size_in_bit(ParameterTypeTypeRawData(max_size=10)) == 80


def test_encode_value_unhandled_type_choice_returns_none() -> None:
    assert _encode_value("1", 8, object()) is None


def test_encode_text() -> None:
    pt = ParameterType(
        id="PT_TEXT", name="T", choice=ParameterTypeTypeText(size_in_bit=16)
    )
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="PT_TEXT",
        value="",
        choice=MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
    )
    app, idx = _app([p], extra_param_types=[pt])
    mem = encode_to_memory(app, idx, {"P1": "AB"})
    assert mem[_SEG_ID][0:2] == b"AB"


# ---------------------------------------------------------------------------
# resolve_param_values
# ---------------------------------------------------------------------------


def test_resolve_param_values_resolves_via_parameter_ref() -> None:
    p = _param("P1", MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0))
    _app_ignored, idx = _app([p], parameter_refs=[ParameterRef(id="PR1", ref_id="P1")])
    state = GlobalState(values={"PR1": "9"})
    overrides = resolve_param_values(idx, state)
    assert overrides == {"P1": "9"}


def test_resolve_param_values_dangling_ref_raises() -> None:
    _app_ignored, idx = _app(
        [], parameter_refs=[ParameterRef(id="PR1", ref_id="NO_SUCH_PARAM")]
    )
    state = GlobalState(values={"PR1": "9"})
    with pytest.raises(EncodingError, match="PR1"):
        resolve_param_values(idx, state)


# ---------------------------------------------------------------------------
# Module-level collect_writes (via module state tree + module_defs)
# ---------------------------------------------------------------------------


def test_module_memory_param_with_base_value_shift() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                value="10",
                base_value="ARG1",
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    ms = state.module_child(
        "M1", ref_id="MD1", arguments={"ARG1": ModuleNumericArg(ref_id="ARG1", value=5)}
    )
    assert ms is not None
    w = collect_writes(app, idx, {}, state)
    assert len(w.mem) == 1
    assert w.mem[0].value == "15"  # base value 10 + resolved arg 5


def test_module_base_value_arg_missing_leaves_value_unshifted() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                value="10",
                base_value="ARG1",
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")  # no ARG1 in arguments
    w = collect_writes(app, idx, {}, state)
    assert w.mem[0].value == "10"


def test_module_memory_param_base_offset_none_defaults_to_zero() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=3, bit_offset=0, base_offset=None
                ),
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert w.mem[0].offset == 3


def test_module_memory_param_base_offset_unresolvable_raises() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0, base_offset="ARG1"
                ),
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")  # ARG1 not in arguments -> unresolvable
    with pytest.raises(EncodingError, match="MP1"):
        collect_writes(app, idx, {}, state)


def test_module_property_param() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterProperty(
                    object_index=1,
                    occurrence=0,
                    property_id=50,
                    offset=0,
                    bit_offset=0,
                    base_offset="BO",
                    base_index="BI",
                    base_occurrence="BOC",
                ),
                value="7",
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child(
        "M1",
        ref_id="MD1",
        arguments={
            "BO": ModuleNumericArg(ref_id="BO", value=2),
            "BI": ModuleNumericArg(ref_id="BI", value=3),
            "BOC": ModuleNumericArg(ref_id="BOC", value=1),
        },
    )
    w = collect_writes(app, idx, {}, state)
    assert len(w.prop) == 1
    pw = w.prop[0]
    assert pw.object_index == 4  # object_index(1) + base_index(3)
    assert pw.occurrence == 1  # 0 + base_occurrence(1)
    assert pw.offset == 2  # 0 + base_offset(2)
    assert pw.value == "7"


def test_module_property_param_base_unresolvable_raises() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterProperty(
                    object_index=1,
                    occurrence=0,
                    property_id=50,
                    offset=0,
                    bit_offset=0,
                    base_offset="BO",
                    base_index=None,
                    base_occurrence=None,
                ),
                value="7",
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")  # BO not in arguments -> unresolvable
    with pytest.raises(EncodingError, match="MP1"):
        collect_writes(app, idx, {}, state)


def test_module_memory_union_default() -> None:
    md = _module_def(
        "MD1",
        [
            ModuleDefStaticParametersUnion(
                choice=ModuleDefStaticParametersUnionMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                size_in_bit=8,
                parameter=[
                    _union_param("U1", 0, "10", default=True),
                    _union_param("U2", 0, "20"),
                ],
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert len(w.mem) == 1
    assert w.mem[0].param_id == "U1"


def test_module_memory_union_base_offset_unresolvable_raises() -> None:
    md = _module_def(
        "MD1",
        [
            ModuleDefStaticParametersUnion(
                choice=ModuleDefStaticParametersUnionMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0, base_offset="ARG1"
                ),
                size_in_bit=8,
                parameter=[_union_param("U1", 0, "10", default=True)],
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    with pytest.raises(EncodingError, match=_SEG_ID):
        collect_writes(app, idx, {}, state)


def test_module_property_union() -> None:
    md = _module_def(
        "MD1",
        [
            ModuleDefStaticParametersUnion(
                choice=ModuleDefStaticParametersUnionProperty(
                    object_index=0,
                    occurrence=0,
                    property_id=10,
                    offset=0,
                    bit_offset=0,
                ),
                size_in_bit=8,
                parameter=[_union_param("U1", 0, "3", default=True)],
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert len(w.prop) == 1
    assert w.prop[0].param_id == "U1"


def test_module_property_union_base_unresolvable_raises() -> None:
    md = _module_def(
        "MD1",
        [
            ModuleDefStaticParametersUnion(
                choice=ModuleDefStaticParametersUnionProperty(
                    object_index=0,
                    occurrence=0,
                    property_id=10,
                    offset=0,
                    bit_offset=0,
                    base_offset="BO",
                ),
                size_in_bit=8,
                parameter=[_union_param("U1", 0, "3", default=True)],
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")  # BO not in arguments -> unresolvable
    with pytest.raises(EncodingError, match="property 10"):
        collect_writes(app, idx, {}, state)


def test_module_property_union_no_active_or_default_contributes_nothing() -> None:
    # Real product data ships unions with no explicit default when none of their
    # alternatives are meant to be written by default - this is valid, not corruption.
    md = _module_def(
        "MD1",
        [
            ModuleDefStaticParametersUnion(
                choice=ModuleDefStaticParametersUnionProperty(
                    object_index=0, occurrence=0, property_id=10, offset=0, bit_offset=0
                ),
                size_in_bit=8,
                parameter=[_union_param("U1", 0, "3")],  # no default
            )
        ],
    )
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert w.prop == []


def test_app_level_property_union_no_active_or_default_contributes_nothing() -> None:
    union = ApplicationProgramStaticParametersUnion(
        choice=PropertyUnion(
            object_index=0, property_id=10, occurrence=0, offset=0, bit_offset=0
        ),
        size_in_bit=8,
        parameter=[_union_param("U1", 0, "3")],  # no default, no override
    )
    app, idx = _app([union])
    w = collect_writes(app, idx, {})
    assert w.prop == []


def test_module_state_without_ref_id_raises() -> None:
    app, idx = _app([])
    state = GlobalState()
    ms = state.module_child("M1")  # no ref_id
    assert ms.ref_id is None
    with pytest.raises(EncodingError, match="no module def reference"):
        collect_writes(app, idx, {}, state)


def test_module_state_with_unknown_ref_id_raises() -> None:
    app, idx = _app([])
    state = GlobalState()
    state.module_child("M1", ref_id="NO_SUCH_MODULE_DEF")
    with pytest.raises(EncodingError, match="NO_SUCH_MODULE_DEF"):
        collect_writes(app, idx, {}, state)


def test_module_def_without_parameters_contributes_nothing() -> None:
    md = _module_def("MD1", None)
    app, idx = _app([], module_defs=[md])
    state = GlobalState()
    state.module_child("M1", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert w.mem == [] and w.prop == []


def test_nested_submodule_writes_are_collected() -> None:
    parent_md = _module_def("PARENT_MD", None)  # a wrapper with nothing of its own
    child_md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
            )
        ],
    )
    app, idx = _app([], module_defs=[parent_md, child_md])
    state = GlobalState()
    parent = state.module_child("PARENT", ref_id="PARENT_MD")
    parent.module_child("CHILD", ref_id="MD1")
    w = collect_writes(app, idx, {}, state)
    assert len(w.mem) == 1
    assert w.mem[0].param_id == "MP1"


def test_module_instance_overrides_resolve_to_parameter_via_ref() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                value="0",
            )
        ],
    )
    app, idx = _app(
        [], module_defs=[md], parameter_refs=[ParameterRef(id="PR1", ref_id="MP1")]
    )
    state = GlobalState()
    ms = state.module_child("M1", ref_id="MD1")
    ms.param_ref_id_to_value["PR1"] = "42"
    w = collect_writes(app, idx, {}, state)
    assert w.mem[0].value == "42"


def test_module_instance_override_unknown_parameter_ref_raises() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                value="0",
            )
        ],
    )
    app, idx = _app([], module_defs=[md])  # no parameter_refs registered at all
    state = GlobalState()
    ms = state.module_child("M1", ref_id="MD1")
    ms.param_ref_id_to_value["PR_UNKNOWN"] = "42"
    with pytest.raises(EncodingError, match="PR_UNKNOWN"):
        collect_writes(app, idx, {}, state)


def test_module_instance_override_dangling_parameter_ref_raises() -> None:
    md = _module_def(
        "MD1",
        [
            _module_param(
                "MP1",
                ModuleDefStaticParametersParameterMemory(
                    code_segment=_SEG_ID, offset=0, bit_offset=0
                ),
                value="0",
            )
        ],
    )
    app, idx = _app(
        [],
        module_defs=[md],
        parameter_refs=[ParameterRef(id="PR1", ref_id="NO_SUCH_PARAM")],
    )
    state = GlobalState()
    ms = state.module_child("M1", ref_id="MD1")
    ms.param_ref_id_to_value["PR1"] = "42"
    with pytest.raises(EncodingError, match="NO_SUCH_PARAM"):
        collect_writes(app, idx, {}, state)


def test_union_choice_none_raises() -> None:
    union = ApplicationProgramStaticParametersUnion(
        choice=None,
        size_in_bit=8,
        parameter=[_union_param("U1", 0, "1", default=True)],
    )
    app, idx = _app([union])
    with pytest.raises(EncodingError, match="U1"):
        collect_writes(app, idx, {})


# ---------------------------------------------------------------------------
# collect_writes: no static parameters at all
# ---------------------------------------------------------------------------


def test_collect_writes_with_no_static_parameters() -> None:
    app, idx = _app([])
    app_no_params = ApplicationProgram(
        id="APP",
        name="",
        application_number=1,
        application_version=1,
        program_type=app.program_type,
        mask_version="BV20",
        load_procedure_style=app.load_procedure_style,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=ApplicationProgramStatic(
            code=app.static.code,
            parameter_types=app.static.parameter_types,
            parameters=None,
        ),
    )
    w = collect_writes(app_no_params, idx, {})
    assert w.mem == [] and w.prop == []


# ---------------------------------------------------------------------------
# encode_to_memory / build_memory_param_map: unresolvable writes
# ---------------------------------------------------------------------------


def test_encode_to_memory_write_to_unknown_segment_raises() -> None:
    p = _param(
        "P1", MemoryParameter(code_segment="NO_SUCH_SEG", offset=0, bit_offset=0)
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_SEG"):
        encode_to_memory(app, idx, {"P1": "1"})


def test_encode_to_memory_write_with_unknown_parameter_type_raises() -> None:
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="NO_SUCH_PT",
        value="1",
        choice=MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_PT"):
        encode_to_memory(app, idx, {})


def test_build_memory_param_map_basic() -> None:
    p = _param("P1", MemoryParameter(code_segment=_SEG_ID, offset=2, bit_offset=0))
    app, idx = _app([p])
    pmap = build_memory_param_map(app, idx, {"P1": "9"})
    assert pmap[_SEG_ID][2] == ("P1", "9")


def test_build_memory_param_map_unknown_segment_raises() -> None:
    p = _param(
        "P1", MemoryParameter(code_segment="NO_SUCH_SEG", offset=0, bit_offset=0)
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_SEG"):
        build_memory_param_map(app, idx, {"P1": "1"})


def test_build_memory_param_map_unknown_parameter_type_raises() -> None:
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="NO_SUCH_PT",
        value="1",
        choice=MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_PT"):
        build_memory_param_map(app, idx, {})


# ---------------------------------------------------------------------------
# encode_to_properties / build_property_param_map
# ---------------------------------------------------------------------------


def test_encode_to_properties_unknown_parameter_type_raises() -> None:
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="NO_SUCH_PT",
        value="1",
        choice=PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_PT"):
        encode_to_properties(app, idx, {})


def test_encode_to_properties_zero_size_type_raises() -> None:
    pt = ParameterType(
        id="PT_ZERO",
        name="Z",
        choice=ParameterTypeTypeNumber(
            size_in_bit=0,
            type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
            min_inclusive=0,
            max_inclusive=0,
        ),
    )
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="PT_ZERO",
        value="1",
        choice=PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p], extra_param_types=[pt])
    with pytest.raises(EncodingError, match="PT_ZERO"):
        encode_to_properties(app, idx, {})


def test_encode_to_properties_non_numeric_value_raises() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="P1"):
        encode_to_properties(app, idx, {"P1": "not-a-number"})


def test_encode_to_properties_second_write_within_existing_buffer_size() -> None:
    # P1 writes at offset 1 (needs a 2-byte buffer); P2 writes at offset 0
    # (needs only a 1-byte buffer) into the same key - the buffer is already
    # big enough, so the extend branch must not run.
    p1 = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=5, occurrence=0, offset=1, bit_offset=0
        ),
    )
    p2 = _param(
        "P2",
        PropertyParameter(
            object_index=0, property_id=5, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p1, p2])
    props = encode_to_properties(app, idx, {"P1": "11", "P2": "22"})
    key = (0, 5, 0)
    assert props[key][0] == 22
    assert props[key][1] == 11


def test_build_property_param_map_basic() -> None:
    p = _param(
        "P1",
        PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
        value="5",
    )
    app, idx = _app([p])
    pmap = build_property_param_map(app, idx, {})
    assert pmap[(0, 1, 0)][0] == ("P1", "5")


def test_build_property_param_map_unknown_parameter_type_raises() -> None:
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="NO_SUCH_PT",
        value="1",
        choice=PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p])
    with pytest.raises(EncodingError, match="NO_SUCH_PT"):
        build_property_param_map(app, idx, {})


def test_build_property_param_map_zero_size_type_raises() -> None:
    pt = ParameterType(
        id="PT_ZERO",
        name="Z",
        choice=ParameterTypeTypeNumber(
            size_in_bit=0,
            type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
            min_inclusive=0,
            max_inclusive=0,
        ),
    )
    p = ApplicationProgramStaticParametersParameter(
        id="P1",
        name="",
        text="",
        parameter_type="PT_ZERO",
        value="1",
        choice=PropertyParameter(
            object_index=0, property_id=1, occurrence=0, offset=0, bit_offset=0
        ),
    )
    app, idx = _app([p], extra_param_types=[pt])
    with pytest.raises(EncodingError, match="PT_ZERO"):
        build_property_param_map(app, idx, {})
