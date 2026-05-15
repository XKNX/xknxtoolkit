from typing import TYPE_CHECKING

from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.node_editor.strings import S
from knx_gui.plugins.node_editor.ui import NodeEditorPanel

if TYPE_CHECKING:
    from knx_gui.types import Device

NAVIGATE_TO_NODE_DURATION = 0.3


class NodeEditorPlugin:
    name = "node_editor"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._log = Logger(api.log, "node_editor")

        self._panel = NodeEditorPanel(
            get_devices=lambda: api.project.devices,
            get_group_addresses=lambda: api.project.group_addresses,
            get_assignments_for_ga=api.project.get_assignments_for_ga,
            add_link=self._add_link,
            remove_link=self._remove_link,
            on_param_change=self._handle_param_change,
        )

        self._panels = [
            PanelDefinition(
                name="node_editor",
                label=S.PANEL_NODE_EDITOR,
                dock="MainDockSpace",
                render=self._panel.render,
            ),
        ]

        api.project.subscribe("device_selected", self._on_device_selected)

    def _add_link(self, output_co_id: int, input_co_id: int) -> int | None:
        ga_id = self._api.project.create_group_address()
        if ga_id is None:
            return None
        self._api.project.link_com_object_to_ga(output_co_id, ga_id, is_sending=True)
        self._api.project.link_com_object_to_ga(input_co_id, ga_id, is_sending=False)
        self._log.debug("link added", ga_id=ga_id, output=output_co_id, input=input_co_id)
        return ga_id

    def _remove_link(self, ga_id: int) -> None:
        ga = self._api.project.get_group_address(ga_id)
        if not ga:
            return
        assignments = self._api.project.get_assignments_for_ga(ga_id)
        for assignment in assignments:
            self._api.project.unlink_com_object_from_ga(
                assignment.id,
                assignment.com_object_id,
                ga_id,
                assignment.is_sending,
            )
        self._api.project.remove_group_address(ga_id, ga.address, ga.name)
        self._log.debug("link removed", ga_id=ga_id, address=ga.address)

    def _handle_param_change(
        self, device: "Device", param_id: str, new_value: str
    ) -> None:
        self._api.project.set_param(device, param_id, new_value)

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
