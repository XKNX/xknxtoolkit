"""Parameter-widget primitives shared by the Configure panel's Parameters section
(`knx_gui.plugins.project.ui.components.parameters_section`) and the Node Editor's
own per-node enum popup (`knx_gui.plugins.node_editor.ui`).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.strings import S
from xknxmono.product.parser_v2.ui import UiParameter
from xknxmono.product.parser_v2.ui.parameter import (
    CheckBoxWidget,
    EnumWidget,
    NumberSliderWidget,
    NumberWidget,
    PictureWidget,
    TextWidget,
)


@dataclass
class EnumPopupRequest:
    device: Device
    param: UiParameter


def render_param_widget(
    param: UiParameter,
    widget_id: str,
    on_change: Callable[[str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    match param.widget:
        case EnumWidget() as w:
            current_idx = 0
            for i, choice in enumerate(w.choices):
                if str(choice.value) == param.value:
                    current_idx = i
                    break
            preview = w.choices[current_idx].label if w.choices else param.value
            if deferred_enum:
                if imgui.button(f"{preview}##{widget_id}", imgui.ImVec2(-1, 0)):
                    return EnumPopupRequest(device=None, param=param)  # type: ignore[arg-type]
            else:
                if imgui.begin_combo(f"##{widget_id}", preview):
                    for choice in w.choices:
                        selected = str(choice.value) == param.value
                        if imgui.selectable(choice.label, selected)[0]:
                            on_change(str(choice.value))
                    imgui.end_combo()
        case NumberWidget() | NumberSliderWidget() as w:
            _render_int_param(widget_id, param.value, w.min, w.max, on_change)
        case CheckBoxWidget():
            checked = param.value == "1"
            changed, new_checked = imgui.checkbox(f"##{widget_id}", checked)
            if changed:
                on_change("1" if new_checked else "0")
        case TextWidget():
            _, new_value = imgui.input_text(f"##{widget_id}", param.value)
            if imgui.is_item_deactivated_after_edit():
                on_change(new_value)
        case PictureWidget():
            imgui.text_disabled(S.IMAGE_PLACEHOLDER)
        case _:
            _, new_value = imgui.input_text(f"##{widget_id}", param.value)
            if imgui.is_item_deactivated_after_edit():
                on_change(new_value)
    return None


def _render_int_param(
    widget_id: str,
    value: str,
    min_value: int | None,
    max_value: int | None,
    on_change: Callable[[str], None],
) -> None:
    _, new_text = imgui.input_text(
        f"##{widget_id}", value, imgui.InputTextFlags_.chars_decimal
    )
    if imgui.is_item_deactivated_after_edit():
        try:
            clamped = int(new_text)
        except ValueError:
            clamped = min_value if min_value is not None else 0
        if min_value is not None:
            clamped = max(min_value, clamped)
        if max_value is not None:
            clamped = min(max_value, clamped)
        if str(clamped) != value:
            on_change(str(clamped))


class EnumPopup:
    def __init__(
        self,
        popup_id: str,
        on_change: Callable[[Device, str, str], None],
    ) -> None:
        self._popup_id = popup_id
        self._on_change = on_change
        self._request: EnumPopupRequest | None = None
        self._active: EnumPopupRequest | None = None

    def request(self, device: Device, param: UiParameter) -> None:
        self._request = EnumPopupRequest(device=device, param=param)

    def render(self) -> None:
        if self._request is not None:
            self._active = self._request
            self._request = None
            imgui.open_popup(self._popup_id)

        if imgui.begin_popup(self._popup_id):
            target = self._active
            if target is not None and isinstance(target.param.widget, EnumWidget):
                for choice in target.param.widget.choices:
                    selected = str(choice.value) == target.param.value
                    if imgui.menu_item(choice.label, "", selected)[0]:
                        self._on_change(
                            target.device, target.param.ref_id, str(choice.value)
                        )
            imgui.end_popup()
        else:
            self._active = None
