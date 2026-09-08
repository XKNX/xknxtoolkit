"""UI regression tests for the Configure panel.

Driven by Dear ImGui Test Engine (see `knx_gui.testing.harness`). These open a
real (briefly visible) window, so they need a display and aren't part of the
root `uv run pytest` run (see the root pyproject.toml's `testpaths`) - run
them explicitly:

    uv run pytest src/knx_gui/testing/tests -v
"""

from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace
from typing import cast

from imgui_bundle import hello_imgui, imgui
from imgui_bundle.immapp import testing as imgui_testing

# knx_gui.plugins.node_editor imports knx_gui.widgets before knx_gui.widgets finishes
# initializing if knx_gui.plugins.project (below) is imported first on a fresh
# interpreter - importing knx_gui.main first establishes the same import order the
# app itself uses, side-stepping the circular import. (Sorts first alphabetically too,
# so this also satisfies ruff's import ordering - no noqa needed.)
import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.device import Device
from knx_gui.plugins.project.ui.components import (
    LoadProceduresSection,
    MetadataSection,
    RestartRequest,
    RestartSection,
    render_ui_tree,
)

# Aliased: pytest's default discovery tries to collect any name starting with "Test"
# as a test class, which fails noisily for TestContext (it has an __init__).
from knx_gui.testing.harness import TestContext as _TestContext
from xknxmono.product.parser_v2.ui import UiNode, UiParameter, UiTab
from xknxmono.product.parser_v2.ui.parameter import TextWidget

# Matches the Configure panel's real docked size (see apps/knx-gui/XKNX_Toolkit.ini) -
# the overflows these tests guard against only show up at that width, not a wide window.
_PANEL_SIZE = (417, 477)
_WINDOW_SIZE = (600, 600)


def _fake_metadata_device() -> Device:
    """A duck-typed Device stand-in carrying only what MetadataSection.render() reads
    (device.app.program.*, device.app.manufacturer_id, device.hardware.*) - no
    catalog, no project, no real Application/ApplicationProgram (those are
    xsdata-generated dataclasses with their own required fields, not worth
    constructing just to get a Device past its own __post_init__).

    Several fields are deliberately long (original_manufacturer, hardware.name) -
    that's exactly the kind of content that widened the panel in the original bug,
    so a synthetic worst-case is a more deterministic guard than hoping some demo
    device happens to have wide enough content.

    cast() tells pyright to trust this as a Device rather than loosening
    MetadataSection.render()'s real signature, which should stay strict for actual
    callers.
    """
    program = SimpleNamespace(
        mask_version="MASK0701",
        pei_type=17,
        application_number=1,
        application_version=1,
        program_type=SimpleNamespace(value="Application Program"),
        load_procedure_style=SimpleNamespace(value="Overwriting Load Procedure"),
        linkable=False,
        dynamic_table_management=True,
        is_secure_enabled=False,
        additional_addresses_count=3,
        visible_description="A moderately long description of what this program does",
        original_manufacturer="A Very Long Original Equipment Manufacturer Name GmbH & Co. KG",
    )
    app = SimpleNamespace(
        program=program,
        manufacturer_id="M-0083",
        name="Test Application",
        id="APP-0001",
    )
    hardware = SimpleNamespace(
        is_coupler=False,
        is_power_supply=True,
        is_ip_enabled=False,
        order_number="ORD-1234567890",
        serial_number="SN-0987654321",
        version_number=3,
        bus_current=12.5,
        is_rail_mounted=True,
        width_mm=36.0,
        name="Test Hardware Module With A Fairly Long Name",
        id="HW-0001",
    )
    return cast(Device, SimpleNamespace(app=app, hardware=hardware))


def _assert_no_horizontal_overflow(render: Callable[[], None]) -> None:
    result: dict[str, float] = {}

    def gui_function() -> None:
        imgui.set_next_window_size(imgui.ImVec2(*_PANEL_SIZE))
        imgui.begin("TestPanel")
        render()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        # Content taller than the panel (e.g. many parameters) needs a couple of
        # frames for vertical scroll/layout to settle before scroll_max is final.
        ctx.yield_()
        ctx.yield_()
        window = ctx.get_window_by_ref("//TestPanel")
        result["scroll_max_x"] = window.scroll_max.x

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert result["scroll_max_x"] == 0.0


def test_metadata_section_no_horizontal_overflow() -> None:
    """The Metadata section must not need horizontal scrolling at the docked panel width.

    General sanity guard: catches a column (or anything else in the section)
    growing wide enough to force the whole panel wider than its docked size. Renders
    `MetadataSection` directly rather than through `ConfigurePanel`, so there's no
    Parameters tab bar or Com Flags table in the frame to begin with - isolating the
    Metadata section's own layout from `test_parameters_tab_bar_no_horizontal_overflow`'s
    concern by construction, not by picking a device with few enough parameters. Does
    *not* catch a purely local label/value collision that stays within the window's
    width - see `test_label_column_leaves_room_for_its_own_widest_label` for that.
    """
    device = _fake_metadata_device()
    section = MetadataSection()
    _assert_no_horizontal_overflow(lambda: section.render(device))


def _docked_window_runner_params(
    render_fn: Callable[[], None],
) -> hello_imgui.RunnerParams:
    """A minimal RunnerParams with exactly one genuinely docked window - matching the
    Configure panel's real dock (RightSpace, split off MainDockSpace to the right,
    0.25 ratio) - and nothing else: no KnxGuiApp, no plugins, no catalog, no project.

    Needed for dock-only layout bugs: a plain `imgui.begin()` window, even at a fixed
    size, doesn't reproduce them. Confirmed empirically for the regression this backs
    (`test_parameters_tab_bar_no_horizontal_overflow`) - `scroll_max.x` stayed 0 in a
    bare fixed-size window with the bug's pre-fix code reintroduced, but reached 534px
    in a window built this way, matching what the real docked panel showed (909px,
    back when this was first diagnosed through the full app).
    """
    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_geometry.size = _WINDOW_SIZE
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )

    split_right = hello_imgui.DockingSplit()
    split_right.initial_dock = "MainDockSpace"
    split_right.new_dock = "RightSpace"
    split_right.direction = imgui.Dir.right
    split_right.ratio = 0.25
    runner_params.docking_params.docking_splits = [split_right]

    window = hello_imgui.DockableWindow()
    window.label = "Configure"
    window.dock_space_name = "RightSpace"
    window.gui_function = render_fn
    runner_params.docking_params.dockable_windows = [window]

    return runner_params


def _fake_tabbed_ui(tab_count: int) -> list[UiNode]:
    """`tab_count` UiTabs, each with one parameter - enough tabs at their natural
    width to not fit RightSpace's ~150px (0.25 of the 600px test window)."""
    tabs: list[UiNode] = []
    for i in range(tab_count):
        param = UiParameter(
            ref_id=f"p{i}", label=f"Parameter {i}", value="0", widget=TextWidget()
        )
        tabs.append(
            UiTab(children=(param,), id=f"tab{i}", name=f"Channel {i} Long Name")
        )
    return tabs


def test_parameters_tab_bar_no_horizontal_overflow() -> None:
    """The Parameters tab bar must not need horizontal scrolling at the docked panel width.

    Regression test for a bug where a tab bar's own "ideal" width - every tab
    at its natural, unshrunk width - still counted towards the window's
    content size once tabs didn't fit, even though the tab bar itself
    rendered fine (self-clipped, with scroll arrows). Fixed by containing the
    tab bar in a child window sized to the actually available width (see
    `render_ui_tree` in `knx_gui.plugins.project.ui.components.parameters_section`).

    Builds a genuinely docked window via `_docked_window_runner_params` rather than
    the full app - see its docstring for why a plain fixed-size window can't stand in
    for one here - with enough synthetic tabs to force the overflow deterministically,
    instead of depending on whichever device the demo project happens to default-select.
    """
    device = cast(Device, SimpleNamespace(node_id=1))
    tabs = _fake_tabbed_ui(8)
    result: dict[str, float] = {}

    def render_fn() -> None:
        render_ui_tree(device, tabs, lambda d, p, v: None)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Configure")
        ctx.yield_()
        # Content taller than the panel needs a couple more frames for vertical
        # scroll/layout to settle before scroll_max is final.
        ctx.yield_()
        ctx.yield_()
        window = ctx.get_window_by_ref("//Configure")
        result["scroll_max_x"] = window.scroll_max.x

    imgui_testing.run(
        gui_function=lambda: None,
        test_function=test_function,
        runner_params=_docked_window_runner_params(render_fn),
        exit_after_test=True,
    )

    assert result["scroll_max_x"] == 0.0


def test_label_column_leaves_room_for_its_own_widest_label() -> None:
    """`MetadataSection._label_column` must leave room for its own widest label once
    indented.

    Regression test for the actual bug found via the Test Engine harness:
    `same_line(x)`'s x is measured from the window's own left edge, not from
    the current line's start, so it ignores indent - but every caller renders
    this column one `imgui.indent()` level in. A column smaller than
    `indent_spacing + widest_label_width` lets the value's cursor land before
    the (indent-shifted) label has finished rendering, overlapping it -
    concretely, "Dynamic Table Management" collided with its "No" value.

    A prior version of `_label_column` also capped the column at half the
    available width to guard against overflow that turned out not to
    originate here (see `test_metadata_section_no_horizontal_overflow`);
    in a narrow panel that cap clamped the column *below* the label's own
    width, silently reintroducing the same collision - hence testing the
    invariant directly here instead of only the window-level symptom.

    Reaches into the private `_label_column` directly rather than only
    through `render()`'s public surface, trading some resilience to a future
    rewrite of the column mechanism for a precise, fast, deterministic
    assertion. The alternative (asserting via rendered item rects) isn't
    reliably available here: plain `imgui.text()`/`text_disabled()` calls
    don't get stable IDs, so Test Engine's item-reference APIs can't address
    them individually. If `_label_column` is ever replaced, re-derive an
    equivalent invariant against whatever replaces it rather than deleting
    this test.

    `MetadataSection` being its own component (not a `ConfigurePanel` method)
    is what makes this test possible without a project, a catalog, or even a
    device - just the section and an imgui frame to measure text in.
    """
    section = MetadataSection()
    labels = [
        "Dynamic Table Management",
        "Name",
        "ID",
        "Additional Addresses",
        "Original Manufacturer",
    ]
    result: dict[str, float] = {}

    def gui_function() -> None:
        imgui.begin("TestPanel")
        imgui.indent()
        result["column"] = section._label_column(labels)  # pyright: ignore[reportPrivateUsage]
        result["indent"] = imgui.get_style().indent_spacing
        result["widest"] = max(imgui.calc_text_size(label).x for label in labels)
        imgui.unindent()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert result["column"] >= result["indent"] + result["widest"]


def _fake_restart_device() -> Device:
    """RestartSection.render() only reads device.individual_address (to enable the
    Reset button) and device.name (in the confirmation popup's text) - a real Device
    would need a real Application, which needs a real ApplicationProgram, neither of
    which this test cares about."""
    return cast(Device, SimpleNamespace(individual_address="1.1.1", name="Test Device"))


def test_restart_section_destructive_mode_requires_confirmation() -> None:
    """A destructive reset mode must not fire on the first click - `RestartSection`
    routes it through the "Confirm Reset" popup instead, and only a click inside
    that popup should call `on_restart_device`.

    Drives `_reset_mode_index` directly (see `MetadataSection`'s tests for the same
    trade-off with `_label_column`) rather than operating the mode combo, since the
    combo interaction itself isn't what this test is about.
    """
    device = _fake_restart_device()
    calls: list[RestartRequest] = []
    section = RestartSection(lambda _device, request: calls.append(request))
    section._reset_mode_index = 2  # pyright: ignore[reportPrivateUsage]  # Factory Reset - destructive

    def gui_function() -> None:
        imgui.begin("TestPanel")
        section.render(device)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.item_click("Reset")
        ctx.yield_()
        assert calls == [], "destructive mode must not restart before confirmation"

        ctx.set_ref("//Confirm Reset")
        ctx.item_click("Reset")
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert calls == [RestartRequest(master_reset=True, erase_code=2, channel_number=0)]


def test_restart_section_non_destructive_mode_restarts_immediately() -> None:
    """A non-destructive mode (the default, Basic Restart) must call
    `on_restart_device` straight from the button click, with no confirmation popup."""
    device = _fake_restart_device()
    calls: list[RestartRequest] = []
    section = RestartSection(lambda _device, request: calls.append(request))

    def gui_function() -> None:
        imgui.begin("TestPanel")
        section.render(device)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.item_click("Reset")
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert calls == [RestartRequest(master_reset=False, erase_code=0, channel_number=0)]


def test_load_procedures_section_renders_each_procedures_steps() -> None:
    """`LoadProceduresSection` must render every procedure as an openable tree node
    and not raise while rendering its steps table.

    Uses plain `SimpleNamespace` stand-ins for the load-procedure objects rather than
    real project data: `device.app.load_procedures` is typed as
    `xknxmono.models...LoadProcedures | None`, whose actual `load_procedure` field
    doesn't even match the `.procedures`/`.style` attribute names this section reads
    via `getattr(..., default)` - confirmed empirically against the demo project, none
    of its devices ever populate `.procedures`. That mismatch predates this component
    extraction and is out of scope here; this test exercises the section's own
    rendering contract (duck-typed `lp.style` / `procedures[i].steps[j].{kind,
    applies_to,details}`) independent of whether anything upstream ever fills it in.
    """
    lp = SimpleNamespace(style="Full")
    procedures = [
        SimpleNamespace(
            steps=[
                SimpleNamespace(kind="Connect", applies_to="Full", details="d1"),
                SimpleNamespace(kind="Load", applies_to="Full", details="d2"),
            ]
        )
    ]
    section = LoadProceduresSection()

    def gui_function() -> None:
        imgui.begin("TestPanel")
        section.render(lp, procedures)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_open("Procedure 1  (2 steps)")
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)
