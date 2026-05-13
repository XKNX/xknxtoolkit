from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy.orm import Session

from knx_gui.plugins.project.db.models import (
    AreaModel,
    ComObjectModel,
    DeviceModel,
    LineModel,
    LinkModel,
    ParameterModel,
)
from knx_gui.strings import S


@dataclass
class Event(ABC):
    id: int | None = field(default=None, compare=False)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    reverted: bool = field(default=False, compare=False)

    event_type: ClassVar[str]

    @abstractmethod
    def apply(self, session: Session) -> None:
        pass

    @abstractmethod
    def revert(self, session: Session) -> None:
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        pass

    @abstractmethod
    def display_text(self) -> str:
        pass


@dataclass
class DeviceAdded(Event):
    event_type: ClassVar[str] = "DeviceAdded"

    device_id: int = 0
    individual_address: str | None = None
    template_id: str = ""
    name: str = ""
    parameters: list[tuple[str, str]] = field(default_factory=list)
    com_objects: list[dict[str, Any]] = field(default_factory=list)

    def apply(self, session: Session) -> int:
        if self.device_id:
            device = DeviceModel(
                id=self.device_id,
                individual_address=self.individual_address,
                template_id=self.template_id,
                name=self.name,
            )
        else:
            device = DeviceModel(
                individual_address=self.individual_address,
                template_id=self.template_id,
                name=self.name,
            )
        session.add(device)
        session.flush()
        self.device_id = device.id
        for param_id, value in self.parameters:
            param = ParameterModel(device=device, param_id=param_id, value=value)
            session.add(param)
        for co_data in self.com_objects:
            com_obj = ComObjectModel(
                device=device,
                co_id=co_data["co_id"],
                dpt_major=co_data["dpt_major"],
                dpt_minor=co_data["dpt_minor"],
                flag_communication=co_data.get("flag_communication", True),
                flag_read=co_data.get("flag_read", False),
                flag_write=co_data.get("flag_write", False),
                flag_transmit=co_data.get("flag_transmit", False),
                flag_update=co_data.get("flag_update", False),
            )
            session.add(com_obj)
        return device.id

    def revert(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            session.delete(device)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "individual_address": self.individual_address,
            "template_id": self.template_id,
            "name": self.name,
            "parameters": self.parameters,
            "com_objects": self.com_objects,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceAdded":
        return cls(
            device_id=data["device_id"],
            individual_address=data.get("individual_address"),
            template_id=data["template_id"],
            name=data["name"],
            parameters=data.get("parameters", []),
            com_objects=data.get("com_objects", []),
        )

    def display_text(self) -> str:
        return S.HISTORY_DEVICE_ADD.format(name=self.name)


@dataclass
class DeviceRemoved(Event):
    event_type: ClassVar[str] = "DeviceRemoved"

    device_id: int = 0
    individual_address: str | None = None
    template_id: str = ""
    name: str = ""
    parameters: list[tuple[str, str]] = field(default_factory=list)
    com_objects: list[dict[str, Any]] = field(default_factory=list)

    def apply(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            session.delete(device)

    def revert(self, session: Session) -> None:
        device = DeviceModel(
            id=self.device_id,
            individual_address=self.individual_address,
            template_id=self.template_id,
            name=self.name,
        )
        session.add(device)
        for param_id, value in self.parameters:
            param = ParameterModel(device=device, param_id=param_id, value=value)
            session.add(param)
        for co_data in self.com_objects:
            com_obj = ComObjectModel(
                device=device,
                co_id=co_data["co_id"],
                dpt_major=co_data["dpt_major"],
                dpt_minor=co_data["dpt_minor"],
                flag_communication=co_data.get("flag_communication", True),
                flag_read=co_data.get("flag_read", False),
                flag_write=co_data.get("flag_write", False),
                flag_transmit=co_data.get("flag_transmit", False),
                flag_update=co_data.get("flag_update", False),
            )
            session.add(com_obj)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "individual_address": self.individual_address,
            "template_id": self.template_id,
            "name": self.name,
            "parameters": self.parameters,
            "com_objects": self.com_objects,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceRemoved":
        return cls(
            device_id=data["device_id"],
            individual_address=data.get("individual_address"),
            template_id=data["template_id"],
            name=data["name"],
            parameters=data.get("parameters", []),
            com_objects=data.get("com_objects", []),
        )

    def display_text(self) -> str:
        return S.HISTORY_DEVICE_REMOVE.format(name=self.name)


@dataclass
class DeviceIndividualAddressChanged(Event):
    event_type: ClassVar[str] = "DeviceIndividualAddressChanged"

    device_id: int = 0
    old_individual_address: str | None = None
    new_individual_address: str | None = None

    def apply(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.individual_address = self.new_individual_address

    def revert(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.individual_address = self.old_individual_address

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "old_individual_address": self.old_individual_address,
            "new_individual_address": self.new_individual_address,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceIndividualAddressChanged":
        return cls(
            device_id=data["device_id"],
            old_individual_address=data.get("old_individual_address"),
            new_individual_address=data.get("new_individual_address"),
        )

    def display_text(self) -> str:
        return S.HISTORY_ADDRESS_CHANGE.format(
            old=self.old_individual_address, new=self.new_individual_address
        )


@dataclass
class DeviceNameChanged(Event):
    event_type: ClassVar[str] = "DeviceNameChanged"

    device_id: int = 0
    old_name: str = ""
    new_name: str = ""

    def apply(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.name = self.new_name

    def revert(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "old_name": self.old_name,
            "new_name": self.new_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceNameChanged":
        return cls(
            device_id=data["device_id"],
            old_name=data.get("old_name", ""),
            new_name=data.get("new_name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_NAME_CHANGE.format(old=self.old_name, new=self.new_name)


@dataclass
class ParameterChanged(Event):
    event_type: ClassVar[str] = "ParameterChanged"

    device_id: int = 0
    param_id: str = ""
    old_value: str = ""
    new_value: str = ""

    def apply(self, session: Session) -> None:
        param = (
            session.query(ParameterModel)
            .filter_by(device_id=self.device_id, param_id=self.param_id)
            .first()
        )
        if param:
            param.value = self.new_value

    def revert(self, session: Session) -> None:
        param = (
            session.query(ParameterModel)
            .filter_by(device_id=self.device_id, param_id=self.param_id)
            .first()
        )
        if param:
            param.value = self.old_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "param_id": self.param_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParameterChanged":
        return cls(
            device_id=data["device_id"],
            param_id=data["param_id"],
            old_value=data["old_value"],
            new_value=data["new_value"],
        )

    def display_text(self) -> str:
        return S.HISTORY_PARAM_CHANGE.format(old=self.old_value, new=self.new_value)


@dataclass
class ComObjectDptChanged(Event):
    event_type: ClassVar[str] = "ComObjectDptChanged"

    device_id: int = 0
    co_id: str = ""
    old_dpt_major: int = 0
    old_dpt_minor: int = 0
    new_dpt_major: int = 0
    new_dpt_minor: int = 0

    def apply(self, session: Session) -> None:
        com_obj = (
            session.query(ComObjectModel)
            .filter_by(device_id=self.device_id, co_id=self.co_id)
            .first()
        )
        if com_obj:
            com_obj.dpt_major = self.new_dpt_major
            com_obj.dpt_minor = self.new_dpt_minor

    def revert(self, session: Session) -> None:
        com_obj = (
            session.query(ComObjectModel)
            .filter_by(device_id=self.device_id, co_id=self.co_id)
            .first()
        )
        if com_obj:
            com_obj.dpt_major = self.old_dpt_major
            com_obj.dpt_minor = self.old_dpt_minor

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "co_id": self.co_id,
            "old_dpt_major": self.old_dpt_major,
            "old_dpt_minor": self.old_dpt_minor,
            "new_dpt_major": self.new_dpt_major,
            "new_dpt_minor": self.new_dpt_minor,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComObjectDptChanged":
        return cls(
            device_id=data["device_id"],
            co_id=data["co_id"],
            old_dpt_major=data["old_dpt_major"],
            old_dpt_minor=data["old_dpt_minor"],
            new_dpt_major=data["new_dpt_major"],
            new_dpt_minor=data["new_dpt_minor"],
        )

    def display_text(self) -> str:
        old = f"{self.old_dpt_major}.{self.old_dpt_minor}"
        new = f"{self.new_dpt_major}.{self.new_dpt_minor}"
        return S.HISTORY_DPT_CHANGE.format(old=old, new=new)


@dataclass
class ComObjectFlagChanged(Event):
    event_type: ClassVar[str] = "ComObjectFlagChanged"

    device_id: int = 0
    co_id: str = ""
    flag_name: str = ""
    old_value: bool = False
    new_value: bool = False

    def apply(self, session: Session) -> None:
        com_obj = (
            session.query(ComObjectModel)
            .filter_by(device_id=self.device_id, co_id=self.co_id)
            .first()
        )
        if com_obj:
            setattr(com_obj, f"flag_{self.flag_name}", self.new_value)

    def revert(self, session: Session) -> None:
        com_obj = (
            session.query(ComObjectModel)
            .filter_by(device_id=self.device_id, co_id=self.co_id)
            .first()
        )
        if com_obj:
            setattr(com_obj, f"flag_{self.flag_name}", self.old_value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "co_id": self.co_id,
            "flag_name": self.flag_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComObjectFlagChanged":
        return cls(
            device_id=data["device_id"],
            co_id=data["co_id"],
            flag_name=data["flag_name"],
            old_value=data["old_value"],
            new_value=data["new_value"],
        )

    def display_text(self) -> str:
        state = "on" if self.new_value else "off"
        return S.HISTORY_FLAG_CHANGE.format(flag=self.flag_name, state=state)


@dataclass
class LinkCreated(Event):
    event_type: ClassVar[str] = "LinkCreated"

    link_id: int = 0
    start_pin: int = 0
    end_pin: int = 0

    def apply(self, session: Session) -> None:
        link = LinkModel(
            id=self.link_id, start_pin=self.start_pin, end_pin=self.end_pin
        )
        session.add(link)

    def revert(self, session: Session) -> None:
        link = session.get(LinkModel, self.link_id)
        if link:
            session.delete(link)

    def to_dict(self) -> dict[str, Any]:
        return {
            "link_id": self.link_id,
            "start_pin": self.start_pin,
            "end_pin": self.end_pin,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinkCreated":
        return cls(
            link_id=data["link_id"],
            start_pin=data["start_pin"],
            end_pin=data["end_pin"],
        )

    def display_text(self) -> str:
        return S.HISTORY_LINK_CREATE


@dataclass
class LinkRemoved(Event):
    event_type: ClassVar[str] = "LinkRemoved"

    link_id: int = 0
    start_pin: int = 0
    end_pin: int = 0

    def apply(self, session: Session) -> None:
        link = session.get(LinkModel, self.link_id)
        if link:
            session.delete(link)

    def revert(self, session: Session) -> None:
        link = LinkModel(
            id=self.link_id, start_pin=self.start_pin, end_pin=self.end_pin
        )
        session.add(link)

    def to_dict(self) -> dict[str, Any]:
        return {
            "link_id": self.link_id,
            "start_pin": self.start_pin,
            "end_pin": self.end_pin,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinkRemoved":
        return cls(
            link_id=data["link_id"],
            start_pin=data["start_pin"],
            end_pin=data["end_pin"],
        )

    def display_text(self) -> str:
        return S.HISTORY_LINK_REMOVE


@dataclass
class AreaCreated(Event):
    event_type: ClassVar[str] = "AreaCreated"

    area_id: int = 0
    area_number: int = 0
    name: str = ""

    def apply(self, session: Session) -> int:
        if self.area_id:
            area = AreaModel(
                id=self.area_id, area_number=self.area_number, name=self.name
            )
        else:
            area = AreaModel(area_number=self.area_number, name=self.name)
        session.add(area)
        session.flush()
        self.area_id = area.id
        return area.id

    def revert(self, session: Session) -> None:
        area = session.get(AreaModel, self.area_id)
        if area:
            session.delete(area)

    def to_dict(self) -> dict[str, Any]:
        return {
            "area_id": self.area_id,
            "area_number": self.area_number,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AreaCreated":
        return cls(
            area_id=data["area_id"],
            area_number=data["area_number"],
            name=data.get("name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_AREA_CREATE.format(number=self.area_number)


@dataclass
class AreaRemoved(Event):
    event_type: ClassVar[str] = "AreaRemoved"

    area_id: int = 0
    area_number: int = 0
    name: str = ""

    def apply(self, session: Session) -> None:
        area = session.get(AreaModel, self.area_id)
        if area:
            session.delete(area)

    def revert(self, session: Session) -> None:
        area = AreaModel(id=self.area_id, area_number=self.area_number, name=self.name)
        session.add(area)

    def to_dict(self) -> dict[str, Any]:
        return {
            "area_id": self.area_id,
            "area_number": self.area_number,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AreaRemoved":
        return cls(
            area_id=data["area_id"],
            area_number=data["area_number"],
            name=data.get("name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_AREA_REMOVE.format(number=self.area_number)


@dataclass
class AreaNameChanged(Event):
    event_type: ClassVar[str] = "AreaNameChanged"

    area_id: int = 0
    old_name: str = ""
    new_name: str = ""

    def apply(self, session: Session) -> None:
        area = session.get(AreaModel, self.area_id)
        if area:
            area.name = self.new_name

    def revert(self, session: Session) -> None:
        area = session.get(AreaModel, self.area_id)
        if area:
            area.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "area_id": self.area_id,
            "old_name": self.old_name,
            "new_name": self.new_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AreaNameChanged":
        return cls(
            area_id=data["area_id"],
            old_name=data.get("old_name", ""),
            new_name=data.get("new_name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_AREA_RENAME.format(old=self.old_name, new=self.new_name)


@dataclass
class LineCreated(Event):
    event_type: ClassVar[str] = "LineCreated"

    line_id: int = 0
    area_id: int = 0
    line_number: int = 0
    name: str = ""

    def apply(self, session: Session) -> int:
        if self.line_id:
            line = LineModel(
                id=self.line_id,
                area_id=self.area_id,
                line_number=self.line_number,
                name=self.name,
            )
        else:
            line = LineModel(
                area_id=self.area_id,
                line_number=self.line_number,
                name=self.name,
            )
        session.add(line)
        session.flush()
        self.line_id = line.id
        return line.id

    def revert(self, session: Session) -> None:
        line = session.get(LineModel, self.line_id)
        if line:
            session.delete(line)

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "area_id": self.area_id,
            "line_number": self.line_number,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineCreated":
        return cls(
            line_id=data["line_id"],
            area_id=data["area_id"],
            line_number=data["line_number"],
            name=data.get("name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_LINE_CREATE.format(number=self.line_number)


@dataclass
class LineRemoved(Event):
    event_type: ClassVar[str] = "LineRemoved"

    line_id: int = 0
    area_id: int = 0
    line_number: int = 0
    name: str = ""

    def apply(self, session: Session) -> None:
        line = session.get(LineModel, self.line_id)
        if line:
            session.delete(line)

    def revert(self, session: Session) -> None:
        line = LineModel(
            id=self.line_id,
            area_id=self.area_id,
            line_number=self.line_number,
            name=self.name,
        )
        session.add(line)

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "area_id": self.area_id,
            "line_number": self.line_number,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineRemoved":
        return cls(
            line_id=data["line_id"],
            area_id=data["area_id"],
            line_number=data["line_number"],
            name=data.get("name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_LINE_REMOVE.format(number=self.line_number)


@dataclass
class LineNameChanged(Event):
    event_type: ClassVar[str] = "LineNameChanged"

    line_id: int = 0
    old_name: str = ""
    new_name: str = ""

    def apply(self, session: Session) -> None:
        line = session.get(LineModel, self.line_id)
        if line:
            line.name = self.new_name

    def revert(self, session: Session) -> None:
        line = session.get(LineModel, self.line_id)
        if line:
            line.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "line_id": self.line_id,
            "old_name": self.old_name,
            "new_name": self.new_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineNameChanged":
        return cls(
            line_id=data["line_id"],
            old_name=data.get("old_name", ""),
            new_name=data.get("new_name", ""),
        )

    def display_text(self) -> str:
        return S.HISTORY_LINE_RENAME.format(old=self.old_name, new=self.new_name)


EVENT_TYPES: dict[str, type[Event]] = {
    "AreaCreated": AreaCreated,
    "AreaNameChanged": AreaNameChanged,
    "AreaRemoved": AreaRemoved,
    "ComObjectDptChanged": ComObjectDptChanged,
    "ComObjectFlagChanged": ComObjectFlagChanged,
    "DeviceAdded": DeviceAdded,
    "DeviceIndividualAddressChanged": DeviceIndividualAddressChanged,
    "DeviceNameChanged": DeviceNameChanged,
    "DeviceRemoved": DeviceRemoved,
    "LineCreated": LineCreated,
    "LineNameChanged": LineNameChanged,
    "LineRemoved": LineRemoved,
    "LinkCreated": LinkCreated,
    "LinkRemoved": LinkRemoved,
    "ParameterChanged": ParameterChanged,
}


def deserialize_event(event_type: str, data: dict[str, Any]) -> Event:
    cls = EVENT_TYPES.get(event_type)
    if cls is None:
        raise ValueError(f"Unknown event type: {event_type}")
    return cls.from_dict(data)
