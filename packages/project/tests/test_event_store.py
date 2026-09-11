"""Unit test for EventStore.undo()'s defensive "row vanished underneath us" branch -
unreachable through ProjectService's public API (nothing ever deletes an event row), so
this drives EventStore directly against a real SQLite-backed session and deletes the row
out from under a pending undo to force the condition.

redo()'s equivalent branch (session.get() returning None for a row session.execute()
just found) can't be forced the same way: deleting that row also removes it from the
query redo() runs first (id > cursor AND reverted == True), so the "no event to redo"
branch fires instead - left uncovered, same reasoning as encode.py/knx_id.py/events.py's
similarly unreachable defensive branches."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from xknxmono.project.core.event_store import EventStore
from xknxmono.project.core.events import RenameArea
from xknxmono.project.db import make_engine, url_for
from xknxmono.project.models import Area, Installation
from xknxmono.project.models import Event as EventModel


def _store_with_one_event(db_path: Path) -> tuple[EventStore, Session, int]:
    engine = make_engine(url_for(db_path))
    session = Session(engine)
    inst = Installation(index=0, name="I")
    session.add(inst)
    session.flush()
    area = Area(installation_id=inst.id, address=1, name="A")
    session.add(area)
    session.flush()
    session.commit()

    store = EventStore(session)
    store.append(RenameArea(area_id=area.id, name="New"))
    return store, session, area.id


def test_undo_returns_false_when_event_row_is_gone(tmp_path: Path) -> None:
    store, session, _area_id = _store_with_one_event(tmp_path / "p.xknx")
    session.execute(delete(EventModel).where(EventModel.id == store.cursor))
    session.commit()
    session.expire_all()

    assert store.undo() is False
