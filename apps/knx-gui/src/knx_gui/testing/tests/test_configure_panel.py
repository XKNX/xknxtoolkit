"""UI regression tests for the Configure panel.

Driven by Dear ImGui Test Engine (see `knx_gui.testing.harness`). These open a
real (briefly visible) window, so they need a display and aren't part of the
root `uv run pytest` run (see the root pyproject.toml's `testpaths`) - run
them explicitly:

    uv run pytest src/knx_gui/testing/tests -v
"""

from __future__ import annotations

from types import SimpleNamespace

from imgui_bundle import imgui
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
    count_parameters,
)
from knx_gui.plugins.project.ui.configure import ConfigurePanel

# Aliased: pytest's default discovery tries to collect any name starting with "Test"
# as a test class, which fails noisily for TestContext (it has an __init__).
from knx_gui.testing.harness import AppHandle, build_app, find_device, run_ui_test
from knx_gui.testing.harness import TestContext as _TestContext

# Matches the Configure panel's real docked size (see apps/knx-gui/XKNX_Toolkit.ini) -
# the overflows these tests guard against only show up at that width, not a wide window.
_PANEL_SIZE = (417, 477)
_WINDOW_SIZE = (600, 600)


def _build_panel(app_handle: AppHandle, device: Device) -> ConfigurePanel:
    """A bare ConfigurePanel wired to `app_handle`'s already-open project, showing
    `device` - no KnxGuiApp rendering loop, no other plugins.

    Deliberately bypasses the Node Editor plugin, whose own default selection
    otherwise overrides ConfigurePanel's (confirmed empirically: driving
    selection through the full running app leaves a different device selected
    than the one just requested, because Node Editor syncs its own selection
    back every frame).
    """
    catalog = app_handle.app.catalog
    project = app_handle.app.project
    project.selected_device = device

    return ConfigurePanel(
        get_devices=lambda: project.devices,
        get_selected_device=lambda: project.selected_device,
        set_selected_device=lambda d: setattr(project, "selected_device", d),
        on_param_change=lambda d, p, v: None,
        on_individual_address_change=lambda d, a: None,
        on_name_change=lambda d, n: None,
        set_flag=lambda d, c, f, v: None,
        get_manufacturer=catalog.get_manufacturer,
    )


def _assert_no_horizontal_overflow(panel: ConfigurePanel) -> None:
    result: dict[str, float] = {}

    def gui_function() -> None:
        imgui.set_next_window_size(imgui.ImVec2(*_PANEL_SIZE))
        imgui.begin("TestPanel")
        panel.render()
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
    growing wide enough to force the whole panel wider than its docked size.
    Uses a device with at most one parameter and no com objects, so no
    Parameters tab bar renders - isolating the Metadata section's own layout
    from `test_parameters_tab_bar_no_horizontal_overflow`'s concern. Does
    *not* catch a purely local label/value collision that stays within the
    window's width - see `test_label_column_leaves_room_for_its_own_widest_label`
    for that.
    """
    app_handle = build_app()
    device = find_device(
        app_handle,
        lambda d: count_parameters(d.get_ui()) <= 1 and not d.get_visible_com_objects(),
    )
    _assert_no_horizontal_overflow(_build_panel(app_handle, device))


def test_parameters_tab_bar_no_horizontal_overflow() -> None:
    """The Parameters tab bar must not need horizontal scrolling at the docked panel width.

    Regression test for a bug where a tab bar's own "ideal" width - every tab
    at its natural, unshrunk width - still counted towards the window's
    content size once tabs didn't fit, even though the tab bar itself
    rendered fine (self-clipped, with scroll arrows). Fixed by containing the
    tab bar in a child window sized to the actually available width (see
    `render_ui_tree` in `knx_gui.widgets.parameter_widgets`).

    Runs the *full* app via `run_ui_test`, unlike the other tests here: a bare
    `imgui.begin()` window with a fixed size just grows to fit the tab bar's
    content instead of needing to scroll, so it doesn't reproduce this bug at
    all - confirmed empirically (`scroll_max.x` stayed 0 even with the bug
    reintroduced, in a bare window; it reached 909px in the real docked panel).
    Accepts whichever device the app selects by default rather than forcing a
    specific one (the Node Editor's own selection overrides any explicit
    choice - see `_build_panel`'s docstring), asserting it actually has
    parameters so the test stays meaningful instead of silently passing
    against an empty Parameters section.
    """
    app_handle = build_app()
    result: dict[str, float] = {}

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Configure")
        ctx.yield_()
        # Content taller than the panel needs a couple more frames for vertical
        # scroll/layout to settle before scroll_max is final.
        ctx.yield_()
        ctx.yield_()
        device = app_handle.app.project.selected_device
        assert device is not None and count_parameters(device.get_ui()) > 0, (
            "expected the app to default-select a device with parameters"
        )
        window = ctx.get_window_by_ref("//Configure")
        result["scroll_max_x"] = window.scroll_max.x

    run_ui_test(test_function, app_handle=app_handle)

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


def test_restart_section_destructive_mode_requires_confirmation() -> None:
    """A destructive reset mode must not fire on the first click - `RestartSection`
    routes it through the "Confirm Reset" popup instead, and only a click inside
    that popup should call `on_restart_device`.

    Drives `_reset_mode_index` directly (see `MetadataSection`'s tests for the same
    trade-off with `_label_column`) rather than operating the mode combo, since the
    combo interaction itself isn't what this test is about.
    """
    app_handle = build_app()
    device = find_device(app_handle, lambda d: bool(d.individual_address))
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
    app_handle = build_app()
    device = find_device(app_handle, lambda d: bool(d.individual_address))
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
