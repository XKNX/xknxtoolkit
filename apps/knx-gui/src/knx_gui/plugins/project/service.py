"""The GUI project facade, backed by :class:`xknxmono.project.ProjectService`.

Persistence + undo/redo live in the project package (one open project). This adapter keeps the GUI
concerns: the rich in-memory ``Device`` view (resolved ``Application``, com-objects, parameter
visibility), the selection, and the pub/sub. Project state is read live from the service; only the
resolved ``Application`` is cached (the expensive part), and the device view is rebuilt lazily when
a version counter changes — so there is no reload-from-db: every edit (and undo/redo) just bumps the
version, and the next read rebuilds.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from knx_gui.plugins.project.ui.history import HistoryEntry
from knx_gui.types import Device
from xknxmono.product import Application
from xknxmono.project import ProjectService as _ProjectService

if TYPE_CHECKING:
    from knx_gui.plugins.base import Logger
    from knx_gui.plugins.catalog.service import CatalogService

_INSTALLATION = 0

# GUI flag name -> project ComObject column
_FLAG_COLUMNS: dict[str, str] = {
    "communication": "communication_flag",
    "read": "read_flag",
    "write": "write_flag",
    "transmit": "transmit_flag",
    "update": "update_flag",
    "read_on_init": "read_on_init_flag",
}


def _history_label(event_type: str, data: dict[str, Any]) -> str:
    """Render a command's history label (presentation lives in the GUI, not the project package)."""
    if event_type == "AddDevice":
        return f"Add device {data.get('name', '')!r}"
    if event_type == "SetParameter":
        return f"Set {data.get('ref_id', '')} = {data.get('value', '')!r}"
    if event_type == "CreateArea":
        return f"Create area {data.get('address')}"
    if event_type == "CreateLine":
        return f"Create line {data.get('address')}"
    if event_type == "CreateSegment":
        return "Add segment"
    if event_type == "CreateGroupAddress":
        return f"Create group address {data.get('address')}"
    if event_type == "LinkComObject":
        return "Link com-object"
    if event_type == "UnlinkComObject":
        return "Unlink com-object"
    if event_type == "RenameArea":
        return f"Rename area to {data.get('name', '')!r}"
    if event_type == "RenameLine":
        return f"Rename line to {data.get('name', '')!r}"
    if event_type == "SetDeviceName":
        return f"Rename device to {data.get('name', '')!r}"
    if event_type == "MoveDevice":
        return "Move device"
    if event_type == "SetComObjectFlag":
        return "Set flag"
    if event_type == "SetComObjectSending":
        return "Set sending"
    if event_type == "SetGroupAddressDatapointType":
        return "Set datapoint type"
    if event_type.startswith("Remove"):
        return f"Remove {event_type[len('Remove') :].lower()}"
    if event_type == "AddInstallation":
        return "Add installation"
    return event_type


@dataclass
class _Area:
    id: int
    area_number: int
    name: str


@dataclass
class _Line:
    id: int
    area_id: int
    line_number: int
    name: str


@dataclass
class _GroupAddress:
    id: int
    address: str
    name: str


@dataclass
class _Assignment:
    id: int
    com_object_id: int
    group_address_id: int
    is_sending: bool


class ProjectService:
    def __init__(self, catalog: "CatalogService") -> None:
        self._catalog = catalog
        self._svc = _ProjectService()
        self._pid: str | None = None
        self._path: Path | None = None
        self._log: Logger
        self._listeners: dict[str, list[Callable[..., Any]]] = {}
        self._app_cache: dict[str, Application] = {}
        self._program_to_app: dict[str, str] | None = None
        self._devices_cache: list[Device] | None = None
        self._cache_version: int = -1
        self._version: int = 0
        self._selected_node_id: int | None = None

    def set_logger(self, log: "Logger") -> None:
        self._log = log

    # --- pub/sub ----------------------------------------------------------

    def subscribe(self, event: str, handler: Callable[..., Any]) -> Callable[[], None]:
        self._listeners.setdefault(event, []).append(handler)
        return lambda: self._listeners[event].remove(handler)

    def _emit(self, event: str, *args: Any) -> None:
        for handler in list(self._listeners.get(event, [])):
            handler(*args)

    # --- lifecycle --------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self._pid is not None

    @property
    def path(self) -> Path | None:
        return self._path

    def new(self, path: Path) -> None:
        if self._pid is not None:
            self.close()
        if not path.suffix:
            path = path.with_suffix(".xknx")
        self._pid = self._svc.create(path)
        self._path = path
        self._reset()
        self._log.info("project created", path=str(path))

    def open(self, path: Path) -> None:
        if self._pid is not None:
            self.close()
        self._pid = self._svc.open(path)
        self._path = path
        self._reset()
        self._log.info("project opened", path=str(path), devices=len(self.devices))

    def close(self) -> None:
        if self._pid is not None:
            self._svc.close(self._pid)
            self._pid = None
            self._path = None
            self._reset()
            self._log.info("project closed")

    def _reset(self) -> None:
        self._devices_cache = None
        self._cache_version = -1
        self._version = 0
        self._selected_node_id = None
        self._app_cache.clear()
        self._program_to_app = None

    def _bump(self) -> None:
        self._version += 1

    # --- application resolution + device view -----------------------------

    def _resolve_app(self, program_ref: str | None) -> Application | None:
        if program_ref is None:
            return None
        cached = self._app_cache.get(program_ref)
        if cached is not None:
            return cached
        if self._program_to_app is None:
            self._program_to_app = {
                p.hardware2program_ref_id: p.application_id
                for p in self._catalog.get_products()
                if p.application_id is not None
            }
        app_id = self._program_to_app.get(program_ref)
        app = self._catalog.get_application(app_id) if app_id else None
        if app is not None:
            self._app_cache[program_ref] = app
        return app

    def _build_device(self, row: Any) -> Device | None:
        app = self._resolve_app(row.hardware2program_ref_id)
        if app is None:
            self._log.warning(
                "skipping device: application not found",
                device_id=row.id,
                program=row.hardware2program_ref_id,
            )
            return None
        assert self._pid is not None
        ia = self._svc.individual_address(self._pid, row.id) or ""
        device = Device(node_id=row.id, name=row.name, app=app, individual_address=ia)
        for param in row.parameters:
            device.set_param_value(param.ref_id, param.value)
        for co_row in row.com_objects:
            co = device.find_com_object(co_row.ref_id)
            if co is None:
                continue
            co.db_id = co_row.id
            for attr, column in _FLAG_COLUMNS.items():
                value = getattr(co_row, column)
                if value is not None:
                    setattr(co.flags, attr, value)
        return device

    @property
    def devices(self) -> list[Device]:
        if self._devices_cache is None or self._cache_version != self._version:
            devices: list[Device] = []
            if self._pid is not None:
                for row in self._svc.devices(self._pid):
                    device = self._build_device(row)
                    if device is not None:
                        devices.append(device)
            self._devices_cache = devices
            self._cache_version = self._version
        return self._devices_cache

    def find_device_by_node_id(self, node_id: int) -> Device | None:
        return next((d for d in self.devices if d.node_id == node_id), None)

    def find_device_by_address(self, address: str) -> Device | None:
        return next((d for d in self.devices if d.individual_address == address), None)

    @property
    def selected_device(self) -> Device | None:
        if self._selected_node_id is None:
            return None
        return self.find_device_by_node_id(self._selected_node_id)

    @selected_device.setter
    def selected_device(self, device: Device | None) -> None:
        new_id = device.node_id if device is not None else None
        if new_id != self._selected_node_id:
            self._selected_node_id = new_id
            self._emit("device_selected", device)

    # --- topology reads ---------------------------------------------------

    def _installation(self) -> Any:
        assert self._pid is not None
        return self._svc.topology(self._pid, _INSTALLATION)

    def get_areas(self) -> list[_Area]:
        if self._pid is None:
            return []
        return [
            _Area(id=a.id, area_number=a.address, name=a.name)
            for a in self._installation().areas
        ]

    def get_lines(self, area_id: int) -> list[_Line]:
        if self._pid is None:
            return []
        for area in self._installation().areas:
            if area.id == area_id:
                return [
                    _Line(
                        id=ln.id,
                        area_id=ln.area_id,
                        line_number=ln.address,
                        name=ln.name,
                    )
                    for ln in area.lines
                ]
        return []

    # --- group address reads ----------------------------------------------

    @property
    def group_addresses(self) -> list[_GroupAddress]:
        if self._pid is None:
            return []
        return [
            _GroupAddress(id=g.id, address=g.text, name=g.name)
            for g in self._svc.group_addresses(self._pid)
        ]

    def get_group_address(self, ga_id: int) -> _GroupAddress | None:
        if self._pid is None:
            return None
        try:
            g = self._svc.group_address(self._pid, ga_id)
        except KeyError:
            return None
        return _GroupAddress(id=g.id, address=g.text, name=g.name)

    def get_assignments_for_ga(self, ga_id: int) -> list[_Assignment]:
        if self._pid is None:
            return []
        return [
            _Assignment(
                id=link.id,
                com_object_id=link.com_object_id,
                group_address_id=link.group_address_id,
                is_sending=link.is_sending,
            )
            for link in self._svc.group_address_links(self._pid, ga_id)
        ]

    # --- device edits -----------------------------------------------------

    def add_device(
        self,
        product_ref_id: str,
        hardware2program_ref_id: str | None,
        name: str,
        app: Application,
    ) -> int | None:
        if self._pid is None:
            return None
        segment_id = self._installation().areas[0].lines[0].segments[0].id
        params = [(p.id, p.value) for p in app.parameters()]
        com_objects = [(co.id, None) for co in app.com_objects()]
        device_id = self._svc.add_device(
            self._pid,
            segment_id,
            product_ref_id,
            name=name,
            hardware2program_ref_id=hardware2program_ref_id,
            parameters=params,
            com_objects=com_objects,
        )
        if hardware2program_ref_id is not None:
            self._app_cache[hardware2program_ref_id] = app
        self._bump()
        return device_id

    def set_param(self, device: Device, param_id: str, value: str) -> None:
        if self._pid is None:
            return
        self._svc.set_parameter(self._pid, device.node_id, param_id, value)
        # Reflect the change on the live device object instead of bumping the cache: a rebuild would
        # recreate every Device and reset the Configure panel's tree/edit state. A parameter edit
        # doesn't change device identity or topology, so the in-place update is sufficient (undo/redo
        # still bump and rebuild). This keeps the param's name-placeholder resolution current too.
        device.set_param_value(param_id, value)

    def set_device_name(self, node_id: int, old_name: str, new_name: str) -> None:
        if self._pid is None or old_name == new_name:
            return
        self._svc.set_device_name(self._pid, node_id, new_name)
        self._bump()

    def set_device_individual_address(
        self, node_id: int, old_address: str, new_address: str
    ) -> None:
        if self._pid is None or old_address == new_address:
            return
        try:
            self._svc.set_individual_address(self._pid, node_id, new_address)
        except (KeyError, ValueError) as e:
            self._log.warning(
                "could not set individual address", address=new_address, error=str(e)
            )
            return
        self._bump()

    def set_flag(self, device: Device, co_id: str, flag_name: str, value: bool) -> None:
        if self._pid is None:
            return
        co = device.find_com_object(co_id)
        column = _FLAG_COLUMNS.get(flag_name)
        if co is None or co.db_id is None or column is None:
            return
        self._svc.set_com_object_flag(self._pid, co.db_id, column, value)
        self._bump()

    # --- topology edits ---------------------------------------------------

    def create_area(self, area_number: int, name: str = "") -> int | None:
        if self._pid is None:
            return None
        area_id = self._svc.create_area(self._pid, _INSTALLATION, area_number, name)
        self._bump()
        return area_id

    def remove_area(self, area_id: int, area_number: int = 0, name: str = "") -> None:
        if self._pid is None:
            return
        self._svc.remove_area(self._pid, area_id)
        self._bump()

    def rename_area(self, area_id: int, old_name: str, new_name: str) -> None:
        if self._pid is None or old_name == new_name:
            return
        self._svc.rename_area(self._pid, area_id, new_name)
        self._bump()

    def create_line(self, area_id: int, line_number: int, name: str = "") -> int | None:
        if self._pid is None:
            return None
        line_id = self._svc.create_line(self._pid, area_id, line_number, name)
        self._bump()
        return line_id

    def remove_line(
        self, line_id: int, area_id: int = 0, line_number: int = 0, name: str = ""
    ) -> None:
        if self._pid is None:
            return
        self._svc.remove_line(self._pid, line_id)
        self._bump()

    def rename_line(self, line_id: int, old_name: str, new_name: str) -> None:
        if self._pid is None or old_name == new_name:
            return
        self._svc.rename_line(self._pid, line_id, new_name)
        self._bump()

    # --- group address edits ----------------------------------------------

    def create_group_address(
        self, address: str | None = None, name: str = ""
    ) -> int | None:
        if self._pid is None:
            return None
        value = self._svc.next_free_group_address(self._pid, _INSTALLATION)
        ga_id = self._svc.create_group_address(self._pid, _INSTALLATION, value, name)
        self._bump()
        return ga_id

    def remove_group_address(
        self, ga_id: int, address: str = "", name: str = ""
    ) -> None:
        if self._pid is None:
            return
        self._svc.remove_group_address(self._pid, ga_id)
        self._bump()

    def link_com_object_to_ga(
        self, com_object_id: int, group_address_id: int, is_sending: bool = False
    ) -> int | None:
        if self._pid is None:
            return None
        link_id = self._svc.link_com_object(
            self._pid, com_object_id, group_address_id, sending=is_sending
        )
        self._bump()
        return link_id

    def unlink_com_object_from_ga(
        self,
        assignment_id: int,
        com_object_id: int = 0,
        group_address_id: int = 0,
        is_sending: bool = False,
    ) -> None:
        if self._pid is None:
            return
        self._svc.unlink_com_object(self._pid, assignment_id)
        self._bump()

    # --- undo / redo / history --------------------------------------------

    def undo(self) -> bool:
        if self._pid is None:
            return False
        result = self._svc.undo(self._pid)
        if result:
            self._bump()
        return result

    def redo(self) -> bool:
        if self._pid is None:
            return False
        result = self._svc.redo(self._pid)
        if result:
            self._bump()
        return result

    def can_undo(self) -> bool:
        return self._pid is not None and self._svc.can_undo(self._pid)

    def can_redo(self) -> bool:
        return self._pid is not None and self._svc.can_redo(self._pid)

    @property
    def cursor(self) -> int:
        return self._svc.cursor(self._pid) if self._pid is not None else 0

    def jump_to(self, event_id: int) -> None:
        if self._pid is None:
            return
        self._svc.jump_to(self._pid, event_id)
        self._bump()

    def history(self) -> list[HistoryEntry]:
        if self._pid is None:
            return []
        return [
            HistoryEntry(
                id=entry.id,
                display_text=_history_label(entry.event_type, entry.data),
                reverted=entry.reverted,
            )
            for entry in self._svc.history(self._pid)
        ]
