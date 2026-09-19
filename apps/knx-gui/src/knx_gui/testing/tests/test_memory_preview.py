"""E2E/UI regression tests for `MemoryPreviewWindow` - drives the real
`render()` under Dear ImGui Test Engine.

Needs a real display (CI runs under `xvfb-run`; see `src/knx_gui/testing/`).
Run via:

    uv run pytest src/knx_gui/testing/tests -v          # on a desktop
    xvfb-run -a uv run pytest src/knx_gui/testing/tests # headless

Regression for the 'Preview Memory' button (`open()`) leaking per-segment
reference-file bytes and cached HexView instances across devices of the same
product type (shared segment ids). The combo device-switcher inside the
window cleared these caches; `open()` did not.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from imgui_bundle.immapp import testing as imgui_testing

# knx_gui.plugins.node_editor imports knx_gui.widgets before knx_gui.widgets
# finishes initializing if knx_gui.plugins.project (below) is imported first on
# a fresh interpreter - importing knx_gui.main first establishes the same
# import order the app itself uses, side-stepping the circular import.
import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.device import Device
from knx_gui.plugins.base import Logger
from knx_gui.plugins.project.ui.memory_preview import MemoryPreviewWindow

# Aliased: pytest's default discovery tries to collect any name starting with
# "Test" as a test class, which fails noisily for TestContext (it has an
# __init__). Same pattern as test_configure_panel.py.
from knx_gui.testing.harness import TestContext as _TestContext

SEG = "M-0008_A-7072-21-5CC3-O000A_RS-04-00000"
_WINDOW_SIZE = (800, 600)


class _NullLogger(Logger):
    """Discards everything - `MemoryPreviewWindow` only logs on `EncodingError`,
    which these duck-typed devices never raise."""

    def __init__(self) -> None:
        pass

    def debug(self, event: str, **kwargs: Any) -> None:
        pass

    def info(self, event: str, **kwargs: Any) -> None:
        pass

    def warning(self, event: str, **kwargs: Any) -> None:
        pass

    def error(self, event: str, **kwargs: Any) -> None:
        pass


def _dev(node_id: int, data: bytes) -> Device:
    return cast(
        Device,
        SimpleNamespace(
            node_id=node_id,
            name=f"Dev{node_id}",
            individual_address=f"1.1.{node_id}",
            encode_to_memory=lambda: {SEG: data},
            get_segment_base_addrs=lambda: {SEG: 0},
            get_memory_param_map=lambda: {SEG: cast(dict[int, tuple[str, str]], {})},
        ),
    )


def test_open_preview_for_different_device_does_not_leak_reference() -> None:
    """Reproduction of the leak through the real `render()` path.

    Sequence: open(A) -> load reference file for A (simulated by populating
    `_ref_data`, exactly what the 'Diff...' modal does at memory_preview.py:138)
    -> close the window (only hides it; the instance survives) -> open(B) for a
    different device of the same product type (shared SEG) -> assert the
    per-segment caches did not leak into B. Before the fix this failed with
    `AssertionError: leaked` and B's tab rendered a diff against A's reference
    with a 'Diff (clear)' toolbar the user never requested.
    """
    a, b = _dev(1, b"\x01\x02\x03\x04"), _dev(2, b"\xaa\xbb\xcc\xdd")
    win = MemoryPreviewWindow(get_devices=lambda: [a, b], log=_NullLogger())

    def gui() -> None:
        win.render()

    def test(ctx: _TestContext) -> None:
        ctx.yield_()
        win.open(a)
        ctx.yield_()
        ctx.yield_()
        # Simulate 'Diff...' -> Load reference file for A's shared segment.
        win._ref_data[SEG] = b"\x01\x02\x03\x04"  # pyright: ignore[reportPrivateUsage]
        ctx.yield_()
        # Close the window (only flips `_show`; the instance and caches persist).
        win._show = False  # pyright: ignore[reportPrivateUsage]
        ctx.yield_()
        # Re-open for a different device of the same product type (same SEG).
        win.open(b)
        ctx.yield_()
        ctx.yield_()

        assert win._device is b  # pyright: ignore[reportPrivateUsage]
        # The substantive fix: A's reference bytes must not leak into B's
        # preview. (`_hex_views` clearance is covered by the headless unit
        # test; here `render()` legitimately re-creates a fresh HexView for B's
        # segment, so the carryover is self-healing - see the report's "Notes
        # on the stale HexView instance".)
        assert SEG not in win._ref_data, "leaked"  # pyright: ignore[reportPrivateUsage]

    imgui_testing.run(gui, test, window_size=_WINDOW_SIZE)
