from collections.abc import Callable
from typing import TYPE_CHECKING

from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui import ConfigurePanel, DevicesPanel, HistoryPanel
from knx_gui.plugins.project.ui.devices import Area, Line
from knx_gui.plugins.project.ui.memory_preview import MemoryPreviewWindow

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
        api.project.set_logger(Logger(api.log, "project"))

        self._memory_preview = MemoryPreviewWindow(get_devices=lambda: api.project.devices)

        self._devices_panel = DevicesPanel(
            get_devices=lambda: api.project.devices,
            get_areas=self._get_areas,
            get_lines=self._get_lines,
            on_select_device=self._on_select_device,
            on_move_device=self._on_move_device,
            on_create_area=self._on_create_area,
            on_remove_area=self._on_remove_area,
            on_rename_area=self._on_rename_area,
            on_create_line=self._on_create_line,
            on_remove_line=self._on_remove_line,
            on_rename_line=self._on_rename_line,
        )

        self._configure_panel = ConfigurePanel(
            get_devices=lambda: api.project.devices,
            get_selected_device=lambda: api.project.selected_device,
            set_selected_device=self._set_selected_device,
            on_param_change=self._handle_param_change,
            on_individual_address_change=self._handle_individual_address_change,
            on_name_change=self._handle_name_change,
            set_flag=self._handle_flag_change,
            on_program_device=api.connection.assign_individual_address_for_device,
            open_memory_preview=self._memory_preview.open,
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

    def _get_areas(self) -> list[Area]:
        return [
            Area(id=a.id, number=a.area_number, name=a.name)
            for a in self._api.project.get_areas()
        ]

    def _get_lines(self, area_id: int) -> list[Line]:
        return [
            Line(id=ln.id, area_id=ln.area_id, number=ln.line_number, name=ln.name)
            for ln in self._api.project.get_lines(area_id)
        ]

    def _on_select_device(self, device: "Device") -> None:
        self._api.project.selected_device = device

    def _on_create_area(self, area_number: int, name: str) -> None:
        self._api.project.create_area(area_number, name)

    def _on_remove_area(self, area: Area) -> None:
        self._api.project.remove_area(area.id, area.number, area.name)

    def _on_rename_area(self, area: Area, new_name: str) -> None:
        if area.name != new_name:
            self._api.project.rename_area(area.id, area.name, new_name)

    def _on_create_line(self, area_id: int, line_number: int, name: str) -> None:
        self._api.project.create_line(area_id, line_number, name)

    def _on_remove_line(self, line: Line) -> None:
        self._api.project.remove_line(line.id, line.area_id, line.number, line.name)

    def _on_rename_line(self, line: Line, new_name: str) -> None:
        if line.name != new_name:
            self._api.project.rename_line(line.id, line.name, new_name)

    def _on_move_device(
        self, device: "Device", area_number: int, line_number: int
    ) -> None:
        devices = self._api.project.devices
        used_numbers: set[int] = set()
        for d in devices:
            if not d.individual_address:
                continue
            parts = d.individual_address.split(".")
            if len(parts) < 3:
                continue
            try:
                a, ln, dev = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                continue
            if a == area_number and ln == line_number:
                used_numbers.add(dev)

        device_number = 1
        while device_number in used_numbers:
            device_number += 1

        new_address = f"{area_number}.{line_number}.{device_number}"
        self._handle_individual_address_change(device, new_address)

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

    def _get_history_entries(self):
        return self._api.project.history()

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

    def render_overlays(self) -> None:
        self._memory_preview.render()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
