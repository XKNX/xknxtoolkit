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
        # Snapshot of the device (and destructive reset mode) the "Confirm
        # Reset" popup was opened for, taken at open_popup time so the popup's
        # target is fixed for its lifetime - not re-derived from the per-frame
        # `device` argument every frame. Without this, an out-of-band selected-
        # device change while the modal is open (e.g. the app-level Ctrl+Z
        # shortcut handler firing ProjectService.undo(), which can leave the
        # selected device as None and trip ConfigurePanel.render's `devices[0]`
        # fallback to a different device) would silently re-target the confirm
        # button at that other device - a destructive master-reset dispatched to
        # the wrong individual address.
        self._pending_device: Device | None = None
        self._pending_mode: _ResetMode | None = None

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
                self._pending_device = device
                self._pending_mode = selected
                imgui.open_popup(S.POPUP_CONFIRM_RESET_TITLE)
            else:
                self._do_restart(device, selected)
        imgui.end_disabled()

        imgui.unindent()

        # The popup reads from the open-time snapshot (set above), not the
        # per-frame `device`/`selected`, so its target stays fixed for the
        # lifetime of the modal even if the selected device changes underneath
        # it. Called right after the button so a same-frame open_popup() (above)
        # is seen by this begin_popup_modal() before the frame ends - no need to
        # defer opening it to the next frame.
        pending_device = (
            device if self._pending_device is None else self._pending_device
        )
        pending_mode = selected if self._pending_mode is None else self._pending_mode
        self._render_reset_confirm_popup(pending_device, pending_mode)

    def _render_reset_confirm_popup(self, device: Device, selected: _ResetMode) -> None:
        opened = imgui.begin_popup_modal(
            S.POPUP_CONFIRM_RESET_TITLE, flags=imgui.WindowFlags_.always_auto_resize
        )[0]
        if opened:
            imgui.text(
                S.POPUP_CONFIRM_RESET_TEXT.format(
                    mode=selected.label, device=device.name
                )
            )
            imgui.separator()
            if imgui.button(S.BTN_RESET, imgui.ImVec2(75, 0)):
                self._do_restart(device, selected)
                self._clear_pending_reset()
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                self._clear_pending_reset()
                imgui.close_current_popup()
            imgui.end_popup()
        elif self._pending_device is not None and not imgui.is_popup_open(
            S.POPUP_CONFIRM_RESET_TITLE, imgui.PopupFlags_.any_popup_id
        ):
            # The popup closed without our Reset/Cancel buttons (Escape, the
            # parent window closing, etc.): drop the snapshot so it can't leak
            # into the next open of the same popup. `any_popup_id` checks the
            # popup's open state globally (not just the current popup-stack
            # level), so the guard stays accurate from outside the popup's own
            # begin/end. It also covers the same-frame open_popup() case: even
            # if a begin_popup_modal() on the open-click frame returned False on
            # some config, `any_popup_id` would already report the popup as
            # open, keeping the snapshot for the next frame's render - so the
            # snapshot is only dropped once the popup is genuinely closed.
            self._clear_pending_reset()

    def _clear_pending_reset(self) -> None:
        self._pending_device = None
        self._pending_mode = None

    def _do_restart(self, device: Device, mode: _ResetMode) -> None:
        self._on_restart_device(
            device,
            RestartRequest(
                master_reset=mode.master_reset,
                erase_code=mode.erase_code,
                channel_number=0,
            ),
        )
