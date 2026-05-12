from pathlib import Path
from typing import TYPE_CHECKING

from knx_gui.plugins.base import EventBus
from knx_gui.plugins.project.db import (
    ComObjectDptChanged,
    ComObjectFlagChanged,
    DeviceAdded,
    DeviceAddressChanged,
    DeviceRemoved,
    LinkCreated,
    LinkRemoved,
    ParameterChanged,
    ProjectDatabase,
)

if TYPE_CHECKING:
    from knx_gui.knxprod import DeviceApplication


class ProjectService:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._db: ProjectDatabase | None = None

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
        self._db = ProjectDatabase(path, self._event_bus)
        self._db.create()

    def open(self, path: Path) -> None:
        if self._db:
            self._db.close()
        self._db = ProjectDatabase(path, self._event_bus)
        self._db.open()

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
        return self._db.event_store.undo()

    def redo(self) -> bool:
        if not self._db:
            return False
        return self._db.event_store.redo()

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
