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

from xknxmono.project.core.event_store import EventStore
from xknxmono.project.core.events import (
    AddDevice,
    AddInstallation,
    CreateArea,
    CreateGroupAddress,
    CreateLine,
    LinkComObject,
    SetParameter,
)
from xknxmono.project.core.skeleton import MEDIUM_TP, seed_new_project
from xknxmono.project.db import make_engine, url_for
from xknxmono.project.models import (
    Device,
    GroupAddress,
    Installation,
    Project,
    Segment,
)


@dataclass
class _Open:
    engine: Engine
    session: Session
    store: EventStore


class ProjectService:
    def __init__(self) -> None:
        self._projects: dict[str, _Open] = {}

    # --- lifecycle --------------------------------------------------------

    def create(self, path: Path | str, project_id: str | None = None) -> str:
        pid = project_id or f"P-{uuid4().hex[:8].upper()}"
        engine = make_engine(url_for(Path(path)))
        session = Session(engine)
        seed_new_project(session, pid, "New project")
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
        event = CreateGroupAddress(
            installation_id=self._installation(state, installation).id,
            address=address,
            name=name,
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

    # --- undo / redo ------------------------------------------------------

    def undo(self, project_id: str) -> bool:
        return self._state(project_id).store.undo()

    def redo(self, project_id: str) -> bool:
        return self._state(project_id).store.redo()

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

    def group_addresses(self, project_id: str) -> list[GroupAddress]:
        return (
            self._state(project_id)
            .session.query(GroupAddress)
            .order_by(GroupAddress.id)
            .all()
        )

    # --- internals --------------------------------------------------------

    def _register(self, project_id: str, engine: Engine, session: Session) -> None:
        self._projects[project_id] = _Open(engine, session, EventStore(session))

    def _state(self, project_id: str) -> _Open:
        return self._projects[project_id]

    def _installation(self, state: _Open, index: int) -> Installation:
        inst = state.session.query(Installation).filter_by(index=index).first()
        if inst is None:
            raise KeyError(f"No installation with index {index}")
        return inst

    def _check_unique_address(
        self, state: _Open, segment_id: int, address: int
    ) -> None:
        segment = state.session.get(Segment, segment_id)
        if segment is None:
            raise KeyError(f"No segment with id {segment_id}")
        clash = (
            state.session.query(Device)
            .join(Segment, Device.segment_id == Segment.id)
            .filter(Segment.line_id == segment.line_id, Device.address == address)
            .first()
        )
        if clash is not None:
            raise ValueError(
                f"Individual address {address} already used on this line by device {clash.id}"
            )
