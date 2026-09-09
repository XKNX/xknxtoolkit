"""The Configure panel's Program Device section: how to address the device for
programming (via its programming button, or by serial number) and what to program
(Individual Address / Group Addresses / Parameters, as a Full or Partial download).

KNX v02.01.02 - Management Procedures 03.05.02 distinguishes these as separate
Network Management procedures: NM_IndividualAddress_Write (§2.3) requires the
device to be in programming mode (button pressed) and addresses it via broadcast,
while NM_IndividualAddress_SerialNumber_Write (§2.5) addresses one specific device
by its serial number without needing programming mode or risking collision with
other devices on the bus. Both only ever assign the Individual Address - once a
device has one, everything else (Group Addresses, Parameters/the application
program) is downloaded point-to-point via its Individual Address, independent of
which trigger was used to get it there in the first place.

Presented as a small two-step flow rather than one flat form, since "how do I
find/address the device" and "what do I actually want to program" are genuinely
different decisions - Find Device only matters for the addressing step above, and
is irrelevant once the device already has an address you're just reprogramming.

See `knx_gui.plugins.project.ui.components` for why this lives here and not in
`knx_gui.widgets`.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Literal

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S

_SERIAL_HEX_LENGTH = 12  # 6 bytes, KNX serial number width
_ERROR_COLOR = imgui.ImVec4(0.85, 0.35, 0.35, 1.0)
_WARNING_COLOR = imgui.ImVec4(0.9, 0.5, 0.3, 1.0)
_SUCCESS_COLOR = imgui.ImVec4(0.45, 0.75, 0.45, 1.0)
_CHECKLIST_MARK_COLUMN = 20.0

_Step = Literal["find_device", "mode"]
_Status = Literal["idle", "running", "success", "error"]
_ItemStatus = Literal["done", "current", "failed", "skipped"]


@dataclass(frozen=True)
class ProgramRequest:
    """One programming request. `serial` is only meaningful (and only ever set)
    when `trigger == "serial"`.

    `program_group_addresses` and `program_parameters` describe the requested
    scope, same as `program_individual_address` - but see `ProgramSection`'s own
    docstring: nothing downloads either of those yet, only Individual Address
    actually runs on the bus. They're real fields (not dropped) so a caller can
    already log/surface "this would have also downloaded X" ahead of that landing.
    """

    trigger: str  # "button" | "serial"
    serial: bytes | None
    program_individual_address: bool
    program_group_addresses: bool
    program_parameters: bool


class ProgramSection:
    def __init__(
        self, on_program: Callable[[Device, ProgramRequest], Future[Any] | None]
    ) -> None:
        self._on_program = on_program
        self._step: _Step = "find_device"
        self._trigger_serial: bool = False
        self._scope_full: bool = True
        self._scope_ia: bool = True
        self._scope_ga: bool = True
        self._scope_params: bool = True

        self._status: _Status = "idle"
        self._error_message: str = ""
        self._checklist: list[tuple[str, _ItemStatus]] = []
        self._ia_checklist_index: int | None = None

    def render(self, device: Device, serial_hex: str) -> str:
        """Returns `serial_hex`, or the value it was just edited to - Step 1 also
        offers an inline field for it, alongside the one under Individual Address
        in the panel's header; both edit the same buffer, owned by the caller."""
        if self._status != "idle":
            self._render_status(device)
            return serial_hex

        if self._step == "find_device":
            return self._render_find_device(serial_hex)
        self._render_mode(device, serial_hex)
        return serial_hex

    # --- Step 1: Find Device -----------------------------------------------

    def _render_find_device(self, serial_hex: str) -> str:
        imgui.text(S.PROGRAM_STEP_FIND_DEVICE)
        imgui.indent()

        # Two big tappable cards rather than radio buttons - this is the one
        # choice in the whole flow that's genuinely about the physical device
        # in front of you, not just a setting, so it gets more visual weight.
        # Buttons, not Selectables: a Selectable draws no visible boundary at
        # all when unselected (confirmed via the harness) - just floating text,
        # not a card. A Button always has a filled background, selected or not.
        card_height = 40.0
        spacing = imgui.get_style().item_spacing.x
        avail = imgui.get_content_region_avail().x
        # 85px still fits ~9-10 hex chars before it scrolls internally while
        # typing - narrower than that starts crowding "Programming Button"
        # (122px of text alone) out of its own card.
        field_width = 85.0 if self._trigger_serial else 0.0
        gaps = spacing * (3 if self._trigger_serial else 1)
        card_size = imgui.ImVec2((avail - gaps - field_width) / 2, card_height)

        if _trigger_card(S.PROGRAM_TRIGGER_BUTTON, not self._trigger_serial, card_size):
            self._trigger_serial = False
        imgui.same_line()
        if _trigger_card(S.PROGRAM_TRIGGER_SERIAL, self._trigger_serial, card_size):
            self._trigger_serial = True

        if self._trigger_serial:
            imgui.same_line()
            # Vertically center against the (taller) cards on this same line.
            imgui.set_cursor_pos_y(
                imgui.get_cursor_pos_y() + (card_height - imgui.get_frame_height()) / 2
            )
            imgui.set_next_item_width(field_width)
            _, serial_hex = imgui.input_text(
                "##program_serial", serial_hex, imgui.InputTextFlags_.chars_hexadecimal
            )

        help_text = (
            S.PROGRAM_TRIGGER_HELP_SERIAL
            if self._trigger_serial
            else S.PROGRAM_TRIGGER_HELP_BUTTON
        )
        _wrapped_text_disabled(help_text)

        serial = _parse_serial(serial_hex) if self._trigger_serial else None
        can_advance = not self._trigger_serial or serial is not None
        if self._trigger_serial and serial is None:
            msg = S.PROGRAM_SERIAL_INVALID if serial_hex else S.PROGRAM_SERIAL_MISSING
            imgui.text_colored(_WARNING_COLOR, msg)

        imgui.spacing()
        imgui.begin_disabled(not can_advance)
        if imgui.button(S.BTN_NEXT, imgui.ImVec2(100, 0)):
            self._step = "mode"
        imgui.end_disabled()
        imgui.unindent()
        return serial_hex

    # --- Step 2: Programming Mode -------------------------------------------

    def _render_mode(self, device: Device, serial_hex: str) -> None:
        imgui.text(S.PROGRAM_STEP_MODE)
        imgui.indent()
        if imgui.radio_button(S.PROGRAM_SCOPE_FULL, self._scope_full):
            self._scope_full = True
        imgui.same_line()
        if imgui.radio_button(S.PROGRAM_SCOPE_PARTIAL, not self._scope_full):
            self._scope_full = False

        imgui.begin_disabled(self._scope_full)
        ia = self._scope_ia or self._scope_full
        changed, ia = imgui.checkbox(S.CONFIGURE_INDIVIDUAL_ADDRESS, ia)
        if changed:
            self._scope_ia = ia
        imgui.same_line()
        ga = self._scope_ga or self._scope_full
        changed, ga = imgui.checkbox(S.PROGRAM_SCOPE_GROUP_ADDRESSES, ga)
        if changed:
            self._scope_ga = ga
        imgui.same_line()
        params = self._scope_params or self._scope_full
        changed, params = imgui.checkbox(S.PROGRAM_SCOPE_PARAMETERS, params)
        if changed:
            self._scope_params = params
        imgui.end_disabled()

        if self._active_scope_ga() or self._active_scope_params():
            _wrapped_text_disabled(S.PROGRAM_NOT_YET_SUPPORTED)

        scope_empty = not (
            self._active_scope_ia()
            or self._active_scope_ga()
            or self._active_scope_params()
        )
        if scope_empty:
            imgui.text_colored(_WARNING_COLOR, S.PROGRAM_SCOPE_NONE_SELECTED)

        imgui.spacing()
        if imgui.button(S.BTN_BACK, imgui.ImVec2(100, 0)):
            self._step = "find_device"
        imgui.same_line()
        imgui.begin_disabled(scope_empty)
        if imgui.button(S.BTN_PROGRAM, imgui.ImVec2(100, 0)):
            self._start(device, serial_hex)
        imgui.end_disabled()
        imgui.unindent()

    def _active_scope_ia(self) -> bool:
        return self._scope_full or self._scope_ia

    def _active_scope_ga(self) -> bool:
        return self._scope_full or self._scope_ga

    def _active_scope_params(self) -> bool:
        return self._scope_full or self._scope_params

    # --- Running / result ----------------------------------------------------

    def _start(self, device: Device, serial_hex: str) -> None:
        serial = _parse_serial(serial_hex) if self._trigger_serial else None
        request = ProgramRequest(
            trigger="serial" if self._trigger_serial else "button",
            serial=serial,
            program_individual_address=self._active_scope_ia(),
            program_group_addresses=self._active_scope_ga(),
            program_parameters=self._active_scope_params(),
        )

        self._status = "running"
        self._error_message = ""
        self._checklist = [
            (
                S.PROGRAM_CHECKLIST_ADDRESS_SERIAL
                if request.trigger == "serial"
                else S.PROGRAM_CHECKLIST_ADDRESS_BUTTON,
                "done",
            )
        ]
        if request.program_individual_address:
            self._ia_checklist_index = len(self._checklist)
            self._checklist.append(
                (
                    S.PROGRAM_CHECKLIST_WRITE_IA.format(
                        address=device.individual_address
                    ),
                    "current",
                )
            )
        else:
            self._ia_checklist_index = None
        if request.program_group_addresses or request.program_parameters:
            self._checklist.append((S.PROGRAM_CHECKLIST_GA_PARAMS, "skipped"))

        future = self._on_program(device, request)
        if future is None:
            self._finish(error=S.PROGRAM_LOG_NOT_CONNECTED)
            return
        future.add_done_callback(self._handle_future_done)

    def _handle_future_done(self, future: Future[Any]) -> None:
        # Runs on the asyncio loop's thread (see ConnectionService.run_async),
        # not the render thread - same list-mutation-from-a-callback pattern
        # already used for restart results, no lock (fine under the GIL).
        if future.cancelled():
            return
        exc = future.exception()
        self._finish(error=str(exc) if exc is not None else None)

    def _finish(self, error: str | None) -> None:
        if self._ia_checklist_index is not None:
            label, _ = self._checklist[self._ia_checklist_index]
            self._checklist[self._ia_checklist_index] = (
                label,
                "failed" if error else "done",
            )
        if error is None:
            self._status = "success"
        else:
            self._error_message = error
            self._status = "error"

    def _render_status(self, device: Device) -> None:
        imgui.text(S.BTN_PROGRAM_DEVICE + f": {device.name}")
        imgui.spacing()

        for label, item_status in self._checklist:
            self._render_checklist_item(label, item_status)

        if self._status == "error":
            imgui.spacing()
            _wrapped_error_box(S.PROGRAM_STATUS_ERROR.format(error=self._error_message))

        if self._status != "running":
            imgui.spacing()
            if imgui.button(S.BTN_PROGRAM_ANOTHER):
                self._status = "idle"
                self._step = "find_device"

    def _render_checklist_item(self, label: str, item_status: _ItemStatus) -> None:
        """Each line is its own scan-able unit - a mark, then the label wrapped to
        whatever's left of the row - rather than a scrolling log of timestamped
        text (option A's original treatment; B's mockup read cleaner for this).

        Marks are plain ASCII, not check/cross Unicode glyphs (confirmed via the
        harness: hello_imgui's default font has no glyphs for those - renders
        tofu boxes instead - and nothing else in this app relies on non-ASCII
        symbol glyphs either).
        """
        start_x = imgui.get_cursor_pos_x()
        if item_status == "done":
            imgui.text_colored(_SUCCESS_COLOR, "[+]")
        elif item_status == "failed":
            imgui.text_colored(_ERROR_COLOR, "[!]")
        elif item_status == "skipped":
            imgui.text_disabled("[-]")
        else:
            imgui.text_disabled("[.]")

        imgui.same_line(start_x + _CHECKLIST_MARK_COLUMN)
        wrap_x = imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
        imgui.push_text_wrap_pos(wrap_x)
        if item_status == "skipped":
            imgui.text_disabled(label)
        elif item_status == "failed":
            imgui.text_colored(_ERROR_COLOR, label)
        else:
            imgui.text_unformatted(label)
        imgui.pop_text_wrap_pos()


def _parse_serial(serial_hex: str) -> bytes | None:
    """A KNX serial number is 6 bytes - `serial_hex` must be exactly 12 hex chars
    (whitespace-insensitive, so "00 FA 12 34 56 78" and "00FA12345678" both work)."""
    compact = "".join(serial_hex.split())
    if len(compact) != _SERIAL_HEX_LENGTH:
        return None
    try:
        return bytes.fromhex(compact)
    except ValueError:
        return None


def _wrapped_text_disabled(text: str) -> None:
    wrap_x = imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
    imgui.push_text_wrap_pos(wrap_x)
    imgui.text_disabled(text)
    imgui.pop_text_wrap_pos()


def _trigger_card(label: str, selected: bool, size: imgui.ImVec2) -> bool:
    if selected:
        imgui.push_style_color(imgui.Col_.button, (0.18, 0.45, 0.85, 1.0))
        imgui.push_style_color(imgui.Col_.button_hovered, (0.22, 0.5, 0.9, 1.0))
        imgui.push_style_color(imgui.Col_.button_active, (0.15, 0.4, 0.8, 1.0))
    clicked = imgui.button(label, size)
    if selected:
        imgui.pop_style_color(3)
    return clicked


def _wrapped_error_box(text: str) -> None:
    imgui.push_style_color(imgui.Col_.child_bg, (0.3, 0.12, 0.12, 1.0))
    imgui.begin_child(
        "##program_error",
        imgui.ImVec2(imgui.get_content_region_avail().x, 0),
        imgui.ChildFlags_.borders | imgui.ChildFlags_.auto_resize_y,
    )
    wrap_x = imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
    imgui.push_text_wrap_pos(wrap_x)
    imgui.text_colored(_ERROR_COLOR, text)
    imgui.pop_text_wrap_pos()
    imgui.end_child()
    imgui.pop_style_color()
