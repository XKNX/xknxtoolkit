import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from knx_gui.plugins.base import Logger, PanelDefinition, PluginAPI
from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui import (
    ConfigurePanel,
    DevicesPanel,
    GroupAddressesPanel,
    HistoryPanel,
    ProjectInfoPanel,
    SpacesPanel,
)
from knx_gui.plugins.project.ui.devices import Area, Line
from knx_gui.plugins.project.ui.memory_preview import MemoryPreviewWindow
from knx_gui.plugins.project.ui.preflight_result import PreflightResultWindow

if TYPE_CHECKING:
    from concurrent.futures import Future

    from knx_gui.device import Device
    from xknxmono.download.image import GroupCommunication
    from xknxmono.download.scope import DownloadScope


def _parse_individual_address(text: str) -> int | None:
    """Parse ``area.line.device`` into a raw 16-bit individual address."""
    parts = text.split(".")
    if len(parts) != 3:
        return None
    try:
        area, line, device = (int(p) for p in parts)
    except ValueError:
        return None
    if not (0 <= area <= 0xF and 0 <= line <= 0xF and 0 <= device <= 0xFF):
        return None
    return (area << 12) | (line << 8) | device


def _parse_group_address(text: str) -> int | None:
    """Parse a 3-level (``a/b/c``), 2-level (``a/b``) or free group address."""
    parts = text.split("/")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 3:
        return (nums[0] << 11) | (nums[1] << 8) | nums[2]
    if len(nums) == 2:
        return (nums[0] << 11) | nums[1]
    if len(nums) == 1:
        return nums[0]
    return None


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

        self._memory_preview = MemoryPreviewWindow(
            get_devices=lambda: api.project.devices
        )
        self._preflight_result = PreflightResultWindow()

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
            get_links_for_com_object=self._links_for_com_object,
            get_all_group_addresses=self._all_group_addresses,
            on_link_com_object=self._link_com_object,
            on_unlink_com_object=api.project.unlink_com_object_from_ga,
            get_device_info=api.project.get_device_info,
            on_program_device=self._program_device,
            on_eval_device=self._eval_device,
            open_memory_preview=self._memory_preview.open,
        )

        self._group_addresses_panel = GroupAddressesPanel(
            get_range_tree=api.project.get_group_range_tree,
            get_assignments_for_ga=api.project.get_assignments_for_ga,
            get_devices=lambda: api.project.devices,
            on_create_ga=self._on_create_ga,
            on_rename_ga=api.project.rename_group_address,
            on_set_ga_dpt=api.project.set_group_address_dpt,
            on_remove_ga=api.project.remove_group_address,
        )

        self._spaces_panel = SpacesPanel(
            get_space_tree=api.project.get_space_tree,
            on_select_device_id=self._select_device_by_id,
        )

        self._project_info_panel = ProjectInfoPanel(
            get_project_info=api.project.get_project_metadata,
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
                name="buildings",
                label=S.PANEL_BUILDINGS,
                dock="LeftSpace",
                render=self._spaces_panel.render,
            ),
            PanelDefinition(
                name="group_addresses",
                label=S.PANEL_GROUP_ADDRESSES,
                dock="LeftSpace",
                render=self._group_addresses_panel.render,
            ),
            PanelDefinition(
                name="editor",
                label=S.PANEL_EDITOR,
                dock="MainDockSpace",
                render=self._render_configure,
            ),
            PanelDefinition(
                name="history",
                label=S.PANEL_HISTORY,
                dock="RightSpace",
                render=self._history_panel.render,
            ),
            PanelDefinition(
                name="project_info",
                label=S.PANEL_PROJECT_INFO,
                dock="RightSpace",
                render=self._project_info_panel.render,
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

    def _select_device_by_id(self, node_id: int) -> None:
        device = self._api.project.find_device_by_node_id(node_id)
        if device is not None:
            self._api.project.selected_device = device

    def _on_create_ga(self, address: str, name: str) -> None:
        self._api.project.create_group_address(address, name)

    def _links_for_com_object(
        self, com_object_db_id: int
    ) -> list[tuple[int, int, str, bool]]:
        result: list[tuple[int, int, str, bool]] = []
        for link in self._api.project.get_links_for_com_object(com_object_db_id):
            ga = self._api.project.get_group_address(link.group_address_id)
            if ga is not None:
                result.append(
                    (link.id, link.group_address_id, ga.address, link.is_sending)
                )
        return result

    def _all_group_addresses(self) -> list[tuple[int, str]]:
        return [(g.id, g.address) for g in self._api.project.group_addresses]

    def _link_com_object(self, com_object_db_id: int, group_address_id: int) -> None:
        # The first group address a com-object links to becomes its sending address (like ETS).
        existing = self._api.project.get_links_for_com_object(com_object_db_id)
        self._api.project.link_com_object_to_ga(
            com_object_db_id, group_address_id, is_sending=not existing
        )

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

    def _program_device(self, device: "Device", scope: "DownloadScope") -> None:
        self._api.connection.program_device(
            device, scope, self._group_communication_for(device)
        )

    def _eval_device(self, device: "Device", scope: "DownloadScope") -> None:
        label = device.name or device.individual_address or "device"
        # The test reads the live device, so it needs a bus connection; without one
        # there is nothing to compare against.
        if self._api.connection.xknx is None:
            self._preflight_result.submit_error(
                label, scope.name, S.PREFLIGHT_NO_CONNECTION
            )
            return
        # The test validates our image generation against the device's programmed state, which
        # matches the project only as long as it is unedited (import produces a zero-event project).
        # Any edit would make a diff ambiguous, so refuse the test once the project was changed.
        if self._api.project.history():
            self._preflight_result.submit_error(
                label, scope.name, S.PREFLIGHT_PROJECT_MODIFIED
            )
            return
        runtime = self._runtime_managed_addresses(device)
        future = self._api.connection.evaluate_device(
            device, scope, self._group_communication_for(device)
        )
        if future is not None:
            future.add_done_callback(
                functools.partial(self._on_eval_done, label, scope.name, runtime)
            )

    @staticmethod
    def _runtime_managed_addresses(device: "Device") -> set[int]:
        """Best-effort set of device-managed (runtime) memory addresses; empty on error."""
        from knx_gui.programming import runtime_managed_addresses

        try:
            return runtime_managed_addresses(device)
        except Exception:
            return set()

    def _on_eval_done(
        self, label: str, scope_name: str, runtime: set[int], future: "Future[Any]"
    ) -> None:
        """Runs on the async loop thread; only hands the result to the (thread-safe) window."""
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._preflight_result.submit_error(
                label, scope_name, f"{type(exc).__name__}: {exc}"
            )
            return
        self._preflight_result.submit_result(
            label, scope_name, future.result(), runtime
        )

    def _group_communication_for(self, device: "Device") -> "GroupCommunication | None":
        """Collect the device's group address links into a GroupCommunication."""
        from xknxmono.download import GroupCommunication
        from xknxmono.download.project_data import GroupObjectLink

        device_address = _parse_individual_address(device.individual_address)
        if device_address is None:
            return None
        links: list[GroupObjectLink] = []
        for com_object in device.com_objects:
            if com_object.db_id is None:
                continue
            for assignment in self._api.project.get_links_for_com_object(
                com_object.db_id
            ):
                ga = self._api.project.get_group_address(assignment.group_address_id)
                if ga is None:
                    continue
                address = _parse_group_address(ga.address)
                if address is None:
                    continue
                links.append(
                    GroupObjectLink(
                        com_object_ref_id=com_object.id,
                        group_address=address,
                        sending=assignment.is_sending,
                    )
                )
        return GroupCommunication(device_address=device_address, links=links)

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
        self._preflight_result.render()

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
