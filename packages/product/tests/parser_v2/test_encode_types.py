"""Unit tests for the per-type value encoders (_encode_value).

Values are checked against the KNX Datapoint Type byte encodings; the integer the
encoder returns is packed big-endian (MSB first) by _write_bits.
"""

from __future__ import annotations

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
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_number_type import (
    ParameterTypeTypeNumberType,
)
from xknxmono.models.intermediate.parameter_type_t_type_raw_data import (
    ParameterTypeTypeRawData,
)
from xknxmono.models.intermediate.parameter_type_t_type_restriction import (
    ParameterTypeTypeRestriction,
)
from xknxmono.models.intermediate.parameter_type_t_type_restriction_enumeration import (
    ParameterTypeTypeRestrictionEnumeration,
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
from xknxmono.product.parser_v2.encode import _encode_value


def _number() -> ParameterTypeTypeNumber:
    return ParameterTypeTypeNumber(
        size_in_bit=8,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=255,
    )


def _float(encoding: ParameterTypeTypeFloatEncoding) -> ParameterTypeTypeFloat:
    return ParameterTypeTypeFloat(encoding=encoding, min_inclusive=0, max_inclusive=0)


def _text() -> ParameterTypeTypeText:
    return ParameterTypeTypeText(size_in_bit=0)


def _date(display_the_year: bool = True) -> ParameterTypeTypeDate:
    return ParameterTypeTypeDate(
        encoding=ParameterTypeTypeDateEncoding.DPT_11,
        display_the_year=display_the_year,
    )


def _ipaddress() -> ParameterTypeTypeIpaddress:
    return ParameterTypeTypeIpaddress(
        address_type=ParameterTypeTypeIpaddressAddressType.HOST_ADDRESS
    )


def _color(space: ParameterTypeTypeColorSpace) -> ParameterTypeTypeColor:
    return ParameterTypeTypeColor(space=space)


def _raw_data() -> ParameterTypeTypeRawData:
    return ParameterTypeTypeRawData(max_size=16)


def test_number_unsigned() -> None:
    assert _encode_value("15", 8, _number()) == 0x0F


def test_number_negative_twos_complement() -> None:
    assert _encode_value("-1", 8, _number()) == 0xFF
    assert _encode_value("-2", 16, _number()) == 0xFFFE


def test_number_invalid_returns_none() -> None:
    assert _encode_value("abc", 8, _number()) is None


def test_float_dpt9() -> None:
    # 21.0 -> 0.01 * 1050 * 2^1; encoded 0x0C1A
    tc = _float(ParameterTypeTypeFloatEncoding.DPT_9)
    assert _encode_value("21.0", 16, tc) == 0x0C1A
    assert _encode_value("0", 16, tc) == 0x0000


def test_float_dpt9_negative() -> None:
    tc = _float(ParameterTypeTypeFloatEncoding.DPT_9)
    # -1.0 -> m = -100, exp 0, sign bit set, 11-bit two's complement of -100
    assert _encode_value("-1.0", 16, tc) == (0x8000 | (-100 & 0x7FF))


def test_float_ieee_single() -> None:
    tc = _float(ParameterTypeTypeFloatEncoding.IEEE_754_SINGLE)
    assert _encode_value("1.0", 32, tc) == 0x3F800000


def test_text_latin1_padded() -> None:
    assert _encode_value("AB", 24, _text()) == 0x414200


def test_text_truncated() -> None:
    assert _encode_value("ABCD", 16, _text()) == 0x4142


def test_date_dpt11() -> None:
    # 2024-03-15 -> day 15, month 3, year%100 = 24
    assert _encode_value("2024-03-15", 24, _date()) == 0x0F0318


def test_ipaddress_v4() -> None:
    assert _encode_value("192.168.1.1", 32, _ipaddress()) == 0xC0A80101


def test_ipaddress_invalid() -> None:
    assert _encode_value("192.168.1", 32, _ipaddress()) is None
    assert _encode_value("1.2.3.999", 32, _ipaddress()) is None


def test_color_rgb() -> None:
    assert _encode_value("#FF8000", 24, _color(ParameterTypeTypeColorSpace.RGB)) == (
        0xFF8000
    )


def test_color_hsv() -> None:
    # #FF8000 (255,128,0) -> H=30.12deg -> 21, S=255, V=255
    assert _encode_value("#FF8000", 24, _color(ParameterTypeTypeColorSpace.HSV)) == (
        0x15FFFF
    )


def test_color_rgbw() -> None:
    assert _encode_value(
        "#FF800040", 32, _color(ParameterTypeTypeColorSpace.RGBW)
    ) == 0xFF800040


def test_raw_data_hex() -> None:
    assert _encode_value("0a0b", 16, _raw_data()) == 0x0A0B


def test_raw_data_padded() -> None:
    assert _encode_value("0a", 16, _raw_data()) == 0x0A00


def test_raw_data_little_endian_length_prefix() -> None:
    # little-endian program: 4 octet little-endian length prefix, then the data
    assert _encode_value("0a0b", 48, _raw_data(), little_endian=True) == 0x020000000A0B


def test_number_little_endian_byte_swap() -> None:
    # 500 = 0x01F4 big-endian; little-endian reverses the two octets
    assert _encode_value("500", 16, _number()) == 0x01F4
    assert _encode_value("500", 16, _number(), little_endian=True) == 0xF401


def test_date_without_year_zeroes_year_octet() -> None:
    assert _encode_value("2024-03-17", 24, _date(display_the_year=False)) == (
        (17 << 16) | (3 << 8)
    )


def test_time_encodes_as_integer() -> None:
    tc = ParameterTypeTypeTime(
        size_in_bit=16,
        unit=ParameterTypeTypeTimeUnit.SECONDS,
        min_inclusive=0,
        max_inclusive=65535,
    )
    assert _encode_value("1000", 16, tc) == 1000
    assert _encode_value("1000", 16, tc, little_endian=True) == 0xE803


def test_restriction_uses_enumeration_binary_value() -> None:
    # An enumeration with an explicit binary value writes those octets verbatim.
    tc = ParameterTypeTypeRestriction(
        base="BinaryValue",
        size_in_bit=24,
        enumeration=[
            ParameterTypeTypeRestrictionEnumeration(
                id="EN-0", value=0, binary_value=b"\x01\x00\x02"
            )
        ],
    )
    assert _encode_value("0", 24, tc) == 0x010002
    # even for a little-endian program the binary value is written as-is
    assert _encode_value("0", 24, tc, little_endian=True) == 0x010002


def test_restriction_without_binary_value_is_numeric() -> None:
    tc = ParameterTypeTypeRestriction(
        base="Value",
        size_in_bit=8,
        enumeration=[ParameterTypeTypeRestrictionEnumeration(id="EN-5", value=5)],
    )
    assert _encode_value("5", 8, tc) == 5
