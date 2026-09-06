"""A bounded numeric input segment with auto-advance and live clamping.

Styled after classic IP-address input controls: several of these chained
together (each with its own max length/value) make up one dotted address.
"""

from typing import NamedTuple

from imgui_bundle import imgui


class SegmentResult(NamedTuple):
    value: str
    advance: bool
    deactivated: bool
    active: bool


def render_bounded_numeric_segment(
    id_str: str, value: str, max_len: int, max_value: int
) -> SegmentResult:
    """Render one digit-only, length-capped, value-clamped input segment.

    Typing "." - like the "." key on a classic IP address control - skips
    straight to the next segment instead of being inserted; so does typing
    (or being clamped down to) ``max_len`` characters. Both are reported via
    ``advance``, so the caller can move keyboard focus to whatever segment
    comes next.

    A value typed above ``max_value``, or any non-digit character, is
    corrected live - including while the widget is still active. Dear ImGui
    text widgets that currently have focus keep their own internal edit
    buffer and ignore the `value` passed back in on later frames, so this
    has to happen inside a ``callback_edit`` pass over the live buffer
    (``delete_chars``/``insert_chars``), not by returning a cleaned-up
    string for the caller to pass in next time.
    """
    advance = [False]

    def _filter(data: imgui.InputTextCallbackData) -> int:
        if data.event_flag == imgui.InputTextFlags_.callback_edit:
            text = str(data.buf)[: data.buf_text_len]
            digits = "".join(c for c in text if c.isdigit())[:max_len]
            clamped = str(min(int(digits), max_value)) if digits else ""
            if clamped != text:
                data.delete_chars(0, data.buf_text_len)
                if clamped:
                    data.insert_chars(0, clamped)
            return 0
        # callback_char_filter: only "." needs special handling here - every
        # other non-digit character, excess length and an out-of-range value
        # are all cleaned up by the callback_edit pass above.
        if chr(data.event_char) == ".":
            advance[0] = True
            return 1
        return 0

    imgui.set_next_item_width(24 if max_len == 2 else 32)
    changed, new_value = imgui.input_text_with_hint(
        id_str,
        "0",
        value,
        flags=imgui.InputTextFlags_.callback_char_filter
        | imgui.InputTextFlags_.callback_edit,
        callback=_filter,
    )
    if changed and len(new_value) >= max_len:
        advance[0] = True
    return SegmentResult(
        new_value,
        advance[0],
        imgui.is_item_deactivated_after_edit(),
        imgui.is_item_active(),
    )
