"""Real-editor regression test for the node editor's multi-receiver link bug.

Drives the *actual* ``imgui_node_editor`` C++ bindings (no mocks) through
``NodeEditorPanel._render_links`` - the exact code path the bug lived in -
and queries the editor's own retained link state back with
``ed.get_link_pins`` to confirm every sender x receiver pair survives as its
own curve.

Needs a real display (it opens a window), so it lives under
``src/knx_gui/testing`` and is run by the e2e CI job under ``xvfb-run``:

    xvfb-run -a uv run pytest src/knx_gui/testing/tests -v
"""

from __future__ import annotations

from typing import Any

from imgui_bundle import imgui
from imgui_bundle import imgui_node_editor as ed
from imgui_bundle.immapp import testing as imgui_testing

# Importing knx_gui.main first establishes the same import order the app uses
# (side-stepping a circular import between knx_gui.plugins.node_editor and
# knx_gui.plugins.project) - see test_configure_panel.py for the same note.
import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.plugins.node_editor.ui import NodeEditorPanel
from knx_gui.plugins.project.service import Assignment, GroupAddress
from knx_gui.testing.harness import TestContext as _TestContext

_WINDOW_SIZE = (600, 600)

# Pin ids used to seed the panel's pin map (bypassing device-node rendering so
# the test is independent of Device/Application construction). These become
# real imgui_node_editor pins via ed.begin_pin below.
_SEND_PIN = 100000
_RECV_PINS = (100001, 100002, 100003)
_GA_ID = 7


def _build_panel() -> NodeEditorPanel:
    panel = NodeEditorPanel(
        get_devices=lambda: [],
        get_group_addresses=lambda: [GroupAddress(_GA_ID, "1/7", "Test GA")],
        get_assignments_for_ga=lambda ga_id: (
            [
                Assignment(100, 500, _GA_ID, is_sending=True),
                Assignment(101, 501, _GA_ID, is_sending=False),
                Assignment(102, 502, _GA_ID, is_sending=False),
                Assignment(103, 503, _GA_ID, is_sending=False),
            ]
            if ga_id == _GA_ID
            else []
        ),
        add_link=lambda a, b: 1,
        remove_link=lambda a: None,
        on_param_change=lambda d, p, v: None,
    )
    panel._co_db_id_to_pins[500] = {"out": _SEND_PIN}  # pyright: ignore[reportPrivateUsage]
    panel._co_db_id_to_pins[501] = {"in": _RECV_PINS[0]}  # pyright: ignore[reportPrivateUsage]
    panel._co_db_id_to_pins[502] = {"in": _RECV_PINS[1]}  # pyright: ignore[reportPrivateUsage]
    panel._co_db_id_to_pins[503] = {"in": _RECV_PINS[2]}  # pyright: ignore[reportPrivateUsage]
    panel._show_ga_nodes = False  # pyright: ignore[reportPrivateUsage]  # GA-hidden (default)
    return panel


def test_multi_receiver_ga_renders_all_links_in_real_editor() -> None:
    """A 1-sender/3-receiver GA must produce 3 surviving curves in the editor.

    Reproduces the bug's exact input pattern: the GA-hidden branch used to
    reuse ``ga.id`` as the ``LinkId`` for every sender x receiver pair, so
    ``ed.link(LinkId(7), ...)`` collapsed to one editor link record (only the
    last-submitted pair survived). Querying back with ``ed.get_link_pins``
    returned just that last pair - the other two real assignments were
    invisible. After the fix, each pair has a unique ``LinkId`` and all three
    survive in the editor's own state.
    """
    panel = _build_panel()
    setup_done: dict[str, bool] = {"v": False}
    frame: dict[str, int] = {"n": 0}
    result: dict[str, Any] = {}

    def gui_function() -> None:
        if not setup_done["v"]:
            panel.setup()
            setup_done["v"] = True
        frame["n"] += 1
        ed.set_current_editor(panel._editor_context)  # pyright: ignore[reportPrivateUsage]
        ed.begin("##NodeEditorCanvas", imgui.ImVec2(0, 0))
        # Submit real nodes/pins with the exact ids the panel references, so
        # the editor accepts the links and reports them back via get_link_pins.
        for node_id, pin_id, kind in (
            (1, _SEND_PIN, ed.PinKind.output),
            (2, _RECV_PINS[0], ed.PinKind.input),
            (3, _RECV_PINS[1], ed.PinKind.input),
            (4, _RECV_PINS[2], ed.PinKind.input),
        ):
            ed.begin_node(ed.NodeId(node_id))
            ed.begin_pin(ed.PinId(pin_id), kind)
            ed.pin_pivot_alignment(imgui.ImVec2(0.5, 0.5))
            imgui.dummy(imgui.ImVec2(20.0, 20.0))
            ed.end_pin()
            ed.end_node()
        panel._render_links()  # pyright: ignore[reportPrivateUsage]
        ed.end()

        # Once the links have been submitted for a couple of frames, ask the
        # editor itself which links survive (this is the symptom probe: with
        # the buggy code, ed.get_link_pins(LinkId(7)) returns only the last
        # pair and only one entry would be found here).
        if frame["n"] >= 3:
            expected = panel._compute_visual_links()  # pyright: ignore[reportPrivateUsage]
            surviving: dict[int, tuple[int, int]] = {}
            for link_id, _start, _end, _ga_id in expected:
                sp = ed.PinId()
                ep = ed.PinId()
                if ed.get_link_pins(ed.LinkId(link_id), sp, ep):
                    surviving[link_id] = (sp.id(), ep.id())
            result["expected"] = expected
            result["surviving"] = surviving

    def test_function(_ctx: _TestContext) -> None:
        # Let a few frames render so links are submitted and the editor state
        # is queryable before gui_function stashes the result.
        _ctx.yield_()
        _ctx.yield_()
        _ctx.yield_()
        _ctx.yield_()

    imgui_testing.run(
        gui_function,
        test_function,
        window_size=_WINDOW_SIZE,
        with_node_editor=True,
    )

    expected: list[tuple[int, int, int, int]] = result["expected"]
    surviving: dict[int, tuple[int, int]] = result["surviving"]
    assert len(expected) == 3, f"panel must compute 3 visual links, got {expected}"
    assert len(surviving) == 3, (
        f"all 3 visual links must survive in the editor; "
        f"only {len(surviving)} did: {surviving}. "
        "This is the duplicate-LinkId collapse symptom."
    )
    for link_id, start_pin, end_pin, _ga_id in expected:
        assert link_id in surviving, f"link {link_id} missing from editor"
        assert surviving[link_id] == (start_pin, end_pin), (
            f"link {link_id} pins mismatch: "
            f"expected {(start_pin, end_pin)}, got {surviving[link_id]}"
        )
