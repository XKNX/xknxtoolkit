"""UI regression tests for the Virtual panel.

Driven by Dear ImGui Test Engine (see `knx_gui.testing.harness`). These open a
real (briefly visible) window, so they need a display and aren't part of the
root `uv run pytest` run - run them explicitly:

    uv run pytest src/knx_gui/testing/tests -v

Covers the serial-number input field's validation: the field must cap at 12
hex chars, reject non-hex characters, only write valid 6-byte serials to
``device.serial_number``, and render a warning banner for wrong-width input.
Mirrors the in-repo discipline the Configure panel already ships (see
``test_configure_panel.py``'s ``test_program_section_serial_field_caps_at_twelve_hex_chars``).
"""

from __future__ import annotations

from collections.abc import Callable

from imgui_bundle import imgui
from imgui_bundle.immapp import testing as imgui_testing

# knx_gui.plugins.node_editor imports knx_gui.widgets before knx_gui.widgets finishes
# initializing if knx_gui.plugins.project (below) is imported first on a fresh
# interpreter - importing knx_gui.main first establishes the same import order the
# app itself uses, side-stepping the circular import. (Sorts first alphabetically too,
# so this also satisfies ruff's import ordering - no noqa needed.)
import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.knxip_tunnelling_gateway import GatewayState
from knx_gui.plugins.virtual.ui import VirtualPanel
from knx_gui.plugins.virtual.virtual_device import VirtualDevice
from knx_gui.testing.harness import TestContext as _TestContext

_WINDOW_SIZE = (600, 600)


def _make_panel(device: VirtualDevice | None = None) -> VirtualPanel:
    """A VirtualPanel wired to stub gateway callbacks and a real VirtualDevice -
    enough to render the Devices section and drive the serial field without a
    running gateway, catalog, or project."""
    device = device or VirtualDevice()
    return VirtualPanel(
        get_gateway_state=lambda: GatewayState.STOPPED,
        get_gateway_error=lambda: None,
        get_gateway_connected=lambda: False,
        get_gateway_local_ips=lambda: [],
        on_start=lambda _n, _p, _m: None,
        on_stop=lambda: None,
        get_device=lambda: device,
    )


def _run_virtual_panel(
    panel: VirtualPanel, test_function: Callable[[_TestContext], None]
) -> None:
    """Render ``panel`` inside a bare window each frame while ``test_function``
    drives it - same focused-panel pattern as ``_run_program_section`` in
    ``test_configure_panel.py``."""

    def gui_function() -> None:
        imgui.begin("TestPanel")
        panel.render()
        imgui.end()

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)


def test_virtual_panel_serial_field_caps_at_twelve_hex_chars() -> None:
    """End-to-end: typing 16 hex characters through the real Virtual panel's
    serial field must leave the buffer at only 12 - confirms the field is wired
    to the capping callback, matching the Configure panel's behavior."""
    device = VirtualDevice()
    panel = _make_panel(device)
    panel._device_serial_hex = ""  # pyright: ignore[reportPrivateUsage]

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##device-serial")
        for ch in "00FA1234567890AB":  # 16 hex chars, only 12 fit
            ctx.key_chars(ch)
        ctx.yield_()

    _run_virtual_panel(panel, test_function)

    assert panel._device_serial_hex == "00FA12345678"  # pyright: ignore[reportPrivateUsage]


def test_virtual_panel_serial_field_rejects_non_hex_chars() -> None:
    """``chars_hexadecimal`` must block non-hex characters at the keyboard -
    typing "G" followed by 12 hex chars should result in exactly the 12 hex
    chars with no "G" in the buffer."""
    device = VirtualDevice()
    panel = _make_panel(device)
    panel._device_serial_hex = ""  # pyright: ignore[reportPrivateUsage]

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##device-serial")
        for ch in "G00FA12345678":  # G is non-hex, should be rejected
            ctx.key_chars(ch)
        ctx.yield_()

    _run_virtual_panel(panel, test_function)

    assert panel._device_serial_hex == "00FA12345678"  # pyright: ignore[reportPrivateUsage]


def test_virtual_panel_valid_serial_updates_device_serial_number() -> None:
    """Typing a valid 12-hex-char serial must write the parsed bytes to
    ``device.serial_number`` - the live-write path is preserved for valid input."""
    device = VirtualDevice()
    panel = _make_panel(device)
    panel._device_serial_hex = ""  # pyright: ignore[reportPrivateUsage]
    new_serial = "112233445566"

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##device-serial")
        for ch in new_serial:
            ctx.key_chars(ch)
        ctx.yield_()

    _run_virtual_panel(panel, test_function)

    assert device.serial_number == bytes.fromhex(new_serial)


def test_virtual_panel_wrong_width_does_not_update_device_serial_number() -> None:
    """A wrong-width serial (4 hex chars / 2 bytes) must NOT write to
    ``device.serial_number`` - the ``_parse_serial`` guard blocks the live-write
    for invalid input, leaving the device's serial at its previous value.

    Regression test for Mode B of the bug: ``bytes.fromhex("00FA")`` succeeds
    with a 2-byte result, and the old code silently wrote it to
    ``device.serial_number`` via ``contextlib.suppress(ValueError)``."""
    device = VirtualDevice()
    original_serial = device.serial_number
    panel = _make_panel(device)
    panel._device_serial_hex = ""  # pyright: ignore[reportPrivateUsage]

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##device-serial")
        for ch in "00FA":
            ctx.key_chars(ch)
        ctx.yield_()

    _run_virtual_panel(panel, test_function)

    assert device.serial_number == original_serial


def test_virtual_panel_empty_field_does_not_clear_device_serial_number() -> None:
    """Clearing the serial field must NOT write ``b""`` to
    ``device.serial_number`` - ``_parse_serial("")`` returns ``None``, so the
    guard blocks the write.

    Regression test for Mode B-empty of the bug: ``bytes.fromhex("")`` returns
    ``b""``, and the old code silently wrote it to ``device.serial_number`` when
    the user cleared the field (``changed`` was True, ``suppress`` didn't fire
    because no exception was raised)."""
    device = VirtualDevice()
    original_serial = device.serial_number
    panel = _make_panel(device)

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.item_click("##device-serial")
        # key_chars_replace deletes the existing content then inputs the
        # given chars - an empty string clears the field entirely, regardless
        # of the initial cursor position from item_click.
        ctx.key_chars_replace("")
        ctx.yield_()

    _run_virtual_panel(panel, test_function)

    assert panel._device_serial_hex == ""  # pyright: ignore[reportPrivateUsage]
    assert device.serial_number == original_serial


def test_virtual_panel_warning_banner_renders_for_wrong_width() -> None:
    """The warning banner must render when the serial field is non-empty but
    wrong width - verified by comparing the window height with (invalid serial)
    vs. without (valid serial) the warning, since ``imgui.text_colored`` items
    don't have stable test-engine item IDs.

    Mirrors the height-comparison approach in
    ``test_parameter_block_with_visible_parameters_is_still_rendered``."""
    result: dict[str, float] = {}

    def gui_function() -> None:
        valid_panel = _make_panel()
        valid_panel._device_serial_hex = "00FA12345678"  # pyright: ignore[reportPrivateUsage]
        invalid_panel = _make_panel()
        invalid_panel._device_serial_hex = "00FA"  # pyright: ignore[reportPrivateUsage]
        imgui.begin("Valid")
        valid_panel.render()
        imgui.end()
        imgui.begin("Invalid")
        invalid_panel.render()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Valid")
        ctx.yield_()
        ctx.yield_()
        valid_win = ctx.get_window_by_ref("//Valid")
        invalid_win = ctx.get_window_by_ref("//Invalid")
        result["valid_height"] = valid_win.size.y
        result["invalid_height"] = invalid_win.size.y

    imgui_testing.run(gui_function, test_function, window_size=(800, 600))

    assert result["invalid_height"] > result["valid_height"]


def test_virtual_panel_no_warning_for_empty_field() -> None:
    """An empty serial field must NOT render the warning banner - the warning is
    gated on ``self._device_serial_hex`` being truthy, so a deliberately cleared
    field (self-cuing) doesn't nag the user. Verified by height comparison: the
    empty-field window must be the same height as the valid-serial window."""
    result: dict[str, float] = {}

    def gui_function() -> None:
        valid_panel = _make_panel()
        valid_panel._device_serial_hex = "00FA12345678"  # pyright: ignore[reportPrivateUsage]
        empty_panel = _make_panel()
        empty_panel._device_serial_hex = ""  # pyright: ignore[reportPrivateUsage]
        imgui.begin("Valid")
        valid_panel.render()
        imgui.end()
        imgui.begin("Empty")
        empty_panel.render()
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//Valid")
        ctx.yield_()
        ctx.yield_()
        valid_win = ctx.get_window_by_ref("//Valid")
        empty_win = ctx.get_window_by_ref("//Empty")
        result["valid_height"] = valid_win.size.y
        result["empty_height"] = empty_win.size.y

    imgui_testing.run(gui_function, test_function, window_size=(800, 600))

    assert result["empty_height"] == result["valid_height"]
