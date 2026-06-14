"""Module-instance resolution + `ApplicationInstance`, against the Gira 2-gang button interface.

The two channels K1/K2 are instances of module def MD-1; ETS encodes them as `MD-1_M-100_MI-1` /
`MD-1_M-200_MI-1` and splices that into each member ref. These tests pin that encoding and the
per-instance independence that fixes the "naming one channel renames both" bug.
"""

from pathlib import Path

import pytest

from xknxmono.product import (
    Application,
    ApplicationInstance,
    PersistedParam,
    load,
)
from xknxmono.product.instance import InstanceSnapshot, ValidationError
from xknxmono.product.parser.instantiate import instantiate

_FIXTURE = Path(__file__).parent / "fixtures" / "gira_2gang_button_interface.knxprod"
_APP_ID = "M-0008_A-7072-21-5CC3-O000A"
_K1_NAME = f"{_APP_ID}_MD-1_M-100_MI-1_P-1_R-1"  # channel 1 "Name" param uid
_K2_NAME = f"{_APP_ID}_MD-1_M-200_MI-1_P-1_R-1"


@pytest.fixture(scope="module")
def app() -> Application:
    return load(_FIXTURE.read_bytes()).applications[_APP_ID]


def test_instances_are_distinct(app: Application) -> None:
    instances, _tree = instantiate(app.program)
    params = {uid: pi for inst in instances for uid, pi in inst.parameters.items()}
    # both channels' Name params exist with distinct uids and instance paths
    k1, k2 = params[_K1_NAME], params[_K2_NAME]
    assert k1.module_instance_path == "MD-1_M-100_MI-1"
    assert k2.module_instance_path == "MD-1_M-200_MI-1"
    assert k1.base_ref_id == k2.base_ref_id == f"{_APP_ID}_MD-1_P-1_R-1"
    # the application itself is the "" bundle in the same flat list
    assert any(inst.module_instance_path == "" for inst in instances)


def test_text_args_of_derivation() -> None:
    # folding text_args into arguments: text_args_of derives the {{ArgName}} substitution map
    # from the full argument list — named args (text or numeric) keyed by name, an un-named text
    # arg without "_A-" keyed by its id (nested-module passthrough), empty values skipped.
    from xknxmono.product.parser.modules import ModuleArgument, text_args_of

    args = [
        ModuleArgument(
            id="X_A-15", name="ArgBeschriftung", is_numeric=False, value="1"
        ),
        ModuleArgument(id="X_A-2", name="ObjNumberBase", is_numeric=True, value="253"),
        ModuleArgument(id="X_A-9", name="", is_numeric=False, value="x"),  # _A- → skip
        ModuleArgument(
            id="Sub-1", name="", is_numeric=False, value="y"
        ),  # passthrough by id
        ModuleArgument(
            id="X_A-7", name="Empty", is_numeric=False, value=""
        ),  # empty → skip
    ]
    assert text_args_of(args) == {
        "ArgBeschriftung": "1",
        "ObjNumberBase": "253",
        "Sub-1": "y",
    }


def test_naming_one_channel_is_independent(app: Application) -> None:
    inst = ApplicationInstance(app)
    inst.set_param(_K1_NAME, "Hallway")
    tree = inst.visible_tree()
    top = [n.display_name for n in tree]
    assert "Channel 1 (Hallway)" in top
    assert "Channel 2 ()" in top  # K2 untouched
    # com-objects follow their own channel
    co_names = {co.name for co in inst.visible_com_objects()}
    assert "K 1 (Hallway) - Output" in co_names
    assert "K 2 () - Output" in co_names


def test_persisted_values_load_per_instance(app: Application) -> None:
    inst = ApplicationInstance(
        app,
        param_values=[
            PersistedParam("MD-1_M-200_MI-1", f"{_APP_ID}_MD-1_P-1_R-1", "Kitchen")
        ],
    )
    assert inst.value(_K2_NAME) == "Kitchen"
    assert inst.value(_K1_NAME) == ""  # default


def test_set_param_validates_and_persists(app: Application) -> None:
    captured: list[InstanceSnapshot] = []
    inst = ApplicationInstance(app, on_persist=captured.append)

    inst.set_param(_K1_NAME, "Office")
    assert captured  # persist callback fired
    snap = captured[-1]
    assert any(
        p.module_instance_path == "MD-1_M-100_MI-1" and p.value == "Office"
        for p in snap.parameters
    )

    # a number param out of range is rejected and not persisted
    before = len(captured)
    k1_enable = f"{_APP_ID}_P-15_R-14"  # app-level checkbox
    with pytest.raises(ValidationError):
        inst.set_param(k1_enable, "7")
    assert len(captured) == before
