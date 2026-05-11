from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from sqlalchemy.orm import Session

from knx_gui.project.models import (
    ComObjectModel,
    DeviceModel,
    LinkModel,
    ParameterModel,
)


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


@dataclass
class DeviceAdded(Event):
    event_type: ClassVar[str] = "DeviceAdded"

    device_id: int = 0
    address: str | None = None
    template_id: str = ""
    name: str = ""
    parameters: list[tuple[str, str]] = field(default_factory=list)
    com_objects: list[dict[str, Any]] = field(default_factory=list)

    def apply(self, session: Session) -> None:
        device = DeviceModel(
            id=self.device_id,
            address=self.address,
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

    def revert(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            session.delete(device)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "address": self.address,
            "template_id": self.template_id,
            "name": self.name,
            "parameters": self.parameters,
            "com_objects": self.com_objects,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceAdded":
        return cls(
            device_id=data["device_id"],
            address=data.get("address"),
            template_id=data["template_id"],
            name=data["name"],
            parameters=data.get("parameters", []),
            com_objects=data.get("com_objects", []),
        )


@dataclass
class DeviceRemoved(Event):
    event_type: ClassVar[str] = "DeviceRemoved"

    device_id: int = 0
    address: str | None = None
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
            address=self.address,
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
            "address": self.address,
            "template_id": self.template_id,
            "name": self.name,
            "parameters": self.parameters,
            "com_objects": self.com_objects,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceRemoved":
        return cls(
            device_id=data["device_id"],
            address=data.get("address"),
            template_id=data["template_id"],
            name=data["name"],
            parameters=data.get("parameters", []),
            com_objects=data.get("com_objects", []),
        )


@dataclass
class DeviceAddressChanged(Event):
    event_type: ClassVar[str] = "DeviceAddressChanged"

    device_id: int = 0
    old_address: str | None = None
    new_address: str | None = None

    def apply(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.address = self.new_address

    def revert(self, session: Session) -> None:
        device = session.get(DeviceModel, self.device_id)
        if device:
            device.address = self.old_address

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "old_address": self.old_address,
            "new_address": self.new_address,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceAddressChanged":
        return cls(
            device_id=data["device_id"],
            old_address=data.get("old_address"),
            new_address=data.get("new_address"),
        )


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


EVENT_TYPES: dict[str, type[Event]] = {
    "DeviceAdded": DeviceAdded,
    "DeviceRemoved": DeviceRemoved,
    "DeviceAddressChanged": DeviceAddressChanged,
    "ParameterChanged": ParameterChanged,
    "ComObjectDptChanged": ComObjectDptChanged,
    "ComObjectFlagChanged": ComObjectFlagChanged,
    "LinkCreated": LinkCreated,
    "LinkRemoved": LinkRemoved,
}


def deserialize_event(event_type: str, data: dict[str, Any]) -> Event:
    cls = EVENT_TYPES.get(event_type)
    if cls is None:
        raise ValueError(f"Unknown event type: {event_type}")
    return cls.from_dict(data)
