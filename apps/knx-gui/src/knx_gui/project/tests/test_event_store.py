import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from knx_gui.project.event_store import EventStore
from knx_gui.project.events import DeviceAdded, LinkCreated, ParameterChanged
from knx_gui.project.models import (
    Base,
    DeviceModel,
    EventModel,
    LinkModel,
    ParameterModel,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def event_store(session: Session):
    return EventStore(session)


class TestEventStoreAppend:
    def test_append_applies_and_persists_event(
        self, session: Session, event_store: EventStore
    ):
        event = DeviceAdded(
            device_id=1,
            template_id="t1",
            name="Test Device",
        )
        event_store.append(event)

        device = session.get(DeviceModel, 1)
        assert device is not None
        assert device.name == "Test Device"

        events = session.execute(select(EventModel)).scalars().all()
        assert len(events) == 1
        assert events[0].type == "DeviceAdded"
        assert events[0].reverted is False

    def test_append_sets_event_id(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        assert event.id is None

        event_store.append(event)

        assert event.id is not None
        assert event.id > 0

    def test_append_clears_redo_stack(self, session: Session, event_store: EventStore):
        event1 = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event2 = DeviceAdded(device_id=2, template_id="t2", name="D2")
        event_store.append(event1)
        event_store.append(event2)

        event_store.undo()

        assert session.get(DeviceModel, 2) is None
        assert event_store.can_redo() is True

        event3 = DeviceAdded(device_id=3, template_id="t3", name="D3")
        event_store.append(event3)

        assert event_store.can_redo() is False

        events = session.execute(select(EventModel)).scalars().all()
        assert len(events) == 2
        assert events[0].type == "DeviceAdded"
        assert events[1].data["device_id"] == 3


class TestEventStoreUndo:
    def test_undo_reverts_last_event(self, session: Session, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)

        assert session.get(DeviceModel, 1) is not None

        result = event_store.undo()

        assert result is True
        assert session.get(DeviceModel, 1) is None

    def test_undo_marks_event_as_reverted(
        self, session: Session, event_store: EventStore
    ):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)
        event_id = event.id

        event_store.undo()

        event_model = session.get(EventModel, event_id)
        assert event_model is not None
        assert event_model.reverted is True

    def test_undo_at_start_returns_false(self, event_store: EventStore):
        result = event_store.undo()
        assert result is False

    def test_undo_moves_cursor_back(self, event_store: EventStore):
        event1 = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event2 = DeviceAdded(device_id=2, template_id="t2", name="D2")
        event_store.append(event1)
        event_store.append(event2)

        assert event_store.cursor == event2.id

        event_store.undo()

        assert event_store.cursor == event1.id


class TestEventStoreRedo:
    def test_redo_reapplies_reverted_event(
        self, session: Session, event_store: EventStore
    ):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)
        event_store.undo()

        assert session.get(DeviceModel, 1) is None

        result = event_store.redo()

        assert result is True
        assert session.get(DeviceModel, 1) is not None

    def test_redo_at_end_returns_false(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)

        result = event_store.redo()

        assert result is False

    def test_redo_moves_cursor_forward(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)
        event_id = event.id
        event_store.undo()

        assert event_store.cursor == 0

        event_store.redo()

        assert event_store.cursor == event_id


class TestEventStoreCanUndo:
    def test_can_undo_false_when_empty(self, event_store: EventStore):
        assert event_store.can_undo() is False

    def test_can_undo_true_after_append(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)

        assert event_store.can_undo() is True

    def test_can_undo_false_after_undoing_all(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)
        event_store.undo()

        assert event_store.can_undo() is False


class TestEventStoreCanRedo:
    def test_can_redo_false_when_empty(self, event_store: EventStore):
        assert event_store.can_redo() is False

    def test_can_redo_false_at_end(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)

        assert event_store.can_redo() is False

    def test_can_redo_true_after_undo(self, event_store: EventStore):
        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        event_store.append(event)
        event_store.undo()

        assert event_store.can_redo() is True


class TestEventStoreMultipleOperations:
    def test_multiple_undo_redo_sequence(
        self, session: Session, event_store: EventStore
    ):
        event2 = ParameterChanged(
            device_id=1, param_id="p1", old_value="old", new_value="new"
        )
        event3 = LinkCreated(link_id=1, start_pin=100, end_pin=200)

        device = DeviceModel(id=1, template_id="t1", name="D1")
        param = ParameterModel(device=device, param_id="p1", value="old")
        session.add_all([device, param])
        session.commit()

        event_store.append(event2)
        event_store.append(event3)

        param = (
            session.query(ParameterModel).filter_by(device_id=1, param_id="p1").first()
        )
        assert param is not None
        assert param.value == "new"
        assert session.get(LinkModel, 1) is not None

        event_store.undo()

        assert session.get(LinkModel, 1) is None
        param = (
            session.query(ParameterModel).filter_by(device_id=1, param_id="p1").first()
        )
        assert param is not None
        assert param.value == "new"

        event_store.undo()

        param = (
            session.query(ParameterModel).filter_by(device_id=1, param_id="p1").first()
        )
        assert param is not None
        assert param.value == "old"

        event_store.redo()

        param = (
            session.query(ParameterModel).filter_by(device_id=1, param_id="p1").first()
        )
        assert param is not None
        assert param.value == "new"

        event_store.redo()

        assert session.get(LinkModel, 1) is not None

    def test_cursor_initialization_with_existing_events(self, session: Session):
        from datetime import UTC, datetime

        event_model = EventModel(
            type="DeviceAdded",
            data={"device_id": 1, "template_id": "t1", "name": "D1"},
            timestamp=datetime.now(UTC),
            reverted=False,
        )
        session.add(event_model)
        session.commit()

        event_store = EventStore(session)

        assert event_store.cursor == event_model.id
        assert event_store.can_undo() is True
