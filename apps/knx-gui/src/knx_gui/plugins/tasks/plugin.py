"""Lifecycle wrapper for the tasks feature - owns the status bar widget and
gives `main.py` a `render_status_indicator()` to call alongside
`ConnectionPlugin`'s, matching how every other plugin is wired in rather than
`main.py` holding a raw `TaskStatusWidget` itself. No panels: the task list
only ever shows in the status bar's own popup, never a dockable window.
"""

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
