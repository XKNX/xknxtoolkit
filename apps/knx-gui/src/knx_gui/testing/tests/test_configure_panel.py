"""UI regression tests for the Configure panel.

Driven by Dear ImGui Test Engine (see `knx_gui.testing.harness`). These open a
real (briefly visible) window, so they need a display and aren't part of the
root `uv run pytest` run (see the root pyproject.toml's `testpaths`) - run
them explicitly:

    uv run pytest src/knx_gui/testing/tests -v
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future
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
from knx_gui.device import ComObject, Device
from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui.components import (
    LoadProceduresSection,
    MetadataSection,
    ProgramRequest,
    ProgramSection,
    RestartRequest,
    RestartSection,
    render_ui_tree,
)
from knx_gui.plugins.project.ui.components.program_section import (
    _limit_serial_length,  # pyright: ignore[reportPrivateUsage]
)
from knx_gui.plugins.project.ui.configure import ConfigurePanel

# Aliased: pytest's default discovery tries to collect any name starting with "Test"
# as a test class, which fails noisily for TestContext (it has an __init__).
from knx_gui.testing.harness import TestContext as _TestContext
from knx_gui.widgets import render_bounded_numeric_segment
from xknxmono.product.parser_v2.ui import UiNode, UiParameter, UiParameterBlock, UiTab
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


def test_parameter_block_with_no_visible_parameters_is_not_rendered() -> None:
    """A ParameterBlock whose every parameter is Access="None" (never user-visible -
    e.g. a manufacturer's internal bookkeeping block) reaches here with an empty
    `children` tuple, since `ParameterRefRefNode.eval()` already filtered them out.
    Showing an empty section header for one (as a real ABB product's "DUMMY" block
    did) is worse than not showing the section at all.

    Compares against a baseline window with no nodes at all rather than asserting
    on a specific pixel size (or on item presence - Dear ImGui Test Engine's
    `item_exists`/`item_info`/`gather_items` all reported this section's own tree
    node as absent even right after confirming via a screenshot that it was on
    screen and `item_open` could reach it; the window-size delta these overflow
    tests elsewhere in this file already rely on doesn't have that problem).
    """
    device = cast(Device, SimpleNamespace(node_id=1))
    block = UiParameterBlock(id="pb-empty", children=(), text="DUMMY")

    def gui_function() -> None:
        imgui.begin("Baseline")
        render_ui_tree(device, [], lambda d, p, v: None)
        imgui.end()
        imgui.begin("WithEmptyBlock")
        render_ui_tree(device, [block], lambda d, p, v: None)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Baseline")
        ctx.yield_()
        baseline = ctx.get_window_by_ref("//Baseline")
        with_block = ctx.get_window_by_ref("//WithEmptyBlock")
        assert with_block.size.y == baseline.size.y

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)


def test_parameter_block_with_visible_parameters_is_still_rendered() -> None:
    """Sanity counterpart to the empty-block test above - a block that does have a
    visible parameter must still grow the window with its section header, unlike
    the empty case."""
    device = cast(Device, SimpleNamespace(node_id=1))
    param = UiParameter(
        ref_id="p0", label="Parameter 0", value="0", widget=TextWidget()
    )
    block = UiParameterBlock(id="pb-full", children=(param,), text="General")

    def gui_function() -> None:
        imgui.begin("Baseline")
        render_ui_tree(device, [], lambda d, p, v: None)
        imgui.end()
        imgui.begin("WithBlock")
        render_ui_tree(device, [block], lambda d, p, v: None)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Baseline")
        ctx.yield_()
        baseline = ctx.get_window_by_ref("//Baseline")
        with_block = ctx.get_window_by_ref("//WithBlock")
        assert with_block.size.y > baseline.size.y

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)


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


def _fake_full_configure_device() -> Device:
    """Enough surface for `ConfigurePanel.render()` to complete a full frame:
    `MetadataSection` renders by default (open), so it needs the same app/hardware
    shape as `_fake_metadata_device()`; `app.load_procedures=None` short-circuits the
    Load Procedures section (covered separately above); `get_ui`/
    `get_visible_com_objects` return empty so the Parameters/Com Flags sections have
    nothing to render - none of that is what this test is about."""
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
        visible_description="",
        original_manufacturer="",
    )
    app = SimpleNamespace(
        program=program,
        manufacturer_id="M-0083",
        name="Test Application",
        id="APP-0001",
        load_procedures=None,
    )
    return cast(
        Device,
        SimpleNamespace(
            node_id=1,
            name="Test Device",
            individual_address="1.1.1",
            app=app,
            hardware=None,
            get_ui=lambda: cast(list[UiNode], []),
            get_visible_com_objects=lambda: cast(list[ComObject], []),
        ),
    )


def test_advanced_actions_section_contains_preview_memory_button() -> None:
    """ "Preview Memory" moved out of its old standalone spot above Metadata into the
    Advanced Actions header, alongside Reset Device - regression guard that it's
    still reachable there and still opens the preview for the selected device."""
    device = _fake_full_configure_device()
    opened: list[Device] = []
    panel = ConfigurePanel(
        get_devices=lambda: [device],
        get_selected_device=lambda: device,
        set_selected_device=lambda _device: None,
        on_param_change=lambda _device, _ref_id, _value: None,
        on_individual_address_change=lambda _device, _address: None,
        on_name_change=lambda _device, _name: None,
        set_flag=lambda _device, _co_id, _flag, _value: None,
        open_memory_preview=opened.append,
    )

    def gui_function() -> None:
        imgui.begin("TestPanel")
        panel.render()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_open(S.CONFIGURE_RESET_SECTION)
        ctx.yield_()
        ctx.item_click(S.BTN_PREVIEW_MEMORY)
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert opened == [device]


def _make_ia_panel(
    device: Device,
    on_individual_address_change: Callable[[Device, str], None],
) -> ConfigurePanel:
    """A ConfigurePanel wired up just enough to drive the segmented Individual
    Address input in isolation.

    Pre-seeds the three segment buffers to ``"0"`` and the device's address to
    ``"0.0.0"`` (and pins ``_buffer_device_id`` so the panel's per-device one-shot
    re-sync doesn't overwrite them on the first render frame): the input starts
    each segment at ``"0"``, so typing a single digit appends to ``"0d"`` and the
    segment's clamping callback rewrites that to ``"d"`` deterministically
    regardless of where in the field the cursor lands after ``item_click`` -
    avoiding the ``"1" + "d" = "1d" -> clamp(1d, 15) = 15`` ambiguity of a
    ``1.1.1`` start, where the result depends on cursor position. The
    ``"0.0.0"`` baseline matches the segment buffers so the panel's "re-sync
    when nothing is active and the assembled address differs" branch isn't
    triggered before the user starts typing.
    """
    device.individual_address = "0.0.0"
    panel = ConfigurePanel(
        get_devices=lambda: [device],
        get_selected_device=lambda: device,
        set_selected_device=lambda _device: None,
        on_param_change=lambda _device, _ref_id, _value: None,
        on_individual_address_change=on_individual_address_change,
        on_name_change=lambda _device, _name: None,
        set_flag=lambda _device, _co_id, _flag, _value: None,
    )
    panel._ia_area = "0"  # pyright: ignore[reportPrivateUsage]
    panel._ia_line = "0"  # pyright: ignore[reportPrivateUsage]
    panel._ia_device = "0"  # pyright: ignore[reportPrivateUsage]
    panel._buffer_device_id = device.node_id  # pyright: ignore[reportPrivateUsage]
    return panel


def _run_ia_panel_driving_test(
    panel: ConfigurePanel,
    test_function: Callable[[_TestContext], None],
) -> None:
    def gui_function() -> None:
        imgui.begin("TestPanel")
        panel.render()
        imgui.end()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)


def test_individual_address_chained_edit_commits_once() -> None:
    """A chained Area -> Line -> Device edit of the segmented Individual Address
    must produce a single ``on_individual_address_change`` call carrying the
    *final* assembled address, not one per-segment deactivation.

    Regression test for commit 1ab42e3's segmented IA input, which committed on
    ``area.deactivated or line.deactivated or dev.deactivated`` instead of
    waiting until no segment remained active. The per-segment ``deactivated``
    flag (a thin wrapper around ``imgui.is_item_deactivated_after_edit()``)
    fires on every segment boundary during the chaining click Area -> click
    Line -> click Device -> click elsewhere edit flow, so a one-shot edit of
    ``0.0.0`` to ``8.5.9`` previously produced three callbacks -
    ``(1, "8.0.0"), (1, "8.5.0"), (1, "8.5.9")`` - the first two being
    *intermediate* partial addresses built from the just-typed segment plus the
    other two still holding the old address. Each callback drives the project
    plugin's optimistic ``device.individual_address = new_address`` mutation and
    (topology-dependent) one ``EventStore`` append per intermediate, so an
    intended one-keystroke edit could need multiple undo presses to revert and
    made the per-frame dropdown label flicker through intermediate addresses.

    Drives the real ``ConfigurePanel.render`` through the real Dear ImGui Test
    Engine harness, recording ``on_individual_address_change`` invocations via
    a stub callback - it measures UI-layer commit attempts, which is what the
    buggy ``or``-of-``deactivated`` condition directly controls.
    """
    device = _fake_full_configure_device()
    calls: list[tuple[int, str]] = []

    panel = _make_ia_panel(
        device, lambda dev, address: calls.append((dev.node_id, address))
    )

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        # Click each segment, type one digit, advance to the next by clicking
        # the following segment - the click-through flow the widget was designed
        # for. Final click on ##name moves focus out of the whole composite.
        for label, ch in [("##ia_area", "8"), ("##ia_line", "5"), ("##ia_device", "9")]:
            ctx.item_click(label)
            ctx.yield_()
            ctx.key_chars(ch)
            ctx.yield_()
        ctx.item_click("##name")
        ctx.yield_()
        ctx.yield_()

    _run_ia_panel_driving_test(panel, test_function)

    assert calls == [(1, "8.5.9")], (
        f"chained IA edit must fire exactly one final commit, got {calls}"
    )


def test_individual_address_single_segment_edit_commits_once() -> None:
    """A single-segment edit (Area only, then deactivate by clicking another
    focusable item) must still commit exactly once - regression guard that the
    fix's "and no segment is still active" guard does NOT also suppress the
    classic single-octet commit-on-blur behaviour the segmented widget inherited
    from the single-field IA input it replaced (commit ``1ab42e3``).

    Per-segment commit-on-blur is what a user gets when they, e.g., only meant
    to fix the Area part of an address - skipping it would silently swallow that
    edit. The fix only suppresses *intermediate* commits during a chained
    multi-segment edit, where on the boundary frame the next segment is already
    active; here nothing else takes over as a segment, so the single commit
    fires identically under the buggy code and the fix. The bug report scopes
    that out as an orthogonal design question; this test pins its current
    behaviour against the fix changing it.
    """
    device = _fake_full_configure_device()
    calls: list[tuple[int, str]] = []

    panel = _make_ia_panel(
        device, lambda dev, address: calls.append((dev.node_id, address))
    )

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##ia_area")
        ctx.yield_()
        ctx.key_chars("8")  # 0 + 8 -> clamped to "8"
        ctx.yield_()
        # Click another focusable item to deactivate the area segment without
        # activating the line or device segments.
        ctx.item_click("##name")
        ctx.yield_()
        ctx.yield_()

    _run_ia_panel_driving_test(panel, test_function)

    assert calls == [(1, "8.0.0")], (
        f"single-segment IA edit must still commit once on blur, got {calls}"
    )


def test_individual_address_external_change_resyncs_buffers_when_idle() -> None:
    """When none of the three segments is being edited and the device's
    ``individual_address`` changes from outside the widget (e.g. an undo
    jump, a drag-to-a-new-line in the Devices panel, or a successful
    Individual Address programming), the panel must re-sync its three segment
    buffers to the new address on the next frame.

    Regression guard for the ``elif`` half of the fix: switching the commit
    condition to "segment deactivated AND no segment still active" must not
    silently drop the existing re-sync-from-outside path - the two were always
    mutually exclusive (one fires on edit completion, the other on idle-state
    drift), and they remain so after the fix just with a tighter commit guard.
    """
    device = _fake_full_configure_device()  # individual_address == "1.1.1"
    panel = ConfigurePanel(
        get_devices=lambda: [device],
        get_selected_device=lambda: device,
        set_selected_device=lambda _device: None,
        on_param_change=lambda _device, _ref_id, _value: None,
        on_individual_address_change=lambda _device, _address: None,
        on_name_change=lambda _device, _name: None,
        set_flag=lambda _device, _co_id, _flag, _value: None,
    )

    def gui_function() -> None:
        imgui.begin("TestPanel")
        panel.render()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()  # first frame: per-device one-shot sync -> buffers = "1","1","1"
        # Simulate an external change (undo / drag / programming completion):
        # nothing the test does touches the IA segments, so the panel should
        # notice the drift and re-sync.
        device.individual_address = "5.5.5"
        ctx.yield_()  # else-branch fires -> _sync_address_buffers("5.5.5")
        ctx.yield_()  # let layout settle one more frame

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert panel._ia_area == "5"  # pyright: ignore[reportPrivateUsage]
    assert panel._ia_line == "5"  # pyright: ignore[reportPrivateUsage]
    assert panel._ia_device == "5"  # pyright: ignore[reportPrivateUsage]


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


def _fake_program_device() -> Device:
    """`ProgramSection.render()` only reads `device.individual_address` (for the
    checklist's "Write Individual Address" line) and `device.name` (the status
    header) - no real Application/ApplicationProgram needed."""
    return cast(Device, SimpleNamespace(individual_address="1.1.4", name="Test Device"))


def _run_program_section(
    section: ProgramSection,
    device: Device,
    test_function: Callable[[_TestContext], None],
) -> str:
    """Owns the `serial_hex` buffer across frames the way `ConfigurePanel` does -
    `render()` returns it back since Step 1 can edit it inline. Returns the
    buffer's final value once the test finishes."""
    serial = ""

    def gui_function() -> None:
        nonlocal serial
        imgui.begin("TestPanel")
        serial = section.render(device, serial)
        imgui.end()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)
    return serial


def test_program_section_button_trigger_advances_to_mode_step() -> None:
    """The default trigger (Programming Button) needs no input, so Next must be
    enabled immediately - regression guard for `can_advance`'s gating logic."""
    device = _fake_program_device()
    section = ProgramSection(lambda _device, _request: None)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.BTN_NEXT)
        ctx.yield_()

    _run_program_section(section, device, test_function)

    assert section._step == "mode"  # pyright: ignore[reportPrivateUsage]


def test_program_section_serial_trigger_blocks_advance_until_valid() -> None:
    """Next must stay disabled (so clicking it is a no-op) while the Serial Number
    trigger's field is empty - `_parse_serial` requires exactly 12 hex chars."""
    device = _fake_program_device()
    section = ProgramSection(lambda _device, _request: None)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.PROGRAM_TRIGGER_SERIAL)
        ctx.yield_()
        ctx.item_click(S.BTN_NEXT)
        ctx.yield_()

    _run_program_section(section, device, test_function)

    assert section._step == "find_device"  # pyright: ignore[reportPrivateUsage]


def test_program_section_serial_field_caps_at_twelve_hex_chars() -> None:
    """End-to-end: typing 16 hex characters through the real Step 1 flow
    (trigger card -> field) must leave `render()` returning only the first
    12 - confirms `_render_find_device` actually wires its field up to the
    capping callback, not just that the callback itself works in isolation
    (see `test_limit_serial_length_callback_caps_the_live_buffer` for that)."""
    device = _fake_program_device()
    section = ProgramSection(lambda _device, _request: None)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.PROGRAM_TRIGGER_SERIAL)
        ctx.yield_()
        ctx.item_click("##program_serial")
        for ch in "00FA1234567890AB":  # 16 hex chars, only 12 fit
            ctx.key_chars(ch)
        ctx.yield_()

    serial = _run_program_section(section, device, test_function)

    assert serial == "00FA12345678"


def test_limit_serial_length_callback_caps_the_live_buffer() -> None:
    """`_limit_serial_length` must cap Dear ImGui's *own* edit buffer as the
    user types, not just the string a caller reads back afterward - a
    focused `input_text()` keeps its own buffer and ignores whatever value
    is passed back in on later frames (confirmed via the harness: a naive
    "trim the string `render()` returns" approach never shrinks what's
    actually displayed while typing, even though - misleadingly - the value
    an external caller eventually reads still comes out correctly capped,
    since that caller's own trim re-applies every frame regardless of what
    Dear ImGui does internally).

    Exercises the callback through a real `input_text()` rather than
    `ProgramSection` directly, so the assertion is about the callback's own
    contract; types one character per frame (not one batched `key_chars`
    call, which Dear ImGui treats as a single paste-like edit and so never
    exercises the multi-frame "still focused" case at all).
    """
    observed_lengths: list[int] = []

    def spy(data: imgui.InputTextCallbackData) -> int:
        _limit_serial_length(data)
        observed_lengths.append(data.buf_text_len)
        return 0

    value = ""

    def gui_function() -> None:
        nonlocal value
        imgui.begin("TestPanel")
        _, value = imgui.input_text(
            "##serial",
            value,
            flags=imgui.InputTextFlags_.chars_hexadecimal
            | imgui.InputTextFlags_.callback_edit,
            callback=spy,
        )
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##serial")
        for ch in "00FA1234567890AB":  # 16 hex chars, only 12 fit
            ctx.key_chars(ch)
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert observed_lengths, "callback never fired - test isn't exercising typing"
    assert max(observed_lengths) == 12
    assert value == "00FA12345678"


def test_ia_segment_strips_unicode_superscript_and_subscript_digits() -> None:
    """Regression: ``str.isdigit()`` returns True for Unicode superscripts and
    subscripts (² ³ ¹ ₂ …) that ``int()`` rejects, so ``render_bounded_numeric_segment``'s
    ``callback_edit`` cleanup used to feed such a live buffer straight into
    ``int(...)``, raising ``ValueError`` out of the per-frame imgui callback.
    The exception fires mid-frame, so ``imgui.end()`` (and the rest of
    ``ConfigurePanel.render``) is skipped; on the next frame Dear ImGui's
    ``Begin()`` trips ``IM_ASSERT("Missing End()")`` and the process dies with
    SIGSEGV (139) - the application is lost from a single keystroke/paste.

    Typing those numerals must instead be silently stripped to ASCII digits
    only, per the widget's docstring promise that "any non-digit character is
    corrected live" - and must not raise.

    Drives the real ``render_bounded_numeric_segment`` (the production code
    path used by ``ConfigurePanel.render``) through a real
    ``imgui.input_text_with_hint``; one char per ``key_chars`` call mirrors
    ``test_limit_serial_length_callback_caps_the_live_buffer``.
    """
    value = ""

    def gui_function() -> None:
        nonlocal value
        imgui.begin("TestPanel")
        result = render_bounded_numeric_segment("##ia_area", value, 2, 15)
        value = result.value
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##ia_area")
        # Superscripts 2/3/1 and a subscript 2: isdigit()=True, int()-rejects.
        for ch in "\u00b2\u00b3\u00b9\u2082":
            ctx.key_chars(ch)
        ctx.yield_()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert value == ""


def test_program_section_reports_request_and_marks_checklist_done_on_success() -> None:
    """A full click-through (button trigger, default Full scope) must call
    `on_program` with the request it displayed, and a successful `Future` must
    flip the Individual Address checklist entry from "current" to "done"."""
    device = _fake_program_device()
    calls: list[ProgramRequest] = []
    future: Future[None] = Future()

    def on_program(_device: Device, request: ProgramRequest) -> Future[None] | None:
        calls.append(request)
        return future

    section = ProgramSection(on_program)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.BTN_NEXT)
        ctx.yield_()
        ctx.item_click(S.BTN_PROGRAM)
        ctx.yield_()

    _run_program_section(section, device, test_function)

    assert calls == [
        ProgramRequest(
            trigger="button",
            serial=None,
            program_individual_address=True,
            program_group_addresses=True,
            program_parameters=True,
        )
    ]
    assert section._status == "running"  # pyright: ignore[reportPrivateUsage]

    future.set_result(None)

    assert section._status == "success"  # pyright: ignore[reportPrivateUsage]
    ia_index = section._ia_checklist_index  # pyright: ignore[reportPrivateUsage]
    assert ia_index is not None
    _, ia_item_status = section._checklist[ia_index]  # pyright: ignore[reportPrivateUsage]
    assert ia_item_status == "done"


def test_program_section_marks_checklist_failed_on_future_error() -> None:
    """A `Future` that resolves with an exception must flip the Individual Address
    checklist entry to "failed" and surface the exception text as the error."""
    device = _fake_program_device()
    future: Future[None] = Future()
    section = ProgramSection(lambda _device, _request: future)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.BTN_NEXT)
        ctx.yield_()
        ctx.item_click(S.BTN_PROGRAM)
        ctx.yield_()

    _run_program_section(section, device, test_function)

    future.set_exception(TimeoutError("no ack from device"))

    assert section._status == "error"  # pyright: ignore[reportPrivateUsage]
    assert section._error_message == "no ack from device"  # pyright: ignore[reportPrivateUsage]
    ia_index = section._ia_checklist_index  # pyright: ignore[reportPrivateUsage]
    assert ia_index is not None
    _, ia_item_status = section._checklist[ia_index]  # pyright: ignore[reportPrivateUsage]
    assert ia_item_status == "failed"


def test_program_section_reports_not_connected_when_on_program_returns_none() -> None:
    """`on_program` returning `None` (the "not connected" contract - see
    `ConnectionService.assign_individual_address_for_device`) must show an error
    immediately, with no `Future` to wait on."""
    device = _fake_program_device()
    section = ProgramSection(lambda _device, _request: None)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click(S.BTN_NEXT)
        ctx.yield_()
        ctx.item_click(S.BTN_PROGRAM)
        ctx.yield_()

    _run_program_section(section, device, test_function)

    assert section._status == "error"  # pyright: ignore[reportPrivateUsage]
    assert section._error_message == S.PROGRAM_LOG_NOT_CONNECTED  # pyright: ignore[reportPrivateUsage]


def test_program_section_no_horizontal_overflow() -> None:
    """Step 1's two-card-plus-inline-serial-field layout must not need horizontal
    scrolling at the docked panel width."""
    device = _fake_program_device()
    section = ProgramSection(lambda _device, _request: None)
    result: dict[str, float] = {}

    def gui_function() -> None:
        imgui.set_next_window_size(imgui.ImVec2(*_PANEL_SIZE))
        imgui.begin("TestPanel")
        section.render(device, "")
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.yield_()
        window = ctx.get_window_by_ref("//TestPanel")
        result["scroll_max_x"] = window.scroll_max.x

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)

    assert result["scroll_max_x"] == 0.0
