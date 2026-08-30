"""Project information view: the ETS project metadata carried over on import."""

from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S

if TYPE_CHECKING:
    from knx_gui.plugins.project.service import _ProjectInfo


class ProjectInfoPanel:
    def __init__(self, get_project_info: "Callable[[], _ProjectInfo | None]") -> None:
        self._get_project_info = get_project_info

    def render(self) -> None:
        info = self._get_project_info()
        if info is None:
            imgui.text_disabled(S.PROJECT_INFO_EMPTY)
            return
        rows = [
            (S.PROJECT_INFO_NAME, info.name),
            (S.PROJECT_INFO_GA_STYLE, info.group_address_style),
            (S.PROJECT_INFO_CREATED_BY, info.created_by),
            (S.PROJECT_INFO_TOOL_VERSION, info.tool_version),
            (S.PROJECT_INFO_SCHEMA_VERSION, info.schema_version),
            (S.PROJECT_INFO_LAST_MODIFIED, info.last_modified),
            (S.PROJECT_INFO_GUID, info.guid),
        ]
        flags = imgui.TableFlags_.borders_inner | imgui.TableFlags_.sizing_stretch_prop
        if not imgui.begin_table("##project_info", 2, flags):
            return
        imgui.table_setup_column("", imgui.TableColumnFlags_.width_stretch, 0.35)
        imgui.table_setup_column("", imgui.TableColumnFlags_.width_stretch, 0.65)
        for label, value in rows:
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            imgui.text_disabled(label)
            imgui.table_set_column_index(1)
            imgui.text_wrapped(value or "-")
        imgui.end_table()
