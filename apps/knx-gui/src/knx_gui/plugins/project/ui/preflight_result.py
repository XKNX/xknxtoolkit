"""A result window for a device pre-flight (dry run).

Shows whether the device already matches the configuration and, per memory segment / property,
how many bytes would change. The pre-flight runs on a background thread; its result is handed in via
:meth:`submit_result` / :meth:`submit_error` (thread-safe) and picked up on the next UI frame. The
window can export the current (Ist) and planned (Soll) bytes of every location to a text file.
"""

from __future__ import annotations

import contextlib
import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S

if TYPE_CHECKING:
    from xknxmono.download.preflight import PreflightReport, SegmentDiff

_GREEN = imgui.ImVec4(0.4, 0.85, 0.45, 1.0)
_ORANGE = imgui.ImVec4(0.95, 0.75, 0.2, 1.0)
_RED = imgui.ImVec4(0.9, 0.35, 0.35, 1.0)
_BLUE = imgui.ImVec4(0.45, 0.7, 0.95, 1.0)


class PreflightResultWindow:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Set from the worker thread, consumed on the UI thread.
        self._pending: (
            tuple[str, str, PreflightReport | None, str | None, frozenset[int]] | None
        ) = None
        self._label = ""
        self._scope = ""
        self._report: PreflightReport | None = None
        self._error: str | None = None
        # Absolute addresses of device-managed (runtime) bytes, e.g. a download
        # detection byte the firmware resets after a download; a difference there
        # is benign, so those locations are annotated instead of flagged.
        self._runtime: frozenset[int] = frozenset()
        self._show = False
        self._save_path_buf = "preflight.txt"

    # -- worker thread: no imgui here -------------------------------------
    def submit_result(
        self,
        label: str,
        scope: str,
        report: PreflightReport,
        runtime_addresses: set[int] | frozenset[int] = frozenset(),
    ) -> None:
        with self._lock:
            self._pending = (label, scope, report, None, frozenset(runtime_addresses))

    def submit_error(self, label: str, scope: str, error: str) -> None:
        with self._lock:
            self._pending = (label, scope, None, error, frozenset())

    # -- UI thread --------------------------------------------------------
    def render(self) -> None:
        with self._lock:
            if self._pending is not None:
                (
                    self._label,
                    self._scope,
                    self._report,
                    self._error,
                    self._runtime,
                ) = self._pending
                self._pending = None
                self._show = True
        if not self._show:
            return
        imgui.set_next_window_size(imgui.ImVec2(720, 520), imgui.Cond_.first_use_ever)
        opened, p_open = imgui.begin(S.PREFLIGHT_RESULT_TITLE, self._show)
        if p_open is not None:
            self._show = p_open
        if opened:
            self._render_body()
        imgui.end()

    def _render_body(self) -> None:
        imgui.text_disabled(f"{self._label}    scope={self._scope}")
        imgui.same_line()
        # Text is plain (not selectable), so offer explicit copy-to-clipboard.
        if imgui.small_button(S.COPY_LOG):
            imgui.set_clipboard_text(self._clipboard_text())
        imgui.separator()
        # Reassure up front: a test never writes to the device.
        imgui.text_disabled(S.PREFLIGHT_NO_CHANGES_MADE)
        imgui.spacing()

        if self._error is not None:
            imgui.push_style_color(imgui.Col_.text, _RED)
            imgui.text_wrapped(f"{S.PREFLIGHT_FAILED}: {self._error}")
            imgui.pop_style_color()
            return

        report = self._report
        if report is None:
            return

        # Split real changes from device-managed (runtime) byte differences, which
        # are benign (the firmware sets them after a download).
        real_segments = [
            s
            for s in report.changed_segments
            if not self._segment_runtime_only(s)
        ]
        runtime_segments = [
            s for s in report.changed_segments if self._segment_runtime_only(s)
        ]
        real_locations = len(real_segments) + len(report.changed_properties)
        real_bytes = sum(s.changed_bytes for s in real_segments) + sum(
            p.changed_bytes for p in report.changed_properties
        )
        if real_locations:
            imgui.push_style_color(imgui.Col_.text, _ORANGE)
            imgui.text(
                S.PREFLIGHT_WOULD_CHANGE.format(
                    bytes=real_bytes, locations=real_locations
                )
            )
            imgui.pop_style_color()
        else:
            imgui.push_style_color(imgui.Col_.text, _GREEN)
            imgui.text(S.PREFLIGHT_MATCH)
            imgui.pop_style_color()
        if runtime_segments:
            runtime_bytes = sum(s.changed_bytes for s in runtime_segments)
            imgui.text_disabled(S.PREFLIGHT_RUNTIME_NOTE.format(bytes=runtime_bytes))

        matched = sum(1 for s in report.segments if not s.changed) + sum(
            1 for p in report.properties if not p.changed
        )
        imgui.text_disabled(
            S.PREFLIGHT_SUMMARY_COUNTS.format(matched=matched, changed=real_locations)
        )

        if imgui.button(S.PREFLIGHT_EXPORT):
            imgui.open_popup("##preflight_export")
        self._render_export_modal(report)
        imgui.separator()
        self._render_table(report)

    def _render_table(self, report: PreflightReport) -> None:
        flags = (
            imgui.TableFlags_.row_bg
            | imgui.TableFlags_.borders_inner_h
            | imgui.TableFlags_.scroll_y
        )
        avail = imgui.get_content_region_avail()
        if not imgui.begin_table(
            "##preflight", 4, flags, imgui.ImVec2(avail.x, avail.y)
        ):
            return
        imgui.table_setup_scroll_freeze(0, 1)
        imgui.table_setup_column(S.PREFLIGHT_COL_LOCATION)
        imgui.table_setup_column(
            S.PREFLIGHT_COL_SIZE, imgui.TableColumnFlags_.width_fixed, 70
        )
        imgui.table_setup_column(
            S.PREFLIGHT_COL_STATUS, imgui.TableColumnFlags_.width_fixed, 120
        )
        imgui.table_setup_column(
            S.PREFLIGHT_COL_CHANGED, imgui.TableColumnFlags_.width_fixed, 90
        )
        imgui.table_headers_row()

        for segment in report.segments:
            self._render_row(
                S.PREFLIGHT_MEM_LABEL.format(address=f"{segment.address:#06x}"),
                len(segment.planned),
                segment.changed,
                segment.changed_bytes,
                runtime=self._segment_runtime_only(segment),
            )
        for prop in report.properties:
            self._render_row(
                S.PREFLIGHT_PROP_LABEL.format(
                    object=prop.object_index, property=prop.property_id
                ),
                len(prop.planned),
                prop.changed,
                prop.changed_bytes,
            )
        imgui.end_table()

    def _segment_runtime_only(self, segment: SegmentDiff) -> bool:
        """Whether every changed byte of ``segment`` is a device-managed runtime byte."""
        if not segment.changed or not self._runtime:
            return False
        return all(
            segment.address + r.start + i in self._runtime
            for r in segment.changed_ranges
            for i in range(r.length)
        )

    def _render_row(
        self,
        location: str,
        size: int,
        changed: bool,
        changed_bytes: int,
        runtime: bool = False,
    ) -> None:
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        imgui.text(location)
        imgui.table_set_column_index(1)
        imgui.text_disabled(f"{size} B")
        imgui.table_set_column_index(2)
        if runtime:
            imgui.push_style_color(imgui.Col_.text, _BLUE)
            imgui.text(S.PREFLIGHT_STATUS_RUNTIME)
            imgui.pop_style_color()
            if imgui.is_item_hovered():
                imgui.set_tooltip(S.PREFLIGHT_RUNTIME_TOOLTIP)
        else:
            color = _ORANGE if changed else _GREEN
            label = S.PREFLIGHT_STATUS_CHANGE if changed else S.PREFLIGHT_STATUS_MATCH
            imgui.push_style_color(imgui.Col_.text, color)
            imgui.text(label)
            imgui.pop_style_color()
        imgui.table_set_column_index(3)
        imgui.text_disabled(str(changed_bytes) if changed else "-")

    def _render_export_modal(self, report: PreflightReport) -> None:
        imgui.set_next_window_size(imgui.ImVec2(520, 0), imgui.Cond_.always)
        if not imgui.begin_popup_modal(
            "##preflight_export",
            None,
            imgui.WindowFlags_.no_title_bar | imgui.WindowFlags_.always_auto_resize,
        )[0]:
            return
        imgui.text(S.PREFLIGHT_EXPORT_PATH)
        imgui.set_next_item_width(-1)
        _, self._save_path_buf = imgui.input_text("##pf_path", self._save_path_buf)
        imgui.spacing()
        btn_w = imgui.ImVec2(120, 0)
        if imgui.button(S.BTN_SAVE, btn_w):
            with contextlib.suppress(OSError):
                Path(self._save_path_buf).write_text(
                    self._export_text(report), encoding="utf-8"
                )
            imgui.close_current_popup()
        imgui.same_line()
        if imgui.button(S.BTN_CANCEL, btn_w):
            imgui.close_current_popup()
        imgui.end_popup()

    def _clipboard_text(self) -> str:
        header = f"{self._label} scope={self._scope}"
        if self._error is not None:
            return f"{header}\n{S.PREFLIGHT_FAILED}: {self._error}"
        if self._report is not None:
            return f"{header}\n{self._export_text(self._report)}"
        return header

    def _export_text(self, report: PreflightReport) -> str:
        lines = [
            f"# Pre-flight {self._label} scope={self._scope} "
            f"generated={datetime.now().isoformat(timespec='seconds')}",
            report.summary(),
            "",
        ]
        for segment in report.segments:
            lines.append(
                f"## memory {segment.address:#06x} ({len(segment.planned)}B) "
                f"changed={segment.changed_bytes}"
            )
            lines.append(f"ist : {segment.current.hex()}")
            lines.append(f"soll: {segment.planned.hex()}")
        for prop in report.properties:
            lines.append(
                f"## object {prop.object_index} property {prop.property_id} "
                f"changed={prop.changed_bytes}"
            )
            lines.append(f"ist : {prop.current.hex()}")
            lines.append(f"soll: {prop.planned.hex()}")
        return "\n".join(lines) + "\n"
