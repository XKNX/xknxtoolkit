"""The Configure panel's Advanced Actions section: pick a restart/reset mode and,
for destructive modes, confirm before sending it.

See `knx_gui.plugins.project.ui.components` for why this lives here and not in
`knx_gui.widgets`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S


@dataclass(frozen=True)
class _ResetMode:
    """One selectable entry in the reset-mode dropdown.

    ``erase_code`` is only meaningful when ``master_reset`` is True - see
    KNX v02.01.02 - Management Procedures 03.05.02 - §3.7.1.2.3.1, Table 4.
    ``destructive`` marks every mode that actually resets a Resource -
    anything but Basic Restart and Confirmed Restart - and gates the
    confirmation popup.

    Table 4 lets several of these Erase Codes scope to a single Channel
    Number instead of the whole device; there's no UI for that yet, so
    every request is sent with Channel Number 00h ("all Channels"), which
    every Erase Code accepts.
    """

    label: str
    master_reset: bool
    erase_code: int
    destructive: bool


def _reset_modes() -> list[_ResetMode]:
    """Build the dropdown entries fresh so labels pick up the current locale."""
    return [
        _ResetMode(S.RESET_MODE_BASIC_RESTART, False, 0, False),
        _ResetMode(S.RESET_MODE_CONFIRMED_RESTART, True, 0x01, False),
        _ResetMode(S.RESET_MODE_FACTORY_RESET, True, 0x02, True),
        _ResetMode(S.RESET_MODE_RESET_IA, True, 0x03, True),
        _ResetMode(S.RESET_MODE_RESET_AP, True, 0x04, True),
        _ResetMode(S.RESET_MODE_RESET_PARAM, True, 0x05, True),
        _ResetMode(S.RESET_MODE_RESET_LINKS, True, 0x06, True),
        _ResetMode(S.RESET_MODE_FACTORY_RESET_NO_IA, True, 0x07, True),
        _ResetMode(S.RESET_MODE_ERASE_APP_DATA, True, 0x08, True),
    ]


@dataclass(frozen=True)
class RestartRequest:
    """Parameters for one restart/reset call, matching dm_restart's own signature."""

    master_reset: bool
    erase_code: int
    channel_number: int


class RestartSection:
    def __init__(
        self, on_restart_device: Callable[[Device, RestartRequest], None]
    ) -> None:
        self._on_restart_device = on_restart_device
        self._reset_mode_index: int = 0

    def render(self, device: Device) -> None:
        modes = _reset_modes()
        mode_labels = [mode.label for mode in modes]

        imgui.text(S.CONFIGURE_RESET_HEADER)
        imgui.indent()

        imgui.set_next_item_width(220)
        _, self._reset_mode_index = imgui.combo(
            "##reset_mode", self._reset_mode_index, mode_labels
        )
        selected = modes[self._reset_mode_index]

        button_size = imgui.ImVec2(110, 0)
        imgui.same_line()
        avail = imgui.get_content_region_avail().x
        if avail > button_size.x:
            imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + avail - button_size.x)
        enabled = bool(device.individual_address)
        imgui.begin_disabled(not enabled)
        if imgui.button(S.BTN_RESET, button_size):
            if selected.destructive:
                imgui.open_popup(S.POPUP_CONFIRM_RESET_TITLE)
            else:
                self._do_restart(device, selected)
        imgui.end_disabled()

        imgui.unindent()

        # Called right after the button so a same-frame open_popup() (above)
        # is seen by this begin_popup_modal() before the frame ends - no
        # need to defer opening it to the next frame.
        self._render_reset_confirm_popup(device, selected)

    def _render_reset_confirm_popup(self, device: Device, selected: _ResetMode) -> None:
        if imgui.begin_popup_modal(
            S.POPUP_CONFIRM_RESET_TITLE, flags=imgui.WindowFlags_.always_auto_resize
        )[0]:
            imgui.text(
                S.POPUP_CONFIRM_RESET_TEXT.format(
                    mode=selected.label, device=device.name
                )
            )
            imgui.separator()
            if imgui.button(S.BTN_RESET, imgui.ImVec2(75, 0)):
                self._do_restart(device, selected)
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

    def _do_restart(self, device: Device, mode: _ResetMode) -> None:
        self._on_restart_device(
            device,
            RestartRequest(
                master_reset=mode.master_reset,
                erase_code=mode.erase_code,
                channel_number=0,
            ),
        )
