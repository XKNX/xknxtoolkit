from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.constants import LINK_INVALID_COLOR
from knx_gui.strings import S
from knx_gui.types import ComObject, Device


@dataclass
class PendingParamChange:
    device: Device
    param_id: str
    value: str
    hidden_cos: list[ComObject]
    affected_links: list[tuple[int, int, int]]


class LinkWarningDialog:
    def __init__(
        self,
        on_confirm: Callable[[Device, str, str, list[tuple[int, int, int]]], None],
    ) -> None:
        self._on_confirm = on_confirm
        self._pending: PendingParamChange | None = None
        self._show_popup: bool = False

    def request_confirmation(
        self,
        device: Device,
        param_id: str,
        value: str,
        hidden_cos: list[ComObject],
        affected_links: list[tuple[int, int, int]],
    ) -> None:
        self._pending = PendingParamChange(
            device=device,
            param_id=param_id,
            value=value,
            hidden_cos=hidden_cos,
            affected_links=affected_links,
        )
        self._show_popup = True

    def render(self) -> None:
        if self._show_popup:
            imgui.open_popup("##LinkWarning")
            self._show_popup = False

        center = imgui.get_main_viewport().get_center()
        imgui.set_next_window_pos(center, imgui.Cond_.appearing, imgui.ImVec2(0.5, 0.5))

        if imgui.begin_popup_modal(
            "##LinkWarning", None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            pending = self._pending
            if pending is None:
                imgui.close_current_popup()
                imgui.end_popup()
                return

            imgui.text(S.LINK_WARNING_HIDE_COM_OBJECTS)
            imgui.spacing()
            for co in pending.hidden_cos:
                imgui.bullet_text(co.name)
            imgui.spacing()
            imgui.push_style_color(imgui.Col_.text, LINK_INVALID_COLOR)
            imgui.text(S.LINK_WARNING_REMOVED.format(count=len(pending.affected_links)))
            imgui.pop_style_color()
            imgui.spacing()
            imgui.separator()
            imgui.spacing()

            if imgui.button(S.BTN_REMOVE_LINKS, imgui.ImVec2(120, 0)):
                self._on_confirm(
                    pending.device,
                    pending.param_id,
                    pending.value,
                    pending.affected_links,
                )
                self._pending = None
                imgui.close_current_popup()

            imgui.same_line()

            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(120, 0)):
                self._pending = None
                imgui.close_current_popup()

            imgui.end_popup()
