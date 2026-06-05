"""The undo/redo history over a project's ``Session``.

A cursor tracks the highest non-reverted event; ``undo``/``redo`` flip the ``reverted`` flag and
walk the cursor (no rows are deleted), so the history is fully re-playable and survives reopen.
``append`` truncates any redo branch, applies the event, and persists it.
"""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from xknxmono.project.core.events import Event, deserialize_event
from xknxmono.project.models import Event as EventModel


class EventStore:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._cursor = self._calculate_cursor()

    def _calculate_cursor(self) -> int:
        row = self._session.execute(
            select(EventModel.id)
            .where(EventModel.reverted == False)  # noqa: E712
            .order_by(EventModel.id.desc())
            .limit(1)
        ).scalar()
        return row if row is not None else 0

    def append(self, event: Event) -> Event:
        if self._cursor > 0:
            self._session.execute(
                delete(EventModel).where(EventModel.id > self._cursor)
            )

        event.apply(self._session)

        model = EventModel(
            type=event.event_type,
            data=event.to_dict(),
            timestamp=datetime.now(UTC),
            reverted=False,
        )
        self._session.add(model)
        self._session.commit()

        self._cursor = model.id
        return event

    def undo(self) -> bool:
        if not self.can_undo():
            return False

        model = self._session.get(EventModel, self._cursor)
        if model is None:
            return False

        deserialize_event(model.type, model.data).revert(self._session)
        model.reverted = True
        self._session.commit()

        prev = self._session.execute(
            select(EventModel.id)
            .where(EventModel.id < self._cursor)
            .where(EventModel.reverted == False)  # noqa: E712
            .order_by(EventModel.id.desc())
            .limit(1)
        ).scalar()
        self._cursor = prev if prev is not None else 0
        return True

    def redo(self) -> bool:
        next_id = self._session.execute(
            select(EventModel.id)
            .where(EventModel.id > self._cursor)
            .where(EventModel.reverted == True)  # noqa: E712
            .order_by(EventModel.id.asc())
            .limit(1)
        ).scalar()
        if next_id is None:
            return False

        model = self._session.get(EventModel, next_id)
        if model is None:
            return False

        deserialize_event(model.type, model.data).apply(self._session)
        model.reverted = False
        self._session.commit()

        self._cursor = model.id
        return True

    def can_undo(self) -> bool:
        return self._cursor > 0

    def can_redo(self) -> bool:
        return (
            self._session.execute(
                select(EventModel.id)
                .where(EventModel.id > self._cursor)
                .where(EventModel.reverted == True)  # noqa: E712
                .limit(1)
            ).scalar()
            is not None
        )

    def jump_to(self, target_id: int) -> None:
        while self._cursor > target_id and self.can_undo():
            self.undo()
        while self._cursor < target_id and self.can_redo():
            self.redo()

    @property
    def cursor(self) -> int:
        return self._cursor
