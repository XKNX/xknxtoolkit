"""Real-app visibility regression: the Gira "Push-button interface 2-gang comfort"
(M-0008_A-7072-21-5CC3-O000A) — a module-def application (channels + module instances), which is the
case that drives the GUI Configure panel.

Values are the current resolver baseline; this is the test we iterate on as the visible-parameters UI
is refined. Things that already look off and are candidates to fix (assertions flag them):
  - a top-level "Invisible (will be hidden later)" node with ~147 params leaks into the tree,
  - internal params (``_Allg_Pic_*``, ``_General_A_Channel_Configuration_*``) show as visible,
  - channel / com-object names keep an un-substituted ``()`` placeholder.
"""

from pathlib import Path

import pytest

from xknxmono.product import Application, ParamTypeKind, load

_FIXTURE = Path(__file__).parent / "fixtures" / "gira_2gang_button_interface.knxprod"
_APP_ID = "M-0008_A-7072-21-5CC3-O000A"


@pytest.fixture(scope="module")
def app() -> Application:
    return load(_FIXTURE.read_bytes()).applications[_APP_ID]


def test_app_loads(app: Application) -> None:
    assert app.id == _APP_ID
    assert app.name == "Push-button interface 2-gang comfort 707221"
    # the full (unfiltered) sets are huge; visibility must narrow them right down
    assert len(app.parameters()) == 3470
    assert len(app.com_objects()) == 1596


def test_visible_com_objects(app: Application) -> None:
    # a 2-gang device: each channel (K1/K2) exposes an input + output object by default
    names = [co.name for co in app.visible_com_objects()]
    assert names == [
        "K 1 () - Output",
        "K 1 () - Input",
        "K 2 () - Output",
        "K 2 () - Input",
    ]


def test_visible_parameters(app: Application) -> None:
    visible = app.visible_parameters()
    assert len(visible) == 10
    by_text = {p.text: p for p in visible}
    # both channels are enabled by default
    assert by_text["_General_A_Channel_Configuration_K1_Enable"].value == "1"
    assert by_text["_General_A_Channel_Configuration_K2_Enable"].value == "1"

    # UIHint="CheckBox" number types classify as checkboxes (not number inputs)
    def kind(text: str) -> ParamTypeKind | None:
        pt = by_text[text].param_type
        return pt.kind if pt else None

    assert kind("Logic functions") is ParamTypeKind.CHECKBOX
    assert kind("_General_A_Channel_Configuration_K1_Enable") is ParamTypeKind.CHECKBOX


def test_visible_tree(app: Application) -> None:
    tree = app.visible_tree()
    assert [n.display_name for n in tree] == [
        "Invisible (will be hidden later)",
        "Information",
        "General",
        "Channel 1 ()",
        "Channel 2 ()",
    ]
    channel_1 = tree[3]
    assert [c.display_name for c in channel_1.children] == [
        "K 1 - General ()",
        "Application instances",
    ]
