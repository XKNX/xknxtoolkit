from typing import TYPE_CHECKING

from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.project.ui import ConfigurePanel, DevicesPanel, HistoryPanel

if TYPE_CHECKING:
    from knx_gui.types import Device


class ProjectPlugin:
    name = "project"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api

        self._devices_panel = DevicesPanel(
            get_devices=lambda: api.project.devices,
            on_select_device=self._on_select_device,
        )

        self._configure_panel = ConfigurePanel(
            get_devices=lambda: api.project.devices,
            get_selected_device=lambda: api.project.selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._handle_param_change,
            set_flag=self._handle_flag_change,
        )

        self._history_panel = HistoryPanel(
            get_entries=self._get_history_entries,
            get_cursor=lambda: api.project.cursor,
            on_jump_to=self._handle_jump_to,
        )

        api.events.subscribe("flag_changed", self._on_flag_changed)
        api.events.subscribe("param_changed", self._on_param_changed)
        api.events.subscribe("link_added", self._on_link_added)
        api.events.subscribe("link_removed", self._on_link_removed)

    def _on_select_device(self, device: "Device") -> None:
        self._api.project.selected_device = device

    def _set_selected_device(self, device: "Device") -> None:
        self._api.project.selected_device = device

    def _handle_param_change(self, device: "Device", param_id: str, new_value: str) -> None:
        self._api.project.set_param(device, param_id, new_value)

    def _handle_flag_change(
        self, device: "Device", co_id: str, flag_name: str, new_value: bool
    ) -> None:
        self._api.project.set_flag(device, co_id, flag_name, new_value)

    def _on_param_changed(
        self, device: "Device", param_id: str, old_value: str, new_value: str
    ) -> None:
        self._api.project.set_parameter(device.node_id, param_id, old_value, new_value)

    def _on_flag_changed(
        self, device: "Device", co_id: str, flag_name: str, old_value: bool, new_value: bool
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
        if not self._api.project.session:
            return
        self._api.project.jump_to(event_id)
        self._api.project.session.expire_all()
        self._api.project.request_reload()

    @property
    def devices_panel(self) -> DevicesPanel:
        return self._devices_panel

    @property
    def configure_panel(self) -> ConfigurePanel:
        return self._configure_panel

    @property
    def history_panel(self) -> HistoryPanel:
        return self._history_panel

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
