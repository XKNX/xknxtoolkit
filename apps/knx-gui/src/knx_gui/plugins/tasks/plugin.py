"""Lifecycle wrapper for the tasks feature - see apps/knx-gui/CLAUDE.md's
"Tasks plugin" section for the design. No panels: the task list only ever
shows in the status bar's own popup."""

from __future__ import annotations

from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.tasks.ui import TaskStatusWidget


class TasksPlugin:
    name = "tasks"

    def __init__(self, api: PluginAPI) -> None:
        self._widget = TaskStatusWidget(api.tasks.tasks)

    @property
    def panels(self) -> list[PanelDefinition]:
        return []

    def render_status_indicator(self) -> None:
        self._widget.render()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
