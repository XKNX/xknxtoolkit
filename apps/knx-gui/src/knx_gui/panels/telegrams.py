from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.strings import S
from knx_gui.types import Telegram

TELEGRAM_HEADER_BUTTONS_WIDTH = 100


@dataclass
class TelegramColumn:
    name: str
    getter: Callable[[Telegram], str]
    stretch: bool = False
    disabled: bool = False


TELEGRAM_COLUMNS: list[TelegramColumn] = [
    TelegramColumn("Time", lambda t: t.timestamp),
    TelegramColumn("Source", lambda t: t.source),
    TelegramColumn("Destination", lambda t: t.destination),
    TelegramColumn("Service", lambda t: t.service),
    TelegramColumn("DPT", lambda t: t.dpt, disabled=True),
    TelegramColumn("Value", lambda t: t.value, stretch=True),
]


class TelegramsPanel:
    def __init__(
        self,
        get_telegrams: Callable[[], list[Telegram]],
        on_focus_source: Callable[[str], None],
    ) -> None:
        self._get_telegrams = get_telegrams
        self._on_focus_source = on_focus_source
        self._selected: set[int] = set()
        self._last_selected: int = -1

    def render(self) -> None:
        self._render_header()
        self._handle_shortcuts()
        self._render_table()

    def _render_header(self) -> None:
        imgui.text(S.TELEGRAMS_TITLE)
        if self._selected:
            imgui.same_line()
            imgui.text_disabled(
                f"  {S.TELEGRAMS_SELECTED.format(count=len(self._selected))}"
            )
        imgui.same_line(imgui.get_window_width() - TELEGRAM_HEADER_BUTTONS_WIDTH)
        if imgui.small_button(S.BTN_COPY):
            self._copy_telegrams()
        imgui.same_line()
        if imgui.small_button(S.BTN_CLEAR):
            self._selected.clear()
        imgui.separator()

    def _handle_shortcuts(self) -> None:
        if not imgui.is_window_focused():
            return
        io = imgui.get_io()
        if (io.key_ctrl or io.key_super) and imgui.is_key_pressed(imgui.Key.c):
            self._copy_telegrams()

    def _render_table(self) -> None:
        telegrams = self._get_telegrams()
        flags = (
            imgui.TableFlags_.borders_inner_h
            | imgui.TableFlags_.row_bg
            | imgui.TableFlags_.scroll_y
            | imgui.TableFlags_.sizing_fixed_fit
        )
        if not imgui.begin_table("##telegrams_table", len(TELEGRAM_COLUMNS), flags):
            return

        for column in TELEGRAM_COLUMNS:
            col_flags = (
                imgui.TableColumnFlags_.width_stretch
                if column.stretch
                else imgui.TableColumnFlags_.none
            )
            imgui.table_setup_column(column.name, col_flags)
        imgui.table_headers_row()

        for i, telegram in enumerate(telegrams):
            self._render_row(i, telegram)

        imgui.end_table()

    def _render_row(self, index: int, telegram: Telegram) -> None:
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        selected = index in self._selected
        flags = (
            imgui.SelectableFlags_.span_all_columns
            | imgui.SelectableFlags_.allow_overlap
        )
        if imgui.selectable(f"{telegram.timestamp}##row{index}", selected, flags)[0]:
            self._handle_click(index)

        for col_index, column in enumerate(TELEGRAM_COLUMNS[1:], start=1):
            imgui.table_set_column_index(col_index)
            text = column.getter(telegram)
            if column.disabled:
                imgui.text_disabled(text)
            else:
                imgui.text(text)

    def _handle_click(self, index: int) -> None:
        io = imgui.get_io()
        ctrl = io.key_ctrl or io.key_super
        shift = io.key_shift

        if shift and self._last_selected >= 0:
            self._select_range(self._last_selected, index, additive=ctrl)
        elif ctrl:
            self._toggle(index)
        else:
            self._select_single(index)

    def _select_range(self, start: int, end: int, additive: bool) -> None:
        if not additive:
            self._selected.clear()
        lo, hi = min(start, end), max(start, end)
        self._selected.update(range(lo, hi + 1))

    def _toggle(self, index: int) -> None:
        self._selected.symmetric_difference_update({index})
        self._last_selected = index

    def _select_single(self, index: int) -> None:
        telegrams = self._get_telegrams()
        self._selected = {index}
        self._last_selected = index
        if index < len(telegrams):
            self._on_focus_source(telegrams[index].source)

    def _copy_telegrams(self) -> None:
        telegrams = self._get_telegrams()
        if self._selected:
            indices = sorted(self._selected)
        else:
            indices = list(range(len(telegrams)))
        if not indices:
            return

        header = "\t".join(col.name for col in TELEGRAM_COLUMNS)
        rows = [
            self._telegram_to_row(telegrams[i]) for i in indices if i < len(telegrams)
        ]
        imgui.set_clipboard_text("\n".join([header, *rows]))

    def _telegram_to_row(self, telegram: Telegram) -> str:
        return "\t".join(col.getter(telegram) for col in TELEGRAM_COLUMNS)
