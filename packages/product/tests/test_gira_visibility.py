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
    assert len(visible) == 11
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


def test_visible_grid(app: Application) -> None:
    # "Slat adjusting time": a Layout="Grid" block — value + step params side by side, then a "ms"
    # unit label. Cells are 1-based (row, column) from the IR's ``Cell="r,c"``.
    tree = app.visible_tree()
    k1_general = tree[3].children[0]
    assert k1_general.display_name == "K 1 - General ()"
    (grid_node,) = k1_general.children
    assert grid_node.display_name == "Grid - Slat adjusting time"

    grid = grid_node.grid
    assert grid is not None
    assert grid.columns == 3
    positions = [(c.row, c.column) for c in grid.cells]
    assert positions == [(1, 1), (1, 2), (1, 3)]
    # two parameter cells followed by a static unit label
    assert [c.param_ref_id is not None for c in grid.cells] == [True, True, False]
    assert grid.cells[2].label == "ms"


def test_visible_grid_conditional_cells(app: Application) -> None:
    # "Delay after bus voltage return": a grid whose seconds/ms fields are placed *conditionally*
    # (inside <choose> branches gated by a `>0` test). They must still land in their cells, each
    # followed by its unit label — proving choose-cells and comparison-operator tests both resolve.
    general = next(n for n in app.visible_tree() if n.display_name == "General")
    grid_node = next(c for c in general.children if c.grid and c.grid.columns == 7)
    assert grid_node.grid is not None
    cells = grid_node.grid.cells
    assert [(c.row, c.column) for c in cells] == [
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
    ]
    # alternating fields and unit labels: <field> <field> "min" <field> "s" <field> "ms"
    assert [c.label for c in cells] == [None, None, "min", None, "s", None, "ms"]


def test_channel_name_fills_placeholder(app: Application) -> None:
    # The "Name" parameter fills the {{0}} placeholder in channel/com-object names: with it empty
    # the names show the bare "()" ETS shows by default; set it and the value appears.
    name_param = "M-0008_A-7072-21-5CC3-O000A_MD-1_P-1_R-1"

    assert [co.name for co in app.visible_com_objects()] == [
        "K 1 () - Output",
        "K 1 () - Input",
        "K 2 () - Output",
        "K 2 () - Input",
    ]

    values = dict(app.default_values())
    values[name_param] = "Hallway"
    named = [co.name for co in app.visible_com_objects(values)]
    assert named[0] == "K 1 (Hallway) - Output"
    assert [n.display_name for n in app.visible_tree(values)][
        3
    ] == "Channel 1 (Hallway)"


def test_visible_table(app: Application) -> None:
    # The "Channels" block is Layout="Table": a per-channel grid with column headers (Use/Combine)
    # and row headers (K1/K2). Modelled as a GridLayout that carries the header text.
    general = next(n for n in app.visible_tree() if n.display_name == "General")
    table = next(c for c in general.children if c.display_name == "Channels")
    grid = table.grid
    assert grid is not None
    assert grid.column_headers == ["Use", "Combine"]
    assert grid.row_headers == ["K1", "K2"]
    # K1's "Use" + "Combine" and K2's "Use" are placed (K2 "Combine" is conditionally hidden)
    assert {(c.row, c.column) for c in grid.cells if c.param_ref_id} == {
        (1, 1),
        (1, 2),
        (2, 1),
    }
