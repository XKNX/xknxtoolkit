from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from knx_gui.project.events import Event, deserialize_event
from knx_gui.project.models import EventModel


class EventStore:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._cursor = self._calculate_cursor()

    def _calculate_cursor(self) -> int:
        result = self._session.execute(
            select(EventModel.id)
            .where(EventModel.reverted == False)  # noqa: E712
            .order_by(EventModel.id.desc())
            .limit(1)
        )
        row = result.scalar()
        return row if row is not None else 0

    def append(self, event: Event) -> None:
        if self._cursor > 0:
            self._session.execute(
                delete(EventModel).where(EventModel.id > self._cursor)
            )

        event.apply(self._session)

        event_model = EventModel(
            type=event.event_type,
            data=event.to_dict(),
            timestamp=event.timestamp or datetime.now(UTC),
            reverted=False,
        )
        self._session.add(event_model)
        self._session.commit()

        event.id = event_model.id
        self._cursor = event_model.id

    def undo(self) -> bool:
        if not self.can_undo():
            return False

        event_model = self._session.get(EventModel, self._cursor)
        if event_model is None:
            return False

        event = deserialize_event(event_model.type, event_model.data)
        event.id = event_model.id
        event.revert(self._session)

        event_model.reverted = True
        self._session.commit()

        prev_result = self._session.execute(
            select(EventModel.id)
            .where(EventModel.id < self._cursor)
            .where(EventModel.reverted == False)  # noqa: E712
            .order_by(EventModel.id.desc())
            .limit(1)
        )
        prev_id = prev_result.scalar()
        self._cursor = prev_id if prev_id is not None else 0

        return True

    def redo(self) -> bool:
        if not self.can_redo():
            return False

        next_result = self._session.execute(
            select(EventModel.id)
            .where(EventModel.id > self._cursor)
            .where(EventModel.reverted == True)  # noqa: E712
            .order_by(EventModel.id.asc())
            .limit(1)
        )
        next_id = next_result.scalar()
        if next_id is None:
            return False

        event_model = self._session.get(EventModel, next_id)
        if event_model is None:
            return False

        event = deserialize_event(event_model.type, event_model.data)
        event.id = event_model.id
        event.apply(self._session)

        event_model.reverted = False
        self._session.commit()

        self._cursor = event_model.id

        return True

    def can_undo(self) -> bool:
        return self._cursor > 0

    def can_redo(self) -> bool:
        result = self._session.execute(
            select(EventModel.id)
            .where(EventModel.id > self._cursor)
            .where(EventModel.reverted == True)  # noqa: E712
            .limit(1)
        )
        return result.scalar() is not None

    @property
    def cursor(self) -> int:
        return self._cursor
