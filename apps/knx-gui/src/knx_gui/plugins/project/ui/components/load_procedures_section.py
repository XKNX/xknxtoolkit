"""The Configure panel's Load Procedures section: each procedure as a collapsible
tree node listing its steps in a table.

See `knx_gui.plugins.project.ui.components` for why this lives here and not in
`knx_gui.widgets`.
"""

from __future__ import annotations

from typing import Any

from imgui_bundle import imgui

_TABLE_FLAGS = (
    imgui.TableFlags_.borders_outer
    | imgui.TableFlags_.borders_inner_v
    | imgui.TableFlags_.sizing_stretch_prop
)


class LoadProceduresSection:
    def render(self, lp: Any, procedures: list[Any]) -> None:
        imgui.text_disabled(getattr(lp, "style", ""))
        for i, proc in enumerate(procedures):
            label = f"Procedure {i + 1}  ({len(proc.steps)} steps)##lp{i}"
            if imgui.tree_node(label):
                self._render_steps_table(i, proc)
                imgui.tree_pop()

    def _render_steps_table(self, index: int, proc: Any) -> None:
        if not imgui.begin_table(f"##lpt{index}", 3, _TABLE_FLAGS):
            return
        imgui.table_setup_column("Kind", imgui.TableColumnFlags_.width_stretch, 0.3)
        imgui.table_setup_column(
            "Applies To", imgui.TableColumnFlags_.width_stretch, 0.15
        )
        imgui.table_setup_column("Details", imgui.TableColumnFlags_.width_stretch, 0.55)
        imgui.table_headers_row()
        for step in proc.steps:
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            imgui.text(step.kind)
            imgui.table_set_column_index(1)
            imgui.text_disabled(step.applies_to)
            imgui.table_set_column_index(2)
            imgui.text_disabled(step.details)
        imgui.end_table()
