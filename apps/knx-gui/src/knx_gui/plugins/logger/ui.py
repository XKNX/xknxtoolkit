from __future__ import annotations

from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.plugins.logger.service import LogRecord
from knx_gui.plugins.logger.strings import S

LEVEL_COLORS: dict[str, tuple[float, float, float]] = {
    "debug": (0.5, 0.5, 0.55),
    "info": (0.85, 0.85, 0.85),
    "warning": (0.95, 0.75, 0.2),
    "error": (0.9, 0.35, 0.35),
    "critical": (1.0, 0.2, 0.2),
}
_DEFAULT_COLOR = (0.85, 0.85, 0.85)


class LogPanel:
    def __init__(
        self,
        get_records: Callable[[], list[LogRecord]],
        on_clear: Callable[[], None],
    ) -> None:
        self._get_records = get_records
        self._on_clear = on_clear
        self._filter_text = ""
        self._auto_scroll = True
        self._last_count = 0

    def render(self) -> None:
        self._render_toolbar()
        self._render_table()

    def _render_toolbar(self) -> None:
        records = self._get_records()
        imgui.text_disabled(str(len(records)))
        imgui.same_line()
        imgui.set_next_item_width(200)
        _, self._filter_text = imgui.input_text_with_hint(
            "##logfilter", S.FILTER_PLACEHOLDER, self._filter_text
        )
        imgui.same_line()
        if imgui.button(S.BTN_CLEAR):
            self._on_clear()
            self._last_count = 0

    def _render_table(self) -> None:
        records = self._get_records()
        if self._filter_text:
            fl = self._filter_text.lower()
            records = [
                r
                for r in records
                if fl in r.event.lower()
                or fl in r.plugin.lower()
                or fl in r.level.lower()
                or any(fl in v.lower() for v in r.payload.values())
            ]

        avail = imgui.get_content_region_avail()
        flags = (
            imgui.TableFlags_.row_bg
            | imgui.TableFlags_.scroll_y
            | imgui.TableFlags_.borders_inner_h
        )
        if not imgui.begin_table("##logs", 4, flags, imgui.ImVec2(avail.x, avail.y)):
            return

        imgui.table_setup_scroll_freeze(0, 1)
        imgui.table_setup_column(S.COL_TIME, imgui.TableColumnFlags_.width_fixed, 95)
        imgui.table_setup_column(S.COL_LEVEL, imgui.TableColumnFlags_.width_fixed, 60)
        imgui.table_setup_column(S.COL_PLUGIN, imgui.TableColumnFlags_.width_fixed, 90)
        imgui.table_setup_column(S.COL_MESSAGE, imgui.TableColumnFlags_.width_stretch)
        imgui.table_headers_row()

        for record in records:
            self._render_row(record)

        current_count = len(records)
        if self._auto_scroll and current_count > self._last_count:
            imgui.set_scroll_here_y(1.0)
        self._last_count = current_count

        imgui.end_table()

    def _render_row(self, record: LogRecord) -> None:
        r, g, b = LEVEL_COLORS.get(record.level, _DEFAULT_COLOR)
        imgui.table_next_row()

        imgui.table_set_column_index(0)
        imgui.text_disabled(record.timestamp_str)

        imgui.table_set_column_index(1)
        imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(r, g, b, 1.0))
        imgui.text(record.level.upper())
        imgui.pop_style_color()

        imgui.table_set_column_index(2)
        imgui.text_disabled(record.plugin)

        imgui.table_set_column_index(3)
        imgui.push_style_color(imgui.Col_.text, imgui.ImVec4(r, g, b, 1.0))
        imgui.text(record.event)
        imgui.pop_style_color()
        if record.payload:
            payload_str = "  " + "  ".join(f"{k}={v}" for k, v in record.payload.items())
            imgui.same_line(0, 0)
            imgui.text_disabled(payload_str)
