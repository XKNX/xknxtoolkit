from collections.abc import Callable
from typing import TYPE_CHECKING

from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.node_editor.ui import NodeEditorPanel

if TYPE_CHECKING:
    from knx_gui.types import Device

NAVIGATE_TO_NODE_DURATION = 0.3


class NodeEditorPlugin:
    name = "node_editor"

    def __init__(
        self,
        api: PluginAPI,
        on_param_change: Callable[["Device", str, str], None] | None = None,
    ) -> None:
        self._api = api
        self._external_on_param_change = on_param_change

        self._panel = NodeEditorPanel(
            state=api.state,
            get_devices=lambda: api.state.devices,
            get_links=lambda: api.state.links,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._handle_param_change,
        )

        api.state.subscribe("device_selected", self._on_device_selected)

    def _add_link(self, start_pin: int, end_pin: int) -> int:
        return self._api.state.add_link(start_pin, end_pin)

    def _remove_link(self, link_id: int) -> None:
        self._api.state.remove_link(link_id)

    def _handle_param_change(self, device: "Device", param_id: str, new_value: str) -> None:
        if self._external_on_param_change:
            self._external_on_param_change(device, param_id, new_value)
        else:
            self._api.state.set_param(device, param_id, new_value)

    def _on_device_selected(self, device: "Device | None") -> None:
        if device:
            self._panel.select_node(device.node_id, False)
            self._panel.navigate_to_selection(False, NAVIGATE_TO_NODE_DURATION)

    @property
    def panel(self) -> NodeEditorPanel:
        return self._panel

    def setup(self) -> None:
        self._panel.setup()

    def shutdown(self) -> None:
        self._panel.shutdown()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
