"""Headless regression tests for `MemoryPreviewWindow.open()` device-switch
cache isolation.

These are unit tests: they exercise `open()` directly and inspect the
per-segment caches (`_hex_views`, `_ref_data`) without driving imgui, so they
run in the headless unit-test job (no display / xvfb needed). The end-to-end
render path is covered separately by `src/knx_gui/testing/tests/test_memory_preview.py`.

`_hex_views` clearance is asserted here because the e2e test cannot: `render()`
legitimately re-creates a fresh `HexView` for the new device's segment, so by
the time the e2e test inspects `_hex_views` it is populated again.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from knx_gui.device import Device
from knx_gui.plugins.base import Logger
from knx_gui.plugins.project.ui.memory_preview import MemoryPreviewWindow

# Real form of a memory code segment id (see
# packages/product/tests/parser_v2/test_encode.py): derived from the
# application id and the segment's own id - contains nothing device-instance
# specific, so two device instances of the same product type share it verbatim.
SEG = "M-0008_A-7072-21-5CC3-O000A_RS-04-00000"


class _NullLogger(Logger):
    """A `Logger` that discards everything - `MemoryPreviewWindow` only logs on
    `EncodingError`, which these duck-typed devices never raise. Subclassed
    (rather than a `SimpleNamespace` cast) so the instance is statically a
    `Logger` and the four no-op methods keep their typed `(event, **kwargs)`
    signature."""

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


def _make_device(node_id: int, data: bytes) -> Device:
    """Duck-typed Device stand-in carrying only what `MemoryPreviewWindow` reads:
    `node_id`, `name`, `individual_address` and the three memory-encoding
    accessors. Two devices built with the same `SEG` model the same-product-type
    collision that the bug hinges on."""
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


def _make_window(devices: list[Device]) -> MemoryPreviewWindow:
    return MemoryPreviewWindow(get_devices=lambda: devices, log=_NullLogger())


def test_open_different_device_clears_ref_data_and_hex_views() -> None:
    """Regression: opening the preview for a different device via `open()` must
    clear the per-segment caches that are not re-derived each frame, mirroring
    the combo-box device-switcher's reset. Otherwise a reference file loaded
    for device A leaks into device B's preview when both share a segment id."""
    a = _make_device(1, b"\x01\x02\x03\x04")
    b = _make_device(2, b"\xaa\xbb\xcc\xdd")
    win = _make_window([a, b])

    win.open(a)
    # Simulate 'Diff...' loading a reference file for A, plus the cached
    # HexView the tab loop creates for the shared segment id - exactly the
    # state `render()` would build up across frames while previewing A.
    win._ref_data[SEG] = b"\x01\x02\x03\x04"  # pyright: ignore[reportPrivateUsage]
    win._hex_views[SEG] = cast(Any, object())  # pyright: ignore[reportPrivateUsage]
    # Closing the window only hides it; the instance and its caches survive.
    win._show = False  # pyright: ignore[reportPrivateUsage]

    # Re-open for a different device of the same product type (same SEG).
    win.open(b)

    assert win._device is b  # pyright: ignore[reportPrivateUsage]
    assert win._show is True  # pyright: ignore[reportPrivateUsage]
    assert SEG not in win._ref_data, "reference bytes leaked across devices"  # pyright: ignore[reportPrivateUsage]
    assert win._ref_data == {}  # pyright: ignore[reportPrivateUsage]
    assert SEG not in win._hex_views, "cached HexView leaked across devices"  # pyright: ignore[reportPrivateUsage]
    assert win._hex_views == {}  # pyright: ignore[reportPrivateUsage]


def test_open_same_device_preserves_caches() -> None:
    """Closing and re-opening the preview for the *same* device must NOT clear
    the caches - a user who loaded a reference, closed the window, and re-opened
    it for the same device expects their loaded reference to survive. Only an
    actual device change triggers the reset, so this guards against an
    over-aggressive 'always clear on open()' simplification."""
    a = _make_device(1, b"\x01\x02")
    win = _make_window([a])

    win.open(a)
    win._ref_data[SEG] = b"\x01\x02\x03\x04"  # pyright: ignore[reportPrivateUsage]
    ref_view = win._hex_views[SEG] = cast(  # pyright: ignore[reportPrivateUsage]
        Any, object()
    )
    win._show = False  # pyright: ignore[reportPrivateUsage]

    win.open(a)

    assert win._device is a  # pyright: ignore[reportPrivateUsage]
    assert win._show is True  # pyright: ignore[reportPrivateUsage]
    assert win._ref_data == {SEG: b"\x01\x02\x03\x04"}  # pyright: ignore[reportPrivateUsage]
    assert win._hex_views[SEG] is ref_view  # pyright: ignore[reportPrivateUsage]
