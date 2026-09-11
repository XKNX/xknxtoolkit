"""The Configure panel's Program Device section: address the device (via its
programming button, or by serial number - KNX Management Procedures 03.05.02
§2.3/§2.5) and choose what to program. Both triggers only ever assign the
Individual Address; see `ProgramRequest` for Group Addresses/Parameters.

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
_ERROR_BG_COLOR = imgui.ImVec4(0.3, 0.12, 0.12, 1.0)
_CARD_SELECTED_COLOR = imgui.ImVec4(0.18, 0.45, 0.85, 1.0)
_CARD_SELECTED_HOVERED_COLOR = imgui.ImVec4(0.22, 0.5, 0.9, 1.0)
_CARD_SELECTED_ACTIVE_COLOR = imgui.ImVec4(0.15, 0.4, 0.8, 1.0)
_CHECKLIST_MARK_COLUMN = 20.0
_ACTION_BUTTON_SIZE = imgui.ImVec2(100, 0)
_SERIAL_FIELD_WIDTH = 85.0

_Step = Literal["find_device", "mode"]
_Status = Literal["idle", "running", "success", "error"]
_ItemStatus = Literal["done", "current", "failed", "skipped"]


@dataclass(frozen=True)
class ProgramRequest:
    """One programming request. `serial` is only set when `trigger == "serial"`.
    `program_group_addresses`/`program_parameters` are carried through even
    though nothing downloads them yet, so a caller can log/surface that gap."""

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

        # Buttons, not Selectables - a Selectable has no visible boundary when
        # unselected (confirmed via the harness).
        card_height = 40.0
        spacing = imgui.get_style().item_spacing.x
        avail = imgui.get_content_region_avail().x
        card_size = imgui.ImVec2((avail - spacing) / 2, card_height)

        if _trigger_card(S.PROGRAM_TRIGGER_BUTTON, not self._trigger_serial, card_size):
            self._trigger_serial = False
        imgui.same_line()
        if _trigger_card(S.PROGRAM_TRIGGER_SERIAL, self._trigger_serial, card_size):
            self._trigger_serial = True

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
        if self._trigger_serial:
            imgui.set_next_item_width(_SERIAL_FIELD_WIDTH)
            _, serial_hex = imgui.input_text(
                "##program_serial",
                serial_hex,
                flags=imgui.InputTextFlags_.chars_hexadecimal
                | imgui.InputTextFlags_.callback_edit,
                callback=_limit_serial_length,
            )
            imgui.same_line()
        imgui.begin_disabled(not can_advance)
        if imgui.button(S.BTN_NEXT, _ACTION_BUTTON_SIZE):
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
        if imgui.button(S.BTN_BACK, _ACTION_BUTTON_SIZE):
            self._step = "find_device"
        imgui.same_line()
        imgui.begin_disabled(scope_empty)
        if imgui.button(S.BTN_PROGRAM, _ACTION_BUTTON_SIZE):
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
        """ASCII marks, not check/cross glyphs - the default font has no glyphs
        for those (confirmed via the harness: renders as tofu boxes)."""
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


def _limit_serial_length(data: imgui.InputTextCallbackData) -> int:
    """A focused input_text() keeps its own internal edit buffer and ignores
    the string passed back in on later frames (see `segmented_input.py`), so
    the 12-char cap has to be enforced here, live, rather than by truncating
    the returned value."""
    text = str(data.buf)[: data.buf_text_len]
    if len(text) > _SERIAL_HEX_LENGTH:
        data.delete_chars(_SERIAL_HEX_LENGTH, len(text) - _SERIAL_HEX_LENGTH)
    return 0


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
        imgui.push_style_color(imgui.Col_.button, _CARD_SELECTED_COLOR)
        imgui.push_style_color(imgui.Col_.button_hovered, _CARD_SELECTED_HOVERED_COLOR)
        imgui.push_style_color(imgui.Col_.button_active, _CARD_SELECTED_ACTIVE_COLOR)
    clicked = imgui.button(label, size)
    if selected:
        imgui.pop_style_color(3)
    return clicked


def _wrapped_error_box(text: str) -> None:
    imgui.push_style_color(imgui.Col_.child_bg, _ERROR_BG_COLOR)
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
