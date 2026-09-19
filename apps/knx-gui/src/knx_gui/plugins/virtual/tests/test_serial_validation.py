from knx_gui.plugins.virtual.strings import S
from knx_gui.plugins.virtual.ui import (
    _SERIAL_HEX_LENGTH,  # pyright: ignore[reportPrivateUsage]
    _parse_serial,  # pyright: ignore[reportPrivateUsage]
)


def test_parse_serial_returns_bytes_for_valid_twelve_hex_chars() -> None:
    assert _parse_serial("000a2fab1f19") == bytes.fromhex("000a2fab1f19")


def test_parse_serial_returns_none_for_empty_string() -> None:
    assert _parse_serial("") is None


def test_parse_serial_returns_none_for_too_short() -> None:
    assert _parse_serial("00FA") is None
    assert _parse_serial("00FA123456") is None


def test_parse_serial_returns_none_for_too_long() -> None:
    assert _parse_serial("0001020304050607") is None


def test_parse_serial_returns_none_for_odd_length() -> None:
    assert _parse_serial("00FA2F1AB") is None


def test_parse_serial_returns_none_for_non_hex() -> None:
    assert _parse_serial("xyz!@#......") is None


def test_parse_serial_accepts_whitespace_separated() -> None:
    assert _parse_serial("00 fa 12 34 56 78") == bytes.fromhex("00fa12345678")
    assert _parse_serial("00FA12345678") == bytes.fromhex("00fa12345678")


def test_serial_hex_length_is_twelve_for_six_byte_serial() -> None:
    assert _SERIAL_HEX_LENGTH == 12


def test_strings_serial_field_invalid_is_defined() -> None:
    assert S.SERIAL_FIELD_INVALID == "Serial number must be 12 hex characters (6 bytes)"
