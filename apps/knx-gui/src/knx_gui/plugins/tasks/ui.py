"""Bottom status bar widget for background tasks - see apps/knx-gui/CLAUDE.md's
"Tasks plugin" section for the design."""

from __future__ import annotations

from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.color import color_u32
from knx_gui.plugins.tasks.service import Task, TaskStatus
from knx_gui.widgets import render_pulsing_dot

_ACCENT = imgui.ImVec4(0.26, 0.59, 0.98, 1.0)
_ERROR = imgui.ImVec4(0.9, 0.35, 0.35, 1.0)
_MAX_LABEL_LEN = 44
_DOT_SIZE = 12.0
_ICON_GAP = 6.0
_DIVIDER_GAP = 8.0


class TaskStatusWidget:
    def __init__(self, get_tasks: Callable[[], list[Task]]) -> None:
        self._get_tasks = get_tasks

    def render(self) -> None:
        tasks = self._get_tasks()
        running = [t for t in tasks if t.status == "running"]
        queued = [t for t in tasks if t.status == "queued"]
        errors = [t for t in tasks if t.status == "error"]

        if tasks:
            # tasks() orders running before queued before error.
            current = running[0] if running else errors[0] if errors else queued[0]
            status: TaskStatus | None = current.status
            label = _truncate(current.label)
            counts: str | None = _counts_text(running, queued, errors)
        else:
            status = None
            label = "No active tasks"
            counts = None

        content_w = _DOT_SIZE + _ICON_GAP + imgui.calc_text_size(label).x
        if counts is not None:
            content_w += (
                _DIVIDER_GAP
                + imgui.calc_text_size("|").x
                + _DIVIDER_GAP
                + imgui.calc_text_size(counts).x
            )
        window_w = imgui.get_window_size().x
        centered_x = (window_w - content_w) / 2
        imgui.set_cursor_pos_x(max(centered_x, imgui.get_cursor_pos_x()))

        imgui.push_style_color(imgui.Col_.child_bg, imgui.ImVec4(0, 0, 0, 0))
        imgui.push_style_var(imgui.StyleVar_.window_padding, imgui.ImVec2(0, 0))
        imgui.begin_child(
            "##task_pill",
            imgui.ImVec2(0, 0),
            imgui.ChildFlags_.auto_resize_x | imgui.ChildFlags_.auto_resize_y,
        )

        _dot_for_status(status)
        imgui.same_line(0, _ICON_GAP)
        _render_status_label(status, label)

        if counts is not None:
            imgui.same_line(0, _DIVIDER_GAP)
            imgui.text_disabled("|")
            imgui.same_line(0, _DIVIDER_GAP)
            imgui.text_disabled(counts)

        imgui.end_child()
        clicked = imgui.is_item_clicked()
        imgui.pop_style_var()
        imgui.pop_style_color()

        if clicked and tasks:
            imgui.open_popup("##task_popup")
        if imgui.begin_popup("##task_popup"):
            self._render_popup(running, queued, errors)
            imgui.end_popup()

    def _render_popup(
        self, running: list[Task], queued: list[Task], errors: list[Task]
    ) -> None:
        groups = [running, queued, errors]
        first = True
        for group in groups:
            if not group:
                continue
            if not first:
                imgui.spacing()
            first = False
            for task in group:
                _render_task_row(task)


def _render_task_row(task: Task) -> None:
    _dot_for_status(task.status)
    imgui.same_line(0, _ICON_GAP)
    _render_status_label(task.status, _truncate(task.label))
    if task.status == "error" and task.detail:
        wrap_x = imgui.get_cursor_pos_x() + 260
        imgui.push_text_wrap_pos(wrap_x)
        imgui.text_disabled(task.detail)
        imgui.pop_text_wrap_pos()


def _dot_for_status(status: TaskStatus | None) -> None:
    """Blue + pulsing while running, red + steady on error, dim + steady
    otherwise (queued or `None` for idle)."""
    cursor = imgui.get_cursor_screen_pos()
    text_height = imgui.get_text_line_height()
    center = imgui.ImVec2(cursor.x + _DOT_SIZE / 2, cursor.y + text_height / 2)
    if status == "running":
        render_pulsing_dot(_ACCENT, center=center)
    else:
        color = (
            _ERROR
            if status == "error"
            else imgui.get_style_color_vec4(imgui.Col_.text_disabled)
        )
        imgui.get_window_draw_list().add_circle_filled(
            center, 4, color_u32(color.x, color.y, color.z)
        )
    imgui.dummy(imgui.ImVec2(_DOT_SIZE, 0))


def _render_status_label(status: TaskStatus | None, label: str) -> None:
    if status == "error":
        imgui.text_colored(_ERROR, label)
    elif status == "queued" or status is None:
        imgui.text_disabled(label)
    else:
        imgui.text(label)


def _counts_text(running: list[Task], queued: list[Task], errors: list[Task]) -> str:
    text = f"{len(running)} active · {len(queued)} queued"
    if errors:
        text += f" · {len(errors)} error" + ("s" if len(errors) != 1 else "")
    return text


def _truncate(label: str) -> str:
    if len(label) <= _MAX_LABEL_LEN:
        return label
    return label[: _MAX_LABEL_LEN - 3] + "..."
