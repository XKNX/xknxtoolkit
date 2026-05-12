from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from knx_gui.dpt import lookup_or_make_dpt
from knx_gui.knxprod import DeviceApplication, parse_application_xml
from knx_gui.plugins.project.db import (
    ComObjectDptChanged,
    ComObjectFlagChanged,
    ComObjectModel,
    DeviceAdded,
    DeviceAddressChanged,
    DeviceModel,
    DeviceRemoved,
    LinkCreated,
    LinkModel,
    LinkRemoved,
    ParameterChanged,
    ParameterModel,
    ProjectDatabase,
)
from knx_gui.types import ComObject, Device

if TYPE_CHECKING:
    from knx_gui.plugins.catalog.service import CatalogService


class ProjectService:
    def __init__(self, catalog: "CatalogService") -> None:
        self._catalog = catalog
        self._db: ProjectDatabase | None = None
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

        self._devices: list[Device] = []
        self._links: list[tuple[int, int, int]] = []
        self._selected_device: Device | None = None
        self._next_link_id: int = 1000
        self._next_device_id: int = 10

    def subscribe(self, event: str, handler: Callable[..., Any]) -> Callable[[], None]:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)
        return lambda: self._listeners[event].remove(handler)

    def _emit(self, event: str, *args: Any) -> None:
        for handler in self._listeners.get(event, []):
            handler(*args)

    @property
    def devices(self) -> list[Device]:
        return self._devices

    @property
    def links(self) -> list[tuple[int, int, int]]:
        return self._links

    @property
    def selected_device(self) -> Device | None:
        return self._selected_device

    @selected_device.setter
    def selected_device(self, device: Device | None) -> None:
        if self._selected_device != device:
            self._selected_device = device
            self._emit("device_selected", device)

    def add_device_to_state(self, app: "DeviceApplication", address: str = "") -> Device:
        device = Device(
            node_id=self._next_device_id,
            name=app.name,
            app=app,
            address=address,
        )
        self._next_device_id += 1
        self._devices.append(device)
        return device

    def add_device_to_state_with_id(
        self, app: "DeviceApplication", node_id: int, address: str = ""
    ) -> Device:
        device = Device(
            node_id=node_id,
            name=app.name,
            app=app,
            address=address,
        )
        self._devices.append(device)
        return device

    def clear_devices(self) -> None:
        self._devices.clear()
        self._selected_device = None

    def add_link_to_state(self, start_pin: int, end_pin: int) -> int:
        link_id = self._next_link_id
        self._next_link_id += 1
        self._links.append((link_id, start_pin, end_pin))
        self._emit("link_added", link_id, start_pin, end_pin)
        return link_id

    def remove_link_from_state(self, link_id: int) -> None:
        link_data = next((link for link in self._links if link[0] == link_id), None)
        self._links = [link for link in self._links if link[0] != link_id]
        if link_data:
            self._emit("link_removed", link_data[0], link_data[1], link_data[2])

    def clear_links(self) -> None:
        self._links.clear()

    def find_device_by_address(self, address: str) -> Device | None:
        for device in self._devices:
            if device.address == address:
                return device
        return None

    def find_device_by_node_id(self, node_id: int) -> Device | None:
        for device in self._devices:
            if device.node_id == node_id:
                return device
        return None

    def set_flag(self, device: Device, co_id: str, flag_name: str, new_value: bool) -> None:
        com_object = device.find_com_object(co_id)
        if not com_object:
            return
        old_value = getattr(com_object.flags, flag_name)
        if old_value != new_value:
            setattr(com_object.flags, flag_name, new_value)
            self._emit("flag_changed", device, co_id, flag_name, old_value, new_value)

    def set_param(self, device: Device, param_id: str, new_value: str) -> None:
        old_value = device._param_values.get(param_id, "")
        if old_value != new_value:
            device.set_param_value(param_id, new_value)
            self._emit("param_changed", device, param_id, old_value, new_value)

    def check_param_change_hides_com_objects(
        self, device: Device, param_id: str, value: str
    ) -> list[ComObject]:
        return device.would_hide_com_objects(param_id, value)

    def _reload_from_db(self) -> None:
        if not self._db:
            return
        self._load_devices_from_db()
        self._load_links_from_db()

    def _load_links_from_db(self) -> None:
        if not self._db:
            return
        self.clear_links()
        for link_model in self._db.session.query(LinkModel).all():
            self._links.append(
                (link_model.id, link_model.start_pin, link_model.end_pin)
            )
        max_link_id = max((link[0] for link in self._links), default=999)
        self._next_link_id = max_link_id + 1

    def _load_devices_from_db(self) -> None:
        if not self._db:
            return
        from knx_gui.plugins.catalog.db import ApplicationModel

        selected_node_id = (
            self._selected_device.node_id if self._selected_device else None
        )
        self.clear_devices()
        for device_model in self._db.session.query(DeviceModel).all():
            app = self._get_app_for_template(device_model.template_id)
            if not app:
                print(
                    f"[project] skipping device {device_model.id}: "
                    f"template '{device_model.template_id}' not found"
                )
                continue
            device = self.add_device_to_state_with_id(
                app=app,
                node_id=device_model.id,
                address=device_model.address or "",
            )
            for param_model in (
                self._db.session.query(ParameterModel)
                .filter_by(device_id=device_model.id)
                .all()
            ):
                device.set_param_value(param_model.param_id, param_model.value)
            for co_model in (
                self._db.session.query(ComObjectModel)
                .filter_by(device_id=device_model.id)
                .all()
            ):
                co = device.find_com_object(co_model.co_id)
                if co:
                    co.dpt = lookup_or_make_dpt(
                        f"{co_model.dpt_major}.{co_model.dpt_minor}"
                    )
                    co.flags.communication = co_model.flag_communication
                    co.flags.read = co_model.flag_read
                    co.flags.write = co_model.flag_write
                    co.flags.transmit = co_model.flag_transmit
                    co.flags.update = co_model.flag_update
        if selected_node_id is not None:
            self._selected_device = self.find_device_by_node_id(selected_node_id)

    def _get_app_for_template(self, template_id: str) -> DeviceApplication | None:
        from knx_gui.plugins.catalog.db import ApplicationModel

        xml_data = self._catalog.get_application_xml(template_id)
        if not xml_data:
            return None
        app_model = (
            self._catalog.session.query(ApplicationModel)
            .filter_by(application_id=template_id)
            .first()
        )
        if not app_model:
            return None
        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            return None
        return apps[0]

    @property
    def is_open(self) -> bool:
        return self._db is not None

    @property
    def path(self) -> Path | None:
        return self._db.path if self._db else None

    @property
    def session(self):
        if not self._db:
            return None
        return self._db.session

    def new(self, path: Path) -> None:
        if self._db:
            self._db.close()
        if not path.suffix:
            path = path.with_suffix(".xknx")
        self._db = ProjectDatabase(path)
        self._db.create()

    def open(self, path: Path) -> None:
        if self._db:
            self._db.close()
        self._db = ProjectDatabase(path)
        self._db.open()
        self._reload_from_db()

    def close(self) -> None:
        if self._db:
            self._db.close()
            self._db = None

    def add_device(
        self,
        template_id: str,
        name: str,
        app: "DeviceApplication",
        address: str = "",
    ) -> int | None:
        if not self._db:
            return None

        params = [(p.id, p.value) for p in app.parameters]
        com_objs = []
        for co in app.com_objects:
            dpt_major, dpt_minor = 0, 0
            if co.dpt_codes:
                parts = co.dpt_codes[0].split(".")
                dpt_major = int(parts[0]) if len(parts) > 0 else 0
                dpt_minor = int(parts[1]) if len(parts) > 1 else 0
            com_objs.append(
                {
                    "co_id": co.id,
                    "dpt_major": dpt_major,
                    "dpt_minor": dpt_minor,
                    "flag_communication": co.flags.communication,
                    "flag_read": co.flags.read,
                    "flag_write": co.flags.write,
                    "flag_transmit": co.flags.transmit,
                    "flag_update": co.flags.update,
                }
            )

        event = DeviceAdded(
            device_id=0,
            address=address,
            template_id=template_id,
            name=name,
            parameters=params,
            com_objects=com_objs,
        )
        self._db.event_store.append(event)
        return event.device_id

    def remove_device(self, device_id: int, template_id: str, address: str) -> None:
        if not self._db:
            return
        event = DeviceRemoved(
            device_id=device_id,
            template_id=template_id,
            address=address,
        )
        self._db.event_store.append(event)

    def set_device_address(
        self, device_id: int, old_address: str, new_address: str
    ) -> None:
        if not self._db:
            return
        event = DeviceAddressChanged(
            device_id=device_id,
            old_address=old_address,
            new_address=new_address,
        )
        self._db.event_store.append(event)

    def set_parameter(
        self, device_id: int, param_id: str, old_value: str, new_value: str
    ) -> None:
        if not self._db:
            return
        event = ParameterChanged(
            device_id=device_id,
            param_id=param_id,
            old_value=old_value,
            new_value=new_value,
        )
        self._db.event_store.append(event)

    def set_com_object_dpt(
        self,
        device_id: int,
        co_id: str,
        old_major: int,
        old_minor: int,
        new_major: int,
        new_minor: int,
    ) -> None:
        if not self._db:
            return
        event = ComObjectDptChanged(
            device_id=device_id,
            co_id=co_id,
            old_dpt_major=old_major,
            old_dpt_minor=old_minor,
            new_dpt_major=new_major,
            new_dpt_minor=new_minor,
        )
        self._db.event_store.append(event)

    def set_com_object_flag(
        self,
        device_id: int,
        co_id: str,
        flag_name: str,
        old_value: bool,
        new_value: bool,
    ) -> None:
        if not self._db:
            return
        event = ComObjectFlagChanged(
            device_id=device_id,
            co_id=co_id,
            flag_name=flag_name,
            old_value=old_value,
            new_value=new_value,
        )
        self._db.event_store.append(event)

    def add_link(self, link_id: int, start_pin: int, end_pin: int) -> None:
        if not self._db:
            return
        event = LinkCreated(link_id=link_id, start_pin=start_pin, end_pin=end_pin)
        self._db.event_store.append(event)

    def remove_link(self, link_id: int, start_pin: int, end_pin: int) -> None:
        if not self._db:
            return
        event = LinkRemoved(link_id=link_id, start_pin=start_pin, end_pin=end_pin)
        self._db.event_store.append(event)

    def undo(self) -> bool:
        if not self._db:
            return False
        result = self._db.event_store.undo()
        if result:
            self._db.session.expire_all()
            self._reload_from_db()
        return result

    def redo(self) -> bool:
        if not self._db:
            return False
        result = self._db.event_store.redo()
        if result:
            self._db.session.expire_all()
            self._reload_from_db()
        return result

    def can_undo(self) -> bool:
        if not self._db:
            return False
        return self._db.event_store.can_undo()

    def can_redo(self) -> bool:
        if not self._db:
            return False
        return self._db.event_store.can_redo()

    @property
    def cursor(self) -> int:
        if not self._db:
            return 0
        return self._db.event_store.cursor

    def jump_to(self, event_id: int) -> None:
        if not self._db:
            return
        self._db.event_store.jump_to(event_id)
        self._db.session.expire_all()
        self._reload_from_db()
