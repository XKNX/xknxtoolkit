from typing import TYPE_CHECKING

from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.node_editor.ui import NodeEditorPanel
from knx_gui.strings import S

if TYPE_CHECKING:
    from knx_gui.types import Device

NAVIGATE_TO_NODE_DURATION = 0.3


class NodeEditorPlugin:
    name = "node_editor"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api

        self._panel = NodeEditorPanel(
            get_devices=lambda: api.project.devices,
            get_links=lambda: api.project.links,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._handle_param_change,
            set_flag=self._handle_flag_change,
        )

        self._panels = [
            PanelDefinition(
                name="node_editor",
                label=S.PANEL_NODE_EDITOR,
                dock="MainDockSpace",
                render=self._panel.render,
            ),
        ]

        api.events.subscribe("device_selected", self._on_device_selected)

    def _add_link(self, start_pin: int, end_pin: int) -> int:
        return self._api.project.add_link_to_state(start_pin, end_pin)

    def _remove_link(self, link_id: int) -> None:
        self._api.project.remove_link_from_state(link_id)

    def _handle_param_change(self, device: "Device", param_id: str, new_value: str) -> None:
        self._api.project.set_param(device, param_id, new_value)

    def _handle_flag_change(
        self, device: "Device", co_id: str, flag_name: str, new_value: bool
    ) -> None:
        self._api.project.set_flag(device, co_id, flag_name, new_value)

    def _on_device_selected(self, device: "Device | None") -> None:
        if device:
            self._panel.select_node(device.node_id, False)
            self._panel.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)

    def get_selected_node_ids(self) -> list[int]:
        return self._panel.get_selected_node_ids()

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def setup(self) -> None:
        self._panel.setup()

    def shutdown(self) -> None:
        self._panel.shutdown()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
