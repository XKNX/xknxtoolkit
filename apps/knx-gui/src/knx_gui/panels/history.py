from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.strings import S


@dataclass
class HistoryEntry:
    id: int
    display_text: str
    reverted: bool


class HistoryPanel:
    def __init__(
        self,
        get_entries: Callable[[], list[HistoryEntry]],
        get_cursor: Callable[[], int],
        on_jump_to: Callable[[int], None],
    ) -> None:
        self._get_entries = get_entries
        self._get_cursor = get_cursor
        self._on_jump_to = on_jump_to

    def render(self) -> None:
        entries = self._get_entries()
        cursor = self._get_cursor()

        if not entries:
            imgui.text_disabled(S.HISTORY_NO_HISTORY)
            return

        for entry in entries:
            is_current = entry.id == cursor

            if entry.reverted:
                imgui.push_style_color(imgui.Col_.text, imgui.get_style_color_vec4(imgui.Col_.text_disabled))

            row_min_y = imgui.get_cursor_screen_pos().y
            if is_current:
                draw_list = imgui.get_window_draw_list()
                cursor_pos = imgui.get_cursor_screen_pos()
                text_height = imgui.get_text_line_height()
                center = imgui.ImVec2(cursor_pos.x + 6, cursor_pos.y + text_height / 2)
                draw_list.add_circle_filled(center, 4, imgui.get_color_u32(imgui.ImVec4(0.2, 0.8, 0.3, 1.0)))
            imgui.dummy(imgui.ImVec2(14, 0))
            imgui.same_line()

            imgui.text(entry.display_text)
            row_max_y = imgui.get_cursor_screen_pos().y

            mouse_pos = imgui.get_mouse_pos()
            window_pos = imgui.get_window_pos()
            window_size = imgui.get_window_size()
            row_hovered = (
                row_min_y <= mouse_pos.y < row_max_y
                and window_pos.x <= mouse_pos.x < window_pos.x + window_size.x
            )

            if row_hovered and not is_current:
                imgui.same_line(imgui.get_content_region_avail().x - 36)
                if imgui.small_button(f"{S.HISTORY_REVERT}##{entry.id}"):
                    self._on_jump_to(entry.id)

            if entry.reverted:
                imgui.pop_style_color()
