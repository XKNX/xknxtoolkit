import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from knx_gui.project.events import (
    ComObjectDptChanged,
    ComObjectFlagChanged,
    DeviceAdded,
    DeviceAddressChanged,
    DeviceRemoved,
    LinkCreated,
    LinkRemoved,
    ParameterChanged,
    deserialize_event,
)
from knx_gui.project.models import (
    Base,
    ComObjectModel,
    DeviceModel,
    LinkModel,
    ParameterModel,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestDeviceAdded:
    def test_apply_creates_device(self, session: Session):
        event = DeviceAdded(
            device_id=1,
            address="1.1.1",
            template_id="t1",
            name="Test Device",
            parameters=[("p1", "100"), ("p2", "200")],
            com_objects=[
                {"co_id": "co1", "dpt_major": 1, "dpt_minor": 1, "flag_read": True},
                {"co_id": "co2", "dpt_major": 5, "dpt_minor": 1},
            ],
        )
        event.apply(session)
        session.commit()

        device = session.get(DeviceModel, 1)
        assert device is not None
        assert device.name == "Test Device"
        assert device.address == "1.1.1"
        assert len(device.parameters) == 2
        assert len(device.com_objects) == 2

    def test_revert_removes_device(self, session: Session):
        event = DeviceAdded(
            device_id=2,
            template_id="t2",
            name="Device to Remove",
        )
        event.apply(session)
        session.commit()

        assert session.get(DeviceModel, 2) is not None

        event.revert(session)
        session.commit()

        assert session.get(DeviceModel, 2) is None


class TestDeviceRemoved:
    def test_apply_removes_device(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        session.add(device)
        session.commit()

        event = DeviceRemoved(device_id=1, template_id="t1", name="D1")
        event.apply(session)
        session.commit()

        assert session.get(DeviceModel, 1) is None

    def test_revert_restores_device(self, session: Session):
        event = DeviceRemoved(
            device_id=2,
            address="1.1.2",
            template_id="t2",
            name="Restored Device",
            parameters=[("p1", "val1")],
            com_objects=[{"co_id": "co1", "dpt_major": 1, "dpt_minor": 1}],
        )
        event.revert(session)
        session.commit()

        device = session.get(DeviceModel, 2)
        assert device is not None
        assert device.name == "Restored Device"
        assert len(device.parameters) == 1
        assert len(device.com_objects) == 1


class TestDeviceAddressChanged:
    def test_apply_updates_address(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1", address="1.1.1")
        session.add(device)
        session.commit()

        event = DeviceAddressChanged(
            device_id=1, old_address="1.1.1", new_address="1.1.2"
        )
        event.apply(session)
        session.commit()

        device = session.get(DeviceModel, 1)
        assert device is not None
        assert device.address == "1.1.2"

    def test_revert_restores_address(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2", address="2.2.2")
        session.add(device)
        session.commit()

        event = DeviceAddressChanged(
            device_id=2, old_address="2.2.1", new_address="2.2.2"
        )
        event.revert(session)
        session.commit()

        device = session.get(DeviceModel, 2)
        assert device is not None
        assert device.address == "2.2.1"


class TestParameterChanged:
    def test_apply_updates_value(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        param = ParameterModel(device=device, param_id="p1", value="old_value")
        session.add_all([device, param])
        session.commit()

        event = ParameterChanged(
            device_id=1, param_id="p1", old_value="old_value", new_value="new_value"
        )
        event.apply(session)
        session.commit()

        param = (
            session.query(ParameterModel).filter_by(device_id=1, param_id="p1").first()
        )
        assert param is not None
        assert param.value == "new_value"

    def test_revert_restores_old_value(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2")
        param = ParameterModel(device=device, param_id="p2", value="new_value")
        session.add_all([device, param])
        session.commit()

        event = ParameterChanged(
            device_id=2, param_id="p2", old_value="old_value", new_value="new_value"
        )
        event.revert(session)
        session.commit()

        param = (
            session.query(ParameterModel).filter_by(device_id=2, param_id="p2").first()
        )
        assert param is not None
        assert param.value == "old_value"


class TestComObjectDptChanged:
    def test_apply_updates_dpt(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        com_obj = ComObjectModel(device=device, co_id="co1", dpt_major=1, dpt_minor=1)
        session.add_all([device, com_obj])
        session.commit()

        event = ComObjectDptChanged(
            device_id=1,
            co_id="co1",
            old_dpt_major=1,
            old_dpt_minor=1,
            new_dpt_major=5,
            new_dpt_minor=1,
        )
        event.apply(session)
        session.commit()

        com_obj = (
            session.query(ComObjectModel).filter_by(device_id=1, co_id="co1").first()
        )
        assert com_obj is not None
        assert com_obj.dpt_major == 5
        assert com_obj.dpt_minor == 1

    def test_revert_restores_dpt(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2")
        com_obj = ComObjectModel(device=device, co_id="co2", dpt_major=5, dpt_minor=1)
        session.add_all([device, com_obj])
        session.commit()

        event = ComObjectDptChanged(
            device_id=2,
            co_id="co2",
            old_dpt_major=1,
            old_dpt_minor=1,
            new_dpt_major=5,
            new_dpt_minor=1,
        )
        event.revert(session)
        session.commit()

        com_obj = (
            session.query(ComObjectModel).filter_by(device_id=2, co_id="co2").first()
        )
        assert com_obj is not None
        assert com_obj.dpt_major == 1
        assert com_obj.dpt_minor == 1


class TestComObjectFlagChanged:
    def test_apply_updates_flag(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        com_obj = ComObjectModel(
            device=device, co_id="co1", dpt_major=1, dpt_minor=1, flag_write=False
        )
        session.add_all([device, com_obj])
        session.commit()

        event = ComObjectFlagChanged(
            device_id=1, co_id="co1", flag_name="write", old_value=False, new_value=True
        )
        event.apply(session)
        session.commit()

        com_obj = (
            session.query(ComObjectModel).filter_by(device_id=1, co_id="co1").first()
        )
        assert com_obj is not None
        assert com_obj.flag_write is True

    def test_revert_restores_flag(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2")
        com_obj = ComObjectModel(
            device=device, co_id="co2", dpt_major=1, dpt_minor=1, flag_read=True
        )
        session.add_all([device, com_obj])
        session.commit()

        event = ComObjectFlagChanged(
            device_id=2, co_id="co2", flag_name="read", old_value=False, new_value=True
        )
        event.revert(session)
        session.commit()

        com_obj = (
            session.query(ComObjectModel).filter_by(device_id=2, co_id="co2").first()
        )
        assert com_obj is not None
        assert com_obj.flag_read is False


class TestLinkCreated:
    def test_apply_creates_link(self, session: Session):
        event = LinkCreated(link_id=1, start_pin=100, end_pin=200)
        event.apply(session)
        session.commit()

        link = session.get(LinkModel, 1)
        assert link is not None
        assert link.start_pin == 100
        assert link.end_pin == 200

    def test_revert_removes_link(self, session: Session):
        event = LinkCreated(link_id=2, start_pin=101, end_pin=201)
        event.apply(session)
        session.commit()

        event.revert(session)
        session.commit()

        assert session.get(LinkModel, 2) is None


class TestLinkRemoved:
    def test_apply_removes_link(self, session: Session):
        link = LinkModel(id=1, start_pin=100, end_pin=200)
        session.add(link)
        session.commit()

        event = LinkRemoved(link_id=1, start_pin=100, end_pin=200)
        event.apply(session)
        session.commit()

        assert session.get(LinkModel, 1) is None

    def test_revert_restores_link(self, session: Session):
        event = LinkRemoved(link_id=2, start_pin=101, end_pin=201)
        event.revert(session)
        session.commit()

        link = session.get(LinkModel, 2)
        assert link is not None
        assert link.start_pin == 101
        assert link.end_pin == 201


class TestEventSerialization:
    def test_device_added_roundtrip(self):
        original = DeviceAdded(
            device_id=1,
            address="1.1.1",
            template_id="t1",
            name="Test",
            parameters=[("p1", "v1")],
            com_objects=[{"co_id": "co1", "dpt_major": 1, "dpt_minor": 1}],
        )
        data = original.to_dict()
        restored = DeviceAdded.from_dict(data)

        assert restored.device_id == original.device_id
        assert restored.address == original.address
        assert restored.template_id == original.template_id
        assert restored.name == original.name
        assert restored.parameters == original.parameters
        assert restored.com_objects == original.com_objects

    def test_parameter_changed_roundtrip(self):
        original = ParameterChanged(
            device_id=1, param_id="p1", old_value="old", new_value="new"
        )
        data = original.to_dict()
        restored = ParameterChanged.from_dict(data)

        assert restored.device_id == original.device_id
        assert restored.param_id == original.param_id
        assert restored.old_value == original.old_value
        assert restored.new_value == original.new_value

    def test_link_created_roundtrip(self):
        original = LinkCreated(link_id=1, start_pin=100, end_pin=200)
        data = original.to_dict()
        restored = LinkCreated.from_dict(data)

        assert restored.link_id == original.link_id
        assert restored.start_pin == original.start_pin
        assert restored.end_pin == original.end_pin

    def test_deserialize_event(self):
        data = {"device_id": 1, "param_id": "p1", "old_value": "a", "new_value": "b"}
        event = deserialize_event("ParameterChanged", data)

        assert isinstance(event, ParameterChanged)
        assert event.device_id == 1
        assert event.param_id == "p1"

    def test_deserialize_unknown_event_raises(self):
        with pytest.raises(ValueError, match="Unknown event type"):
            deserialize_event("UnknownEvent", {})
