"""`ProjectService` — owns N open projects (one SQLite document each), keyed by project id.

Every edit funnels through an :class:`~xknxmono.project.core.event_store.EventStore`, which applies
the event, persists it to the ``events`` history, and manages the undo/redo cursor. The live state
is the relational tables; reads return ORM rows. Installation-scoped calls take the installation's
0-based ``index``; other graph references use internal row ids.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from xknxmono.project.core.addressing import (
    GroupAddressStyle,
    format_ga,
    format_ia,
    parse_ia,
    ranges_for,
)
from xknxmono.project.core.event_store import EventStore, HistoryEntry
from xknxmono.project.core.events import (
    COM_OBJECT_FLAGS,
    AddDevice,
    AddInstallation,
    CreateArea,
    CreateGroupAddress,
    CreateLine,
    LinkComObject,
    MoveDevice,
    RemoveArea,
    RemoveDevice,
    RemoveGroupAddress,
    RemoveLine,
    RenameArea,
    RenameLine,
    SetComObjectFlag,
    SetDeviceName,
    SetGroupAddressDatapointType,
    SetParameter,
    UnlinkComObject,
)
from xknxmono.project.core.skeleton import MEDIUM_TP, seed_new_project
from xknxmono.project.db import make_engine, url_for
from xknxmono.project.models import (
    Area,
    Device,
    GroupAddress,
    GroupRange,
    Installation,
    Line,
    Project,
    Segment,
)


@dataclass
class _Open:
    engine: Engine
    session: Session
    store: EventStore


@dataclass(frozen=True)
class GroupAddressInfo:
    """A group address resolved for display: its value, the style-formatted string, and its links."""

    id: int
    address: int
    text: str
    name: str
    datapoint_type: str | None
    links: list[int]


@dataclass(frozen=True)
class DeviceInfo:
    """A device resolved for display. The refs identify the catalog product and the loaded program;
    callers resolve the application from them (the project package itself is ref-only)."""

    id: int
    name: str
    individual_address: str | None
    product_ref_id: str
    hardware2program_ref_id: str | None


class ProjectService:
    def __init__(self) -> None:
        self._projects: dict[str, _Open] = {}

    # --- lifecycle --------------------------------------------------------

    def create(
        self,
        path: Path | str,
        project_id: str | None = None,
        *,
        group_address_style: GroupAddressStyle = GroupAddressStyle.THREE_LEVEL,
    ) -> str:
        pid = project_id or f"P-{uuid4().hex[:8].upper()}"
        engine = make_engine(url_for(Path(path)))
        session = Session(engine)
        seed_new_project(session, pid, "New project", group_address_style)
        self._register(pid, engine, session)
        return pid

    def open(self, path: Path | str) -> str:
        engine = make_engine(url_for(Path(path)))
        session = Session(engine)
        project = session.query(Project).first()
        if project is None:
            raise ValueError(f"{path} is not a project (no project row)")
        self._register(project.id, engine, session)
        return project.id

    def close(self, project_id: str) -> None:
        state = self._projects.pop(project_id)
        state.session.close()
        state.engine.dispose()

    def list(self) -> list[str]:
        return list(self._projects)

    # --- commands (one public method each) --------------------------------

    def add_installation(self, project_id: str, name: str) -> int:
        state = self._state(project_id)
        highest = state.session.query(func.max(Installation.index)).scalar()
        index = highest + 1 if highest is not None else 0
        state.store.append(AddInstallation(index=index, name=name))
        return index

    def create_area(
        self, project_id: str, installation: int, address: int, name: str
    ) -> int:
        state = self._state(project_id)
        event = CreateArea(
            installation_id=self._installation(state, installation).id,
            address=address,
            name=name,
        )
        state.store.append(event)
        assert event.area_id is not None
        return event.area_id

    def create_line(
        self, project_id: str, area_id: int, address: int, name: str
    ) -> int:
        state = self._state(project_id)
        event = CreateLine(
            area_id=area_id, address=address, name=name, medium_type=MEDIUM_TP
        )
        state.store.append(event)
        assert event.line_id is not None
        return event.line_id

    def add_device(
        self,
        project_id: str,
        segment_id: int,
        product_ref_id: str,
        *,
        address: int | None = None,
        name: str = "",
        hardware2program_ref_id: str | None = None,
        parameters: list[tuple[str, str]] | None = None,
        com_object_refs: list[str] | None = None,
    ) -> int:
        """Add a device. ``product_ref_id`` is the catalog product; ``hardware2program_ref_id`` is
        the loaded program through which the application resolves. The project package is ref-only —
        it never reads the catalog, so the caller expands the application and passes its
        ``parameters`` (``(ref_id, value)``) and ``com_object_refs`` (``ref_id``) in."""
        state = self._state(project_id)
        if address is not None:
            self._check_unique_address(state, segment_id, address)
        event = AddDevice(
            segment_id=segment_id,
            address=address,
            name=name,
            product_ref_id=product_ref_id,
            hardware2program_ref_id=hardware2program_ref_id,
            parameters=[[ref, value] for ref, value in (parameters or [])],
            com_object_refs=list(com_object_refs or []),
        )
        state.store.append(event)
        assert event.device_id is not None
        return event.device_id

    def set_parameter(
        self, project_id: str, device_id: int, ref_id: str, value: str
    ) -> None:
        self._state(project_id).store.append(
            SetParameter(device_id=device_id, ref_id=ref_id, value=value)
        )

    def create_group_address(
        self, project_id: str, installation: int, address: int, name: str
    ) -> int:
        state = self._state(project_id)
        levels = ranges_for(address, self._style(state))
        event = CreateGroupAddress(
            installation_id=self._installation(state, installation).id,
            address=address,
            name=name,
            levels=[[start, end, range_name] for start, end, range_name in levels],
        )
        state.store.append(event)
        assert event.ga_id is not None
        return event.ga_id

    def link_com_object(
        self, project_id: str, com_object_id: int, group_address_id: int
    ) -> int:
        state = self._state(project_id)
        event = LinkComObject(
            com_object_id=com_object_id, group_address_id=group_address_id
        )
        state.store.append(event)
        assert event.link_id is not None
        return event.link_id

    def set_com_object_flag(
        self, project_id: str, com_object_id: int, flag: str, value: bool | None
    ) -> None:
        """Override a com-object flag (``value`` forces it; ``None`` reverts to the product default).

        ``flag`` is one of :data:`~xknxmono.project.core.events.COM_OBJECT_FLAGS`."""
        if flag not in COM_OBJECT_FLAGS:
            raise ValueError(f"Unknown com-object flag {flag!r}")
        self._state(project_id).store.append(
            SetComObjectFlag(com_object_id=com_object_id, flag=flag, value=value)
        )

    def set_group_address_datapoint_type(
        self, project_id: str, group_address_id: int, datapoint_type: str | None
    ) -> None:
        self._state(project_id).store.append(
            SetGroupAddressDatapointType(
                group_address_id=group_address_id, datapoint_type=datapoint_type
            )
        )

    # --- remove / rename / move -------------------------------------------

    def remove_device(self, project_id: str, device_id: int) -> None:
        self._state(project_id).store.append(RemoveDevice(target_id=device_id))

    def remove_area(self, project_id: str, area_id: int) -> None:
        self._state(project_id).store.append(RemoveArea(target_id=area_id))

    def remove_line(self, project_id: str, line_id: int) -> None:
        self._state(project_id).store.append(RemoveLine(target_id=line_id))

    def remove_group_address(self, project_id: str, group_address_id: int) -> None:
        self._state(project_id).store.append(
            RemoveGroupAddress(target_id=group_address_id)
        )

    def unlink_com_object(self, project_id: str, link_id: int) -> None:
        self._state(project_id).store.append(UnlinkComObject(target_id=link_id))

    def rename_area(self, project_id: str, area_id: int, name: str) -> None:
        self._state(project_id).store.append(RenameArea(area_id=area_id, name=name))

    def rename_line(self, project_id: str, line_id: int, name: str) -> None:
        self._state(project_id).store.append(RenameLine(line_id=line_id, name=name))

    def set_device_name(self, project_id: str, device_id: int, name: str) -> None:
        self._state(project_id).store.append(
            SetDeviceName(device_id=device_id, name=name)
        )

    def move_device(
        self, project_id: str, device_id: int, segment_id: int, address: int | None
    ) -> None:
        state = self._state(project_id)
        if address is not None:
            self._check_unique_address(state, segment_id, address, exclude=device_id)
        state.store.append(
            MoveDevice(device_id=device_id, segment_id=segment_id, address=address)
        )

    # --- undo / redo / history --------------------------------------------

    def undo(self, project_id: str) -> bool:
        return self._state(project_id).store.undo()

    def redo(self, project_id: str) -> bool:
        return self._state(project_id).store.redo()

    def can_undo(self, project_id: str) -> bool:
        return self._state(project_id).store.can_undo()

    def can_redo(self, project_id: str) -> bool:
        return self._state(project_id).store.can_redo()

    def cursor(self, project_id: str) -> int:
        return self._state(project_id).store.cursor

    def jump_to(self, project_id: str, event_id: int) -> None:
        self._state(project_id).store.jump_to(event_id)

    def history(self, project_id: str) -> list[HistoryEntry]:
        return self._state(project_id).store.history()

    # --- reads ------------------------------------------------------------

    def project(self, project_id: str) -> Project:
        project = self._state(project_id).session.get(Project, project_id)
        assert project is not None
        return project

    def installations(self, project_id: str) -> list[Installation]:
        return (
            self._state(project_id)
            .session.query(Installation)
            .order_by(Installation.index)
            .all()
        )

    def topology(self, project_id: str, installation: int) -> Installation:
        return self._installation(self._state(project_id), installation)

    def devices(self, project_id: str) -> list[Device]:
        return self._state(project_id).session.query(Device).order_by(Device.id).all()

    def device(self, project_id: str, device_id: int) -> DeviceInfo:
        """A device resolved for display (composed individual address + catalog/program refs)."""
        state = self._state(project_id)
        device = state.session.get(Device, device_id)
        if device is None:
            raise KeyError(f"No device with id {device_id}")
        return DeviceInfo(
            id=device.id,
            name=device.name,
            individual_address=self._compose_ia(device),
            product_ref_id=device.product_ref_id,
            hardware2program_ref_id=device.hardware2program_ref_id,
        )

    def group_addresses(self, project_id: str) -> list[GroupAddressInfo]:
        state = self._state(project_id)
        style = self._style(state)
        rows = state.session.query(GroupAddress).order_by(GroupAddress.id).all()
        return [self._ga_info(row, style) for row in rows]

    def group_address(self, project_id: str, group_address_id: int) -> GroupAddressInfo:
        state = self._state(project_id)
        ga = state.session.get(GroupAddress, group_address_id)
        if ga is None:
            raise KeyError(f"No group address with id {group_address_id}")
        return self._ga_info(ga, self._style(state))

    def next_free_group_address(
        self, project_id: str, installation: int, *, start: int = 1
    ) -> int:
        """The lowest unused group-address value (>= ``start``) in the installation. Address 0 is
        reserved, so allocation begins at 1."""
        state = self._state(project_id)
        inst = self._installation(state, installation)
        used = {
            address
            for (address,) in state.session.query(GroupAddress.address)
            .join(GroupRange, GroupAddress.group_range_id == GroupRange.id)
            .filter(GroupRange.installation_id == inst.id)
        }
        address = max(1, start)
        while address in used:
            address += 1
        if address > 0xFFFF:
            raise ValueError("no free group address available")
        return address

    # --- individual-address helpers ---------------------------------------

    def individual_address(self, project_id: str, device_id: int) -> str | None:
        """The device's ``area.line.device`` string, or ``None`` if its octet is unassigned."""
        state = self._state(project_id)
        device = state.session.get(Device, device_id)
        if device is None:
            raise KeyError(f"No device with id {device_id}")
        return self._compose_ia(device)

    def next_free_individual_address(self, project_id: str, line_id: int) -> int:
        """The lowest unused device octet (1-255) across all segments of the line."""
        state = self._state(project_id)
        if state.session.get(Line, line_id) is None:
            raise KeyError(f"No line with id {line_id}")
        used = {
            octet
            for (octet,) in state.session.query(Device.address)
            .join(Segment, Device.segment_id == Segment.id)
            .filter(Segment.line_id == line_id, Device.address.is_not(None))
        }
        octet = 1
        while octet in used:
            octet += 1
        if octet > 255:
            raise ValueError("no free individual address on this line")
        return octet

    def set_individual_address(
        self, project_id: str, device_id: int, address: str
    ) -> None:
        """Place a device at an ``area.line.device`` address within its installation.

        Resolves the target line by its area/line numbers and uses that line's first segment (the
        segment is a media grouping, not part of the address). Raises if no such line exists."""
        state = self._state(project_id)
        device = state.session.get(Device, device_id)
        if device is None:
            raise KeyError(f"No device with id {device_id}")
        area_no, line_no, octet = parse_ia(address)
        installation_id = device.segment.line.area.installation_id
        line = (
            state.session.query(Line)
            .join(Area, Line.area_id == Area.id)
            .filter(
                Area.installation_id == installation_id,
                Area.address == area_no,
                Line.address == line_no,
            )
            .first()
        )
        if line is None:
            raise KeyError(f"No line {area_no}.{line_no} in this installation")
        self.move_device(
            project_id, device_id, self._first_segment(state, line).id, octet
        )

    # --- internals --------------------------------------------------------

    def _ga_info(self, ga: GroupAddress, style: GroupAddressStyle) -> GroupAddressInfo:
        return GroupAddressInfo(
            id=ga.id,
            address=ga.address,
            text=format_ga(ga.address, style),
            name=ga.name,
            datapoint_type=ga.datapoint_type,
            links=[link.com_object_id for link in ga.links],
        )

    def _register(self, project_id: str, engine: Engine, session: Session) -> None:
        self._projects[project_id] = _Open(engine, session, EventStore(session))

    def _state(self, project_id: str) -> _Open:
        return self._projects[project_id]

    def _installation(self, state: _Open, index: int) -> Installation:
        inst = state.session.query(Installation).filter_by(index=index).first()
        if inst is None:
            raise KeyError(f"No installation with index {index}")
        return inst

    def _style(self, state: _Open) -> GroupAddressStyle:
        project = state.session.query(Project).first()
        assert project is not None
        return GroupAddressStyle(project.group_address_style)

    def _compose_ia(self, device: Device) -> str | None:
        if device.address is None:
            return None
        line = device.segment.line
        return format_ia(line.area.address, line.address, device.address)

    def _first_segment(self, state: _Open, line: Line) -> Segment:
        segment = (
            state.session.query(Segment)
            .filter_by(line_id=line.id)
            .order_by(Segment.id)
            .first()
        )
        if segment is None:
            raise KeyError(f"Line {line.id} has no segment")
        return segment

    def _check_unique_address(
        self,
        state: _Open,
        segment_id: int,
        address: int,
        exclude: int | None = None,
    ) -> None:
        segment = state.session.get(Segment, segment_id)
        if segment is None:
            raise KeyError(f"No segment with id {segment_id}")
        query = (
            state.session.query(Device)
            .join(Segment, Device.segment_id == Segment.id)
            .filter(Segment.line_id == segment.line_id, Device.address == address)
        )
        if exclude is not None:
            query = query.filter(Device.id != exclude)
        clash = query.first()
        if clash is not None:
            raise ValueError(
                f"Individual address {address} already used on this line by device {clash.id}"
            )
