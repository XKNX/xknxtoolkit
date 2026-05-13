from collections.abc import Callable
from typing import TYPE_CHECKING

from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.plugins.project.ui import ConfigurePanel, DevicesPanel, HistoryPanel
from knx_gui.strings import S

if TYPE_CHECKING:
    from knx_gui.types import Device


class ProjectPlugin:
    name = "project"

    def __init__(
        self,
        api: PluginAPI,
        get_selected_node_ids: Callable[[], list[int]] | None = None,
    ) -> None:
        self._api = api
        self._get_selected_node_ids = get_selected_node_ids

        self._devices_panel = DevicesPanel(
            get_devices=lambda: api.project.devices,
            on_select_device=self._on_select_device,
        )

        self._configure_panel = ConfigurePanel(
            get_devices=lambda: api.project.devices,
            get_selected_device=lambda: api.project.selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._handle_param_change,
            on_individual_address_change=self._handle_individual_address_change,
            on_name_change=self._handle_name_change,
            set_flag=self._handle_flag_change,
        )

        self._history_panel = HistoryPanel(
            get_entries=self._get_history_entries,
            get_cursor=lambda: api.project.cursor,
            on_jump_to=self._handle_jump_to,
        )

        self._panels = [
            PanelDefinition(
                name="devices",
                label=S.PANEL_DEVICES,
                dock="LeftSpace",
                render=self._devices_panel.render,
            ),
            PanelDefinition(
                name="configure",
                label=S.PANEL_CONFIGURE,
                dock="RightSpace",
                render=self._render_configure,
            ),
            PanelDefinition(
                name="history",
                label=S.PANEL_HISTORY,
                dock="RightSpace",
                render=self._history_panel.render,
            ),
        ]

        api.project.subscribe("flag_changed", self._on_flag_changed)
        api.project.subscribe("param_changed", self._on_param_changed)
        api.project.subscribe("link_added", self._on_link_added)
        api.project.subscribe("link_removed", self._on_link_removed)

    def _on_select_device(self, device: "Device") -> None:
        self._api.project.selected_device = device

    def _set_selected_device(self, device: "Device") -> None:
        self._api.project.selected_device = device

    def _handle_param_change(
        self, device: "Device", param_id: str, new_value: str
    ) -> None:
        self._api.project.set_param(device, param_id, new_value)

    def _handle_individual_address_change(
        self, device: "Device", new_address: str
    ) -> None:
        old_address = device.individual_address
        if old_address != new_address:
            device.individual_address = new_address
            self._api.project.set_device_individual_address(
                device.node_id, old_address, new_address
            )

    def _handle_name_change(self, device: "Device", new_name: str) -> None:
        old_name = device.name
        if old_name != new_name:
            device.name = new_name
            self._api.project.set_device_name(device.node_id, old_name, new_name)

    def _handle_flag_change(
        self, device: "Device", co_id: str, flag_name: str, new_value: bool
    ) -> None:
        self._api.project.set_flag(device, co_id, flag_name, new_value)

    def _on_param_changed(
        self, device: "Device", param_id: str, old_value: str, new_value: str
    ) -> None:
        self._api.project.set_parameter(device.node_id, param_id, old_value, new_value)

    def _on_flag_changed(
        self,
        device: "Device",
        co_id: str,
        flag_name: str,
        old_value: bool,
        new_value: bool,
    ) -> None:
        self._api.project.set_com_object_flag(
            device.node_id, co_id, flag_name, old_value, new_value
        )

    def _on_link_added(self, link_id: int, start_pin: int, end_pin: int) -> None:
        self._api.project.add_link(link_id, start_pin, end_pin)

    def _on_link_removed(self, link_id: int, start_pin: int, end_pin: int) -> None:
        self._api.project.remove_link(link_id, start_pin, end_pin)

    def _get_history_entries(self):
        from knx_gui.plugins.project.db import EventModel
        from knx_gui.plugins.project.db.events import deserialize_event
        from knx_gui.plugins.project.ui import HistoryEntry

        if not self._api.project.session:
            return []

        entries = []
        for event_model in (
            self._api.project.session.query(EventModel)
            .order_by(EventModel.id.desc())
            .all()
        ):
            event = deserialize_event(event_model.type, event_model.data)
            entries.append(
                HistoryEntry(
                    id=event_model.id,
                    display_text=event.display_text(),
                    reverted=event_model.reverted,
                )
            )
        return entries

    def _handle_jump_to(self, event_id: int) -> None:
        self._api.project.jump_to(event_id)

    def _render_configure(self) -> None:
        self._sync_selected_device_from_editor()
        self._configure_panel.render()

    def _sync_selected_device_from_editor(self) -> None:
        if not self._get_selected_node_ids:
            return
        selected_ids = self._get_selected_node_ids()
        if len(selected_ids) != 1:
            return
        node_id = selected_ids[0]
        if (
            self._api.project.selected_device
            and self._api.project.selected_device.node_id == node_id
        ):
            return
        device = self._api.project.find_device_by_node_id(node_id)
        if device:
            self._api.project.selected_device = device

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
