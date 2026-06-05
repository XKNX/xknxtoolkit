"""Events — the reversible unit of every edit, applied against a SQLAlchemy ``Session``.

Each event mutates the relational graph and knows how to undo itself. Events capture every row id
they create on first ``apply`` (the ``if self.x_id is not None`` idiom) so a redo re-inserts with
the same ids and downstream foreign keys stay valid. ``to_dict``/``from_dict`` serialise the full
payload — inputs plus captured ids and any before-values needed by ``revert`` — into the ``events``
table's JSON column, so undo/redo survives a close/reopen.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from sqlalchemy.orm import Session

from xknxmono.project.core.skeleton import MEDIUM_IP, three_level_ranges
from xknxmono.project.models import (
    Area,
    ComObject,
    ComObjectLink,
    Device,
    GroupAddress,
    GroupRange,
    Installation,
    Line,
    Parameter,
    Segment,
)

EVENT_TYPES: dict[str, type[Event]] = {}


def _register[E: Event](cls: type[E]) -> type[E]:
    EVENT_TYPES[cls.event_type] = cls
    return cls


def deserialize_event(event_type: str, data: dict[str, Any]) -> Event:
    cls = EVENT_TYPES.get(event_type)
    if cls is None:
        raise ValueError(f"Unknown event type: {event_type}")
    return cls.from_dict(data)


class Event(ABC):
    event_type: ClassVar[str]

    @abstractmethod
    def apply(self, session: Session) -> None: ...

    @abstractmethod
    def revert(self, session: Session) -> None: ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]: ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Event: ...

    def display_text(self) -> str:
        return self.event_type


@_register
@dataclass
class AddInstallation(Event):
    event_type: ClassVar[str] = "AddInstallation"

    index: int
    name: str
    installation_id: int | None = None
    area_id: int | None = None
    line_id: int | None = None
    segment_id: int | None = None

    def apply(self, session: Session) -> None:
        inst = Installation(index=self.index, name=self.name)
        if self.installation_id is not None:
            inst.id = self.installation_id
        area = Area(address=0, name="")
        if self.area_id is not None:
            area.id = self.area_id
        line = Line(address=0, name="")
        if self.line_id is not None:
            line.id = self.line_id
        segment = Segment(number=0, medium_type=MEDIUM_IP)
        if self.segment_id is not None:
            segment.id = self.segment_id
        line.segments.append(segment)
        area.lines.append(line)
        inst.areas.append(area)
        session.add(inst)
        session.flush()
        self.installation_id = inst.id
        self.area_id = area.id
        self.line_id = line.id
        self.segment_id = segment.id

    def revert(self, session: Session) -> None:
        inst = session.get(Installation, self.installation_id)
        if inst is not None:
            session.delete(inst)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "installation_id": self.installation_id,
            "area_id": self.area_id,
            "line_id": self.line_id,
            "segment_id": self.segment_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AddInstallation:
        return cls(**data)

    def display_text(self) -> str:
        return f"Add installation {self.name!r}"


@_register
@dataclass
class CreateArea(Event):
    event_type: ClassVar[str] = "CreateArea"

    installation_id: int
    address: int
    name: str
    area_id: int | None = None

    def apply(self, session: Session) -> None:
        area = Area(
            installation_id=self.installation_id, address=self.address, name=self.name
        )
        if self.area_id is not None:
            area.id = self.area_id
        session.add(area)
        session.flush()
        self.area_id = area.id

    def revert(self, session: Session) -> None:
        area = session.get(Area, self.area_id)
        if area is not None:
            session.delete(area)

    def to_dict(self) -> dict[str, Any]:
        return {
            "installation_id": self.installation_id,
            "address": self.address,
            "name": self.name,
            "area_id": self.area_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateArea:
        return cls(**data)

    def display_text(self) -> str:
        return f"Create area {self.address}"


@_register
@dataclass
class CreateLine(Event):
    event_type: ClassVar[str] = "CreateLine"

    area_id: int
    address: int
    name: str
    medium_type: str
    line_id: int | None = None
    segment_id: int | None = None

    def apply(self, session: Session) -> None:
        line = Line(area_id=self.area_id, address=self.address, name=self.name)
        if self.line_id is not None:
            line.id = self.line_id
        segment = Segment(number=0, medium_type=self.medium_type)
        if self.segment_id is not None:
            segment.id = self.segment_id
        line.segments.append(segment)
        session.add(line)
        session.flush()
        self.line_id = line.id
        self.segment_id = segment.id

    def revert(self, session: Session) -> None:
        line = session.get(Line, self.line_id)
        if line is not None:
            session.delete(line)

    def to_dict(self) -> dict[str, Any]:
        return {
            "area_id": self.area_id,
            "address": self.address,
            "name": self.name,
            "medium_type": self.medium_type,
            "line_id": self.line_id,
            "segment_id": self.segment_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateLine:
        return cls(**data)

    def display_text(self) -> str:
        return f"Create line {self.address}"


@_register
@dataclass
class AddDevice(Event):
    event_type: ClassVar[str] = "AddDevice"

    segment_id: int
    address: int | None
    name: str
    product_ref_id: str
    hardware2program_ref_id: str | None
    parameters: list[list[str]] = field(default_factory=list[list[str]])
    com_object_refs: list[str] = field(default_factory=list[str])
    device_id: int | None = None
    parameter_ids: list[int] = field(default_factory=list[int])
    com_object_ids: list[int] = field(default_factory=list[int])

    def apply(self, session: Session) -> None:
        device = Device(
            segment_id=self.segment_id,
            address=self.address,
            name=self.name,
            product_ref_id=self.product_ref_id,
            hardware2program_ref_id=self.hardware2program_ref_id,
        )
        if self.device_id is not None:
            device.id = self.device_id
        for i, (ref_id, value) in enumerate(self.parameters):
            param = Parameter(ref_id=ref_id, value=value)
            if i < len(self.parameter_ids):
                param.id = self.parameter_ids[i]
            device.parameters.append(param)
        for i, ref_id in enumerate(self.com_object_refs):
            com_object = ComObject(ref_id=ref_id)
            if i < len(self.com_object_ids):
                com_object.id = self.com_object_ids[i]
            device.com_objects.append(com_object)
        session.add(device)
        session.flush()
        self.device_id = device.id
        self.parameter_ids = [p.id for p in device.parameters]
        self.com_object_ids = [c.id for c in device.com_objects]

    def revert(self, session: Session) -> None:
        device = session.get(Device, self.device_id)
        if device is not None:
            session.delete(device)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "address": self.address,
            "name": self.name,
            "product_ref_id": self.product_ref_id,
            "hardware2program_ref_id": self.hardware2program_ref_id,
            "parameters": self.parameters,
            "com_object_refs": self.com_object_refs,
            "device_id": self.device_id,
            "parameter_ids": self.parameter_ids,
            "com_object_ids": self.com_object_ids,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AddDevice:
        return cls(**data)

    def display_text(self) -> str:
        return f"Add device {self.name!r}"


@_register
@dataclass
class SetParameter(Event):
    event_type: ClassVar[str] = "SetParameter"

    device_id: int
    ref_id: str
    value: str
    existed: bool | None = None
    old_value: str | None = None
    parameter_id: int | None = None

    def _find(self, session: Session) -> Parameter | None:
        return (
            session.query(Parameter)
            .filter_by(device_id=self.device_id, ref_id=self.ref_id)
            .first()
        )

    def apply(self, session: Session) -> None:
        param = self._find(session)
        if param is not None:
            self.existed = True
            self.old_value = param.value
            param.value = self.value
        else:
            self.existed = False
            param = Parameter(
                device_id=self.device_id, ref_id=self.ref_id, value=self.value
            )
            if self.parameter_id is not None:
                param.id = self.parameter_id
            session.add(param)
            session.flush()
            self.parameter_id = param.id

    def revert(self, session: Session) -> None:
        if self.existed:
            param = self._find(session)
            if param is not None and self.old_value is not None:
                param.value = self.old_value
        else:
            param = session.get(Parameter, self.parameter_id)
            if param is not None:
                session.delete(param)

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "ref_id": self.ref_id,
            "value": self.value,
            "existed": self.existed,
            "old_value": self.old_value,
            "parameter_id": self.parameter_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SetParameter:
        return cls(**data)

    def display_text(self) -> str:
        return f"Set {self.ref_id} = {self.value!r}"


@_register
@dataclass
class CreateGroupAddress(Event):
    """Add a group address, ETS-style: find-or-create the containing main/middle ranges as one
    undoable step (``created_main``/``created_middle`` record which ranges this event created)."""

    event_type: ClassVar[str] = "CreateGroupAddress"

    installation_id: int
    address: int
    name: str
    main_range_id: int | None = None
    middle_range_id: int | None = None
    ga_id: int | None = None
    created_main: bool = False
    created_middle: bool = False

    def apply(self, session: Session) -> None:
        main_start, main_end, mid_start, mid_end = three_level_ranges(self.address)

        main = (
            session.query(GroupRange)
            .filter_by(
                installation_id=self.installation_id,
                parent_id=None,
                range_start=main_start,
            )
            .first()
        )
        if main is None:
            main = GroupRange(
                installation_id=self.installation_id,
                parent_id=None,
                range_start=main_start,
                range_end=main_end,
                name="New main group",
            )
            if self.main_range_id is not None:
                main.id = self.main_range_id
            session.add(main)
            session.flush()
            self.created_main = True
        else:
            self.created_main = False
        self.main_range_id = main.id

        middle = (
            session.query(GroupRange)
            .filter_by(
                installation_id=self.installation_id,
                parent_id=main.id,
                range_start=mid_start,
            )
            .first()
        )
        if middle is None:
            middle = GroupRange(
                installation_id=self.installation_id,
                parent_id=main.id,
                range_start=mid_start,
                range_end=mid_end,
                name="New middle group",
            )
            if self.middle_range_id is not None:
                middle.id = self.middle_range_id
            session.add(middle)
            session.flush()
            self.created_middle = True
        else:
            self.created_middle = False
        self.middle_range_id = middle.id

        ga = GroupAddress(
            group_range_id=middle.id, address=self.address, name=self.name
        )
        if self.ga_id is not None:
            ga.id = self.ga_id
        session.add(ga)
        session.flush()
        self.ga_id = ga.id

    def revert(self, session: Session) -> None:
        # Delete the outermost thing this event created; cascade removes everything nested under it
        # (a created main contains the created middle, which contains the group address).
        if self.created_main:
            target = session.get(GroupRange, self.main_range_id)
        elif self.created_middle:
            target = session.get(GroupRange, self.middle_range_id)
        else:
            target = session.get(GroupAddress, self.ga_id)
        if target is not None:
            session.delete(target)

    def to_dict(self) -> dict[str, Any]:
        return {
            "installation_id": self.installation_id,
            "address": self.address,
            "name": self.name,
            "main_range_id": self.main_range_id,
            "middle_range_id": self.middle_range_id,
            "ga_id": self.ga_id,
            "created_main": self.created_main,
            "created_middle": self.created_middle,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateGroupAddress:
        return cls(**data)

    def display_text(self) -> str:
        return f"Create group address {self.address}"


@_register
@dataclass
class LinkComObject(Event):
    event_type: ClassVar[str] = "LinkComObject"

    com_object_id: int
    group_address_id: int
    link_id: int | None = None

    def apply(self, session: Session) -> None:
        link = ComObjectLink(
            com_object_id=self.com_object_id, group_address_id=self.group_address_id
        )
        if self.link_id is not None:
            link.id = self.link_id
        session.add(link)
        session.flush()
        self.link_id = link.id

    def revert(self, session: Session) -> None:
        link = session.get(ComObjectLink, self.link_id)
        if link is not None:
            session.delete(link)

    def to_dict(self) -> dict[str, Any]:
        return {
            "com_object_id": self.com_object_id,
            "group_address_id": self.group_address_id,
            "link_id": self.link_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LinkComObject:
        return cls(**data)

    def display_text(self) -> str:
        return "Link com-object"
