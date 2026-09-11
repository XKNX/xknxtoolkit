from imgui_bundle import imgui

from knx_gui.dpt import (
    DPT,
    DPT_UNKNOWN,
    DPTMatch,
    dpt_color,
    dpt_match,
    lookup_or_make_dpt,
)


def test_dpt_code_pads_minor_to_three_digits() -> None:
    assert DPT(1, 1, "Switch", "switch").code == "1.001"
    assert DPT(5, 23, "x", "y").code == "5.023"


def test_lookup_or_make_dpt_none_is_unknown() -> None:
    assert lookup_or_make_dpt(None) is DPT_UNKNOWN


def test_lookup_or_make_dpt_empty_string_is_unknown() -> None:
    assert lookup_or_make_dpt("") is DPT_UNKNOWN


def test_lookup_or_make_dpt_without_a_dot_is_unknown() -> None:
    assert lookup_or_make_dpt("bad") == DPT_UNKNOWN


def test_lookup_or_make_dpt_with_too_many_parts_is_unknown() -> None:
    assert lookup_or_make_dpt("1.2.3") == DPT_UNKNOWN


def test_lookup_or_make_dpt_non_numeric_parts_is_unknown() -> None:
    assert lookup_or_make_dpt("a.b") == DPT_UNKNOWN


def test_lookup_or_make_dpt_resolves_known_dpt_via_xknx() -> None:
    # DPT 1.001 (Switch): xknx reports value_type="switch", unit=None - unit
    # missing falls back to value_type for the label.
    dpt = lookup_or_make_dpt("1.001")
    assert dpt == DPT(1, 1, "Switch", "switch")


def test_lookup_or_make_dpt_prefers_unit_over_value_type_for_label() -> None:
    # DPT 5.001 (Percent): value_type="percent", unit="%" - unit wins.
    dpt = lookup_or_make_dpt("5.001")
    assert dpt == DPT(5, 1, "Percent", "%")


def test_lookup_or_make_dpt_unregistered_falls_back_to_generic_label() -> None:
    dpt = lookup_or_make_dpt("999.999")
    assert dpt == DPT(999, 999, "DPT 999.999", "999.999")


def test_lookup_or_make_dpt_is_cached_by_code() -> None:
    assert lookup_or_make_dpt("9.001") is lookup_or_make_dpt("9.001")


def test_dpt_color_known_major() -> None:
    color = dpt_color(DPT(1, 1, "Switch", "switch"))
    assert color == imgui.ImVec4(0.9, 0.3, 0.3, 1.0)


def test_dpt_color_unknown_major_falls_back_to_gray() -> None:
    color = dpt_color(DPT(9999, 0, "Nonexistent", "?"))
    assert color == imgui.ImVec4(0.5, 0.5, 0.5, 1.0)


def test_dpt_match_exact_when_major_and_minor_match() -> None:
    a = DPT(9, 1, "Temperature", "°C")
    b = DPT(9, 1, "Temperature", "°C")
    assert dpt_match(a, b) == DPTMatch.EXACT


def test_dpt_match_loose_when_only_major_matches() -> None:
    a = DPT(9, 1, "Temperature", "°C")
    b = DPT(9, 4, "Wind Speed", "m/s")
    assert dpt_match(a, b) == DPTMatch.LOOSE


def test_dpt_match_none_when_major_differs() -> None:
    a = DPT(1, 1, "Switch", "switch")
    b = DPT(5, 1, "Percent", "%")
    assert dpt_match(a, b) == DPTMatch.NONE
