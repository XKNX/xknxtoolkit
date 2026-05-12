from knx_gui.plugins.base import PluginAPI
from knx_gui.plugins.project.ui import ConfigurePanel, DevicesPanel, HistoryPanel


class ProjectPlugin:
    name = "project"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api

        self._devices_panel = DevicesPanel(
            get_devices=lambda: api.state.devices,
            on_select_device=self._on_select_device,
        )

        self._configure_panel = ConfigurePanel(
            get_devices=lambda: api.state.devices,
            get_selected_device=lambda: api.state.selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._on_param_change,
            on_flag_change=self._on_flag_change,
        )

        self._history_panel = HistoryPanel(
            get_entries=self._get_history_entries,
            get_cursor=lambda: api.project.cursor,
            on_jump_to=self._on_jump_to,
        )

    def _on_select_device(self, device) -> None:
        self._api.state.selected_device = device

    def _set_selected_device(self, device) -> None:
        self._api.state.selected_device = device

    def _on_param_change(self, device, param_id: str, new_value: str) -> None:
        param = device.get_parameter(param_id)
        if param:
            old_value = param.value
            param.value = new_value
            self._api.project.set_parameter(
                device.db_id, param_id, old_value, new_value
            )

    def _on_flag_change(
        self, device, co_id: str, flag_name: str, new_value: bool
    ) -> None:
        co = device.get_com_object(co_id)
        if co:
            old_value = getattr(co.flags, flag_name)
            setattr(co.flags, flag_name, new_value)
            self._api.project.set_com_object_flag(
                device.db_id, co_id, flag_name, old_value, new_value
            )

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

    def _on_jump_to(self, event_id: int) -> None:
        self._api.project.jump_to(event_id)

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
