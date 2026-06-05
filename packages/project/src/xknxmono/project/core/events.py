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

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Session

from xknxmono.project.core.skeleton import MEDIUM_IP
from xknxmono.project.models import (
    Area,
    Base,
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


@_register
@dataclass
class CreateGroupAddress(Event):
    """Add a group address, finding-or-creating its containing range chain as one undoable step.

    ``levels`` is the ``[range_start, range_end, name]`` chain (top → leaf) the address belongs in
    for the project's style — see :func:`xknxmono.project.core.addressing.ranges_for`. ``range_ids``
    and ``created`` (captured on apply) record each level's row id and whether this event created it,
    so revert removes only what it added and redo re-creates with the same ids."""

    event_type: ClassVar[str] = "CreateGroupAddress"

    installation_id: int
    address: int
    name: str
    levels: list[list[Any]] = field(default_factory=list[list[Any]])
    range_ids: list[int] = field(default_factory=list[int])
    created: list[bool] = field(default_factory=list[bool])
    ga_id: int | None = None

    def apply(self, session: Session) -> None:
        parent_id: int | None = None
        range_ids: list[int] = []
        created: list[bool] = []
        for i, (start, end, range_name) in enumerate(self.levels):
            existing = (
                session.query(GroupRange)
                .filter_by(
                    installation_id=self.installation_id,
                    parent_id=parent_id,
                    range_start=start,
                )
                .first()
            )
            if existing is None:
                group_range = GroupRange(
                    installation_id=self.installation_id,
                    parent_id=parent_id,
                    range_start=start,
                    range_end=end,
                    name=range_name,
                )
                if i < len(self.range_ids):
                    group_range.id = self.range_ids[i]
                session.add(group_range)
                session.flush()
                created.append(True)
            else:
                group_range = existing
                created.append(False)
            range_ids.append(group_range.id)
            parent_id = group_range.id
        self.range_ids = range_ids
        self.created = created

        ga = GroupAddress(
            group_range_id=parent_id, address=self.address, name=self.name
        )
        if self.ga_id is not None:
            ga.id = self.ga_id
        session.add(ga)
        session.flush()
        self.ga_id = ga.id

    def revert(self, session: Session) -> None:
        # Delete the shallowest range this event created (cascade removes deeper created ranges and
        # the group address); if it created none, just remove the group address itself.
        first_created = next((i for i, made in enumerate(self.created) if made), None)
        if first_created is not None:
            target = session.get(GroupRange, self.range_ids[first_created])
        else:
            target = session.get(GroupAddress, self.ga_id)
        if target is not None:
            session.delete(target)

    def to_dict(self) -> dict[str, Any]:
        return {
            "installation_id": self.installation_id,
            "address": self.address,
            "name": self.name,
            "levels": self.levels,
            "range_ids": self.range_ids,
            "created": self.created,
            "ga_id": self.ga_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreateGroupAddress:
        return cls(**data)


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


# --- reversible deletes (snapshot the subtree, restore it on revert) ----------


@dataclass
class _SubtreeDelete(Event):
    """Delete a row (and everything cascade-owned under it), capturing the deleted rows so revert
    re-inserts them with their original ids — keeping any external foreign keys valid."""

    _model: ClassVar[type[Base]]

    target_id: int
    rows: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])

    def apply(self, session: Session) -> None:
        obj = session.get(self._model, self.target_id)
        if obj is not None:
            self.rows = _snapshot_subtree(obj)
            session.delete(obj)

    def revert(self, session: Session) -> None:
        _restore_rows(session, self.rows)

    def to_dict(self) -> dict[str, Any]:
        return {"target_id": self.target_id, "rows": self.rows}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> _SubtreeDelete:
        return cls(**data)


@_register
@dataclass
class RemoveDevice(_SubtreeDelete):
    event_type: ClassVar[str] = "RemoveDevice"
    _model: ClassVar[type[Base]] = Device


@_register
@dataclass
class RemoveArea(_SubtreeDelete):
    event_type: ClassVar[str] = "RemoveArea"
    _model: ClassVar[type[Base]] = Area


@_register
@dataclass
class RemoveLine(_SubtreeDelete):
    event_type: ClassVar[str] = "RemoveLine"
    _model: ClassVar[type[Base]] = Line


@_register
@dataclass
class RemoveGroupAddress(_SubtreeDelete):
    event_type: ClassVar[str] = "RemoveGroupAddress"
    _model: ClassVar[type[Base]] = GroupAddress


@_register
@dataclass
class UnlinkComObject(_SubtreeDelete):
    event_type: ClassVar[str] = "UnlinkComObject"
    _model: ClassVar[type[Base]] = ComObjectLink


# --- field changes (capture the old value, restore it on revert) --------------


@_register
@dataclass
class RenameArea(Event):
    event_type: ClassVar[str] = "RenameArea"

    area_id: int
    name: str
    old_name: str | None = None

    def apply(self, session: Session) -> None:
        area = session.get(Area, self.area_id)
        if area is not None:
            self.old_name = area.name
            area.name = self.name

    def revert(self, session: Session) -> None:
        area = session.get(Area, self.area_id)
        if area is not None and self.old_name is not None:
            area.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {"area_id": self.area_id, "name": self.name, "old_name": self.old_name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RenameArea:
        return cls(**data)


@_register
@dataclass
class RenameLine(Event):
    event_type: ClassVar[str] = "RenameLine"

    line_id: int
    name: str
    old_name: str | None = None

    def apply(self, session: Session) -> None:
        line = session.get(Line, self.line_id)
        if line is not None:
            self.old_name = line.name
            line.name = self.name

    def revert(self, session: Session) -> None:
        line = session.get(Line, self.line_id)
        if line is not None and self.old_name is not None:
            line.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {"line_id": self.line_id, "name": self.name, "old_name": self.old_name}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RenameLine:
        return cls(**data)


@_register
@dataclass
class SetDeviceName(Event):
    event_type: ClassVar[str] = "SetDeviceName"

    device_id: int
    name: str
    old_name: str | None = None

    def apply(self, session: Session) -> None:
        device = session.get(Device, self.device_id)
        if device is not None:
            self.old_name = device.name
            device.name = self.name

    def revert(self, session: Session) -> None:
        device = session.get(Device, self.device_id)
        if device is not None and self.old_name is not None:
            device.name = self.old_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "old_name": self.old_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SetDeviceName:
        return cls(**data)


@_register
@dataclass
class MoveDevice(Event):
    """Move a device to another segment and/or change its individual-address octet."""

    event_type: ClassVar[str] = "MoveDevice"

    device_id: int
    segment_id: int
    address: int | None
    old_segment_id: int | None = None
    old_address: int | None = None

    def apply(self, session: Session) -> None:
        device = session.get(Device, self.device_id)
        if device is not None:
            self.old_segment_id = device.segment_id
            self.old_address = device.address
            device.segment_id = self.segment_id
            device.address = self.address

    def revert(self, session: Session) -> None:
        device = session.get(Device, self.device_id)
        if device is not None and self.old_segment_id is not None:
            device.segment_id = self.old_segment_id
            device.address = self.old_address

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "segment_id": self.segment_id,
            "address": self.address,
            "old_segment_id": self.old_segment_id,
            "old_address": self.old_address,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoveDevice:
        return cls(**data)


# --- subtree snapshot helpers -------------------------------------------------

_MODELS: dict[str, type[Base]] = {
    m.__name__: m
    for m in (
        Installation,
        Area,
        Line,
        Segment,
        Device,
        Parameter,
        ComObject,
        GroupRange,
        GroupAddress,
        ComObjectLink,
    )
}


def _row_to_dict(obj: Base) -> dict[str, Any]:
    mapper = sa_inspect(type(obj))
    data: dict[str, Any] = {"__model__": type(obj).__name__}
    for column in mapper.columns:
        data[column.name] = getattr(obj, column.name)
    return data


def _snapshot_subtree(obj: Base) -> list[dict[str, Any]]:
    """Capture ``obj`` then every cascade-owned descendant, parents first (restore-safe order)."""
    rows = [_row_to_dict(obj)]
    mapper = sa_inspect(type(obj))
    for rel in mapper.relationships:
        if rel.direction.name == "ONETOMANY" and rel.cascade.delete_orphan:
            for child in getattr(obj, rel.key):
                rows.extend(_snapshot_subtree(child))
    return rows


def _restore_rows(session: Session, rows: list[dict[str, Any]]) -> None:
    for data in rows:
        payload = dict(data)
        model = _MODELS[payload.pop("__model__")]
        session.add(model(**payload))
    session.flush()
