"""DynamicUI regression tests against the real Gira Push-button interface 2-gang comfort
(M-0008_A-7072-21-5CC3-O000A) - see test_encode.py's docstring for the same fixture used
there. This file covers DynamicUI's own wrapper methods (module instances, com-object
instance overrides, segment addresses, property encoding) and set_parameter_ref's L<->R
calculation propagation, none of which test_encode.py's encode-focused tests exercise."""

from pathlib import Path

import pytest

from xknxmono.models.intermediate import ComObjectInstanceRef
from xknxmono.product import load
from xknxmono.product.parser_v2.dynamic import DynamicUI

_FIXTURE = (
    Path(__file__).parent.parent / "fixtures" / "gira_2gang_button_interface.knxprod"
)
_APP_ID = "M-0008_A-7072-21-5CC3-O000A"

# An active param ref whose value drives an L->R JavaScript calculation.
_L_CALC_REF_ID = "M-0008_A-7072-21-5CC3-O000A_P-106_R-153"
# An active param ref whose value drives an R->L JavaScript calculation.
_R_CALC_REF_ID = "M-0008_A-7072-21-5CC3-O000A_P-7_R-3"


@pytest.fixture()
def dui() -> DynamicUI:
    app = load(_FIXTURE.read_bytes()).applications[_APP_ID]
    d = app.dynamic_ui()
    assert d is not None
    d.ui()  # populate active refs / module instances
    return d


def test_get_module_instances_returns_top_level_modules(dui: DynamicUI) -> None:
    instances = dui.get_module_instances()
    assert len(instances) > 0
    for instance_id, ref_id in instances:
        assert instance_id.startswith(_APP_ID)
        assert ref_id.startswith(_APP_ID)


def test_segment_base_addrs_covers_every_code_segment(dui: DynamicUI) -> None:
    addrs = dui.segment_base_addrs()
    assert addrs == {"M-0008_A-7072-21-5CC3-O000A_RS-04-00000": 0}


def test_set_com_obj_instance_ref_invalidates_cached_ui(dui: DynamicUI) -> None:
    dui.ui()
    assert dui._ui is not None  # pyright: ignore[reportPrivateUsage]
    coir = ComObjectInstanceRef(ref_id="CO-TEST")
    dui.set_com_obj_instance_ref("SOME_CO_REF", coir)
    assert dui._ui is None  # pyright: ignore[reportPrivateUsage]
    assert dui._state.get_com_obj_instance_ref("SOME_CO_REF") is coir  # pyright: ignore[reportPrivateUsage]


def test_encode_to_properties_produces_property_writes(dui: DynamicUI) -> None:
    props = dui.encode_to_properties()
    assert len(props) > 0
    for value in props.values():
        assert isinstance(value, bytes)


def test_property_param_map_matches_encoded_properties(dui: DynamicUI) -> None:
    props = dui.encode_to_properties()
    pmap = dui.property_param_map()
    assert set(pmap.keys()) == set(props.keys())
    for key, byte_map in pmap.items():
        assert len(byte_map) > 0
        for offset in byte_map:
            assert offset < len(props[key])


def test_set_parameter_ref_rejects_inactive_ref(dui: DynamicUI) -> None:
    with pytest.raises(ValueError, match="not active"):
        dui.set_parameter_ref("M-0008_A-7072-21-5CC3-O000A_P-999999_R-999999", "1")


def test_set_parameter_ref_propagates_l_to_r_calculation(dui: DynamicUI) -> None:
    before = dui._state.get(_L_CALC_REF_ID)  # pyright: ignore[reportPrivateUsage]
    new_value = "0" if before == "1" else "1"
    dui.set_parameter_ref(_L_CALC_REF_ID, new_value)
    assert dui._state.get(_L_CALC_REF_ID) == new_value  # pyright: ignore[reportPrivateUsage]


def test_set_parameter_ref_propagates_r_to_l_calculation(dui: DynamicUI) -> None:
    before = dui._state.get(_R_CALC_REF_ID)  # pyright: ignore[reportPrivateUsage]
    new_value = "0" if before == "1" else "1"
    dui.set_parameter_ref(_R_CALC_REF_ID, new_value)
    assert dui._state.get(_R_CALC_REF_ID) == new_value  # pyright: ignore[reportPrivateUsage]
