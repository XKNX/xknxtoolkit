from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from knx_gui.project.models import (
    Base,
    ComObjectModel,
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


class TestEventModel:
    def test_create_event(self, session: Session):
        event = EventModel(
            type="DeviceAdded",
            data={"device_id": 1, "name": "Test"},
            timestamp=datetime.now(UTC),
            reverted=False,
        )
        session.add(event)
        session.commit()

        loaded = session.get(EventModel, event.id)
        assert loaded is not None
        assert loaded.type == "DeviceAdded"
        assert loaded.data == {"device_id": 1, "name": "Test"}
        assert loaded.reverted is False

    def test_update_event_reverted(self, session: Session):
        event = EventModel(
            type="DeviceAdded",
            data={},
            timestamp=datetime.now(UTC),
            reverted=False,
        )
        session.add(event)
        session.commit()

        event.reverted = True
        session.commit()

        loaded = session.get(EventModel, event.id)
        assert loaded is not None
        assert loaded.reverted is True

    def test_delete_event(self, session: Session):
        event = EventModel(
            type="DeviceAdded",
            data={},
            timestamp=datetime.now(UTC),
        )
        session.add(event)
        session.commit()
        event_id = event.id

        session.delete(event)
        session.commit()

        assert session.get(EventModel, event_id) is None


class TestDeviceModel:
    def test_create_device(self, session: Session):
        device = DeviceModel(
            id=1,
            address="1.1.1",
            template_id="template_123",
            name="Test Device",
        )
        session.add(device)
        session.commit()

        loaded = session.get(DeviceModel, 1)
        assert loaded is not None
        assert loaded.address == "1.1.1"
        assert loaded.template_id == "template_123"
        assert loaded.name == "Test Device"

    def test_device_without_address(self, session: Session):
        device = DeviceModel(
            id=2,
            address=None,
            template_id="template_456",
            name="Unaddressed Device",
        )
        session.add(device)
        session.commit()

        loaded = session.get(DeviceModel, 2)
        assert loaded is not None
        assert loaded.address is None

    def test_delete_device_cascades(self, session: Session):
        device = DeviceModel(
            id=3,
            template_id="template_789",
            name="Device with relations",
        )
        param = ParameterModel(device=device, param_id="p1", value="100")
        com_obj = ComObjectModel(
            device=device,
            co_id="co1",
            dpt_major=1,
            dpt_minor=1,
        )
        session.add_all([device, param, com_obj])
        session.commit()

        param_id = param.id
        com_obj_id = com_obj.id

        session.delete(device)
        session.commit()

        assert session.get(DeviceModel, 3) is None
        assert session.get(ParameterModel, param_id) is None
        assert session.get(ComObjectModel, com_obj_id) is None


class TestParameterModel:
    def test_create_parameter(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        param = ParameterModel(device=device, param_id="param_1", value="42")
        session.add_all([device, param])
        session.commit()

        loaded = session.get(ParameterModel, param.id)
        assert loaded is not None
        assert loaded.param_id == "param_1"
        assert loaded.value == "42"
        assert loaded.device_id == 1

    def test_update_parameter_value(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2")
        param = ParameterModel(device=device, param_id="param_2", value="old")
        session.add_all([device, param])
        session.commit()

        param.value = "new"
        session.commit()

        loaded = session.get(ParameterModel, param.id)
        assert loaded is not None
        assert loaded.value == "new"


class TestComObjectModel:
    def test_create_com_object(self, session: Session):
        device = DeviceModel(id=1, template_id="t1", name="D1")
        com_obj = ComObjectModel(
            device=device,
            co_id="co_1",
            dpt_major=1,
            dpt_minor=1,
            flag_communication=True,
            flag_read=True,
            flag_write=False,
            flag_transmit=True,
            flag_update=False,
        )
        session.add_all([device, com_obj])
        session.commit()

        loaded = session.get(ComObjectModel, com_obj.id)
        assert loaded is not None
        assert loaded.co_id == "co_1"
        assert loaded.dpt_major == 1
        assert loaded.dpt_minor == 1
        assert loaded.flag_communication is True
        assert loaded.flag_read is True
        assert loaded.flag_write is False
        assert loaded.flag_transmit is True
        assert loaded.flag_update is False

    def test_update_com_object_dpt(self, session: Session):
        device = DeviceModel(id=2, template_id="t2", name="D2")
        com_obj = ComObjectModel(
            device=device,
            co_id="co_2",
            dpt_major=1,
            dpt_minor=1,
        )
        session.add_all([device, com_obj])
        session.commit()

        com_obj.dpt_major = 5
        com_obj.dpt_minor = 1
        session.commit()

        loaded = session.get(ComObjectModel, com_obj.id)
        assert loaded is not None
        assert loaded.dpt_major == 5
        assert loaded.dpt_minor == 1

    def test_update_com_object_flags(self, session: Session):
        device = DeviceModel(id=3, template_id="t3", name="D3")
        com_obj = ComObjectModel(
            device=device,
            co_id="co_3",
            dpt_major=1,
            dpt_minor=1,
            flag_write=False,
        )
        session.add_all([device, com_obj])
        session.commit()

        com_obj.flag_write = True
        session.commit()

        loaded = session.get(ComObjectModel, com_obj.id)
        assert loaded is not None
        assert loaded.flag_write is True


class TestLinkModel:
    def test_create_link(self, session: Session):
        link = LinkModel(id=1, start_pin=100, end_pin=200)
        session.add(link)
        session.commit()

        loaded = session.get(LinkModel, 1)
        assert loaded is not None
        assert loaded.start_pin == 100
        assert loaded.end_pin == 200

    def test_delete_link(self, session: Session):
        link = LinkModel(id=2, start_pin=101, end_pin=201)
        session.add(link)
        session.commit()

        session.delete(link)
        session.commit()

        assert session.get(LinkModel, 2) is None
