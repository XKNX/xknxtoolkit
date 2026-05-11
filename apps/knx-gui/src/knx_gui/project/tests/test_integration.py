from pathlib import Path

import pytest

from knx_gui.project.database import ProjectDatabase
from knx_gui.project.events import (
    ComObjectFlagChanged,
    DeviceAdded,
    DeviceRemoved,
    LinkCreated,
    LinkRemoved,
    ParameterChanged,
)
from knx_gui.project.models import (
    ComObjectModel,
    DeviceModel,
    LinkModel,
    ParameterModel,
)


@pytest.fixture
def tmp_project_path(tmp_path: Path) -> Path:
    return tmp_path / "test_project.xknx"


@pytest.fixture
def project(tmp_project_path: Path):
    db = ProjectDatabase(tmp_project_path)
    db.create()
    yield db
    db.close()


class TestFullWorkflow:
    def test_add_device_change_param_undo_redo(self, project: ProjectDatabase):
        add_device = DeviceAdded(
            device_id=1,
            address="1.1.1",
            template_id="template_1",
            name="Test Device",
            parameters=[("brightness", "50"), ("timeout", "10")],
            com_objects=[
                {
                    "co_id": "switch",
                    "dpt_major": 1,
                    "dpt_minor": 1,
                    "flag_communication": True,
                    "flag_write": True,
                },
            ],
        )
        project.event_store.append(add_device)

        device = project.session.get(DeviceModel, 1)
        assert device is not None
        assert device.name == "Test Device"

        change_param = ParameterChanged(
            device_id=1,
            param_id="brightness",
            old_value="50",
            new_value="100",
        )
        project.event_store.append(change_param)

        param = (
            project.session.query(ParameterModel)
            .filter_by(device_id=1, param_id="brightness")
            .first()
        )
        assert param is not None
        assert param.value == "100"

        project.event_store.undo()

        param = (
            project.session.query(ParameterModel)
            .filter_by(device_id=1, param_id="brightness")
            .first()
        )
        assert param is not None
        assert param.value == "50"

        project.event_store.undo()

        assert project.session.get(DeviceModel, 1) is None

        project.event_store.redo()
        project.event_store.redo()

        device = project.session.get(DeviceModel, 1)
        assert device is not None
        param = (
            project.session.query(ParameterModel)
            .filter_by(device_id=1, param_id="brightness")
            .first()
        )
        assert param is not None
        assert param.value == "100"

    def test_link_creation_and_removal(self, project: ProjectDatabase):
        device1 = DeviceAdded(
            device_id=1,
            template_id="t1",
            name="Device 1",
            com_objects=[{"co_id": "output", "dpt_major": 1, "dpt_minor": 1}],
        )
        device2 = DeviceAdded(
            device_id=2,
            template_id="t2",
            name="Device 2",
            com_objects=[{"co_id": "input", "dpt_major": 1, "dpt_minor": 1}],
        )
        project.event_store.append(device1)
        project.event_store.append(device2)

        create_link = LinkCreated(link_id=1, start_pin=100, end_pin=200)
        project.event_store.append(create_link)

        assert project.session.get(LinkModel, 1) is not None

        remove_link = LinkRemoved(link_id=1, start_pin=100, end_pin=200)
        project.event_store.append(remove_link)

        assert project.session.get(LinkModel, 1) is None

        project.event_store.undo()
        assert project.session.get(LinkModel, 1) is not None

        project.event_store.undo()
        assert project.session.get(LinkModel, 1) is None

    def test_flag_changes_tracked(self, project: ProjectDatabase):
        device = DeviceAdded(
            device_id=1,
            template_id="t1",
            name="Device",
            com_objects=[
                {
                    "co_id": "switch",
                    "dpt_major": 1,
                    "dpt_minor": 1,
                    "flag_read": False,
                    "flag_write": False,
                }
            ],
        )
        project.event_store.append(device)

        flag_change = ComObjectFlagChanged(
            device_id=1,
            co_id="switch",
            flag_name="write",
            old_value=False,
            new_value=True,
        )
        project.event_store.append(flag_change)

        com_obj = (
            project.session.query(ComObjectModel)
            .filter_by(device_id=1, co_id="switch")
            .first()
        )
        assert com_obj is not None
        assert com_obj.flag_write is True

        project.event_store.undo()

        project.session.refresh(com_obj)
        assert com_obj.flag_write is False


class TestPersistenceAcrossReopen:
    def test_state_persisted_across_close_and_open(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()

        device = DeviceAdded(
            device_id=1,
            address="1.1.1",
            template_id="t1",
            name="Persistent Device",
            parameters=[("p1", "val1")],
        )
        db.event_store.append(device)

        link = LinkCreated(link_id=1, start_pin=100, end_pin=200)
        db.event_store.append(link)

        db.close()

        db2 = ProjectDatabase(tmp_project_path)
        db2.open()

        loaded_device = db2.session.get(DeviceModel, 1)
        assert loaded_device is not None
        assert loaded_device.name == "Persistent Device"
        assert loaded_device.address == "1.1.1"

        loaded_link = db2.session.get(LinkModel, 1)
        assert loaded_link is not None
        assert loaded_link.start_pin == 100

        params = db2.session.query(ParameterModel).filter_by(device_id=1).all()
        assert len(params) == 1
        assert params[0].param_id == "p1"
        assert params[0].value == "val1"

        db2.close()


class TestUndoRedoStackSurvivesReopen:
    def test_undo_available_after_reopen(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()

        device = DeviceAdded(device_id=1, template_id="t1", name="Device")
        db.event_store.append(device)

        assert db.event_store.can_undo() is True
        db.close()

        db2 = ProjectDatabase(tmp_project_path)
        db2.open()

        assert db2.event_store.can_undo() is True
        assert db2.session.get(DeviceModel, 1) is not None

        db2.event_store.undo()
        assert db2.session.get(DeviceModel, 1) is None

        db2.close()

    def test_redo_available_after_reopen(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()

        device = DeviceAdded(device_id=1, template_id="t1", name="Device")
        db.event_store.append(device)
        db.event_store.undo()

        assert db.event_store.can_redo() is True
        assert db.session.get(DeviceModel, 1) is None
        db.close()

        db2 = ProjectDatabase(tmp_project_path)
        db2.open()

        assert db2.event_store.can_redo() is True
        db2.event_store.redo()
        assert db2.session.get(DeviceModel, 1) is not None

        db2.close()


class TestComplexUndoRedoScenarios:
    def test_new_action_clears_redo_after_undo(self, project: ProjectDatabase):
        device1 = DeviceAdded(device_id=1, template_id="t1", name="D1")
        device2 = DeviceAdded(device_id=2, template_id="t2", name="D2")
        project.event_store.append(device1)
        project.event_store.append(device2)

        project.event_store.undo()
        assert project.event_store.can_redo() is True

        device3 = DeviceAdded(device_id=3, template_id="t3", name="D3")
        project.event_store.append(device3)

        assert project.event_store.can_redo() is False

        assert project.session.get(DeviceModel, 1) is not None
        assert project.session.get(DeviceModel, 2) is None
        assert project.session.get(DeviceModel, 3) is not None

    def test_device_removal_and_undo_restores_all_data(self, project: ProjectDatabase):
        device = DeviceAdded(
            device_id=1,
            address="1.1.1",
            template_id="t1",
            name="Full Device",
            parameters=[("p1", "v1"), ("p2", "v2")],
            com_objects=[
                {"co_id": "co1", "dpt_major": 1, "dpt_minor": 1, "flag_read": True},
                {"co_id": "co2", "dpt_major": 5, "dpt_minor": 1, "flag_write": True},
            ],
        )
        project.event_store.append(device)

        params = project.session.query(ParameterModel).filter_by(device_id=1).all()
        cos = project.session.query(ComObjectModel).filter_by(device_id=1).all()
        param_data = [(p.param_id, p.value) for p in params]
        co_data = [
            {
                "co_id": co.co_id,
                "dpt_major": co.dpt_major,
                "dpt_minor": co.dpt_minor,
                "flag_communication": co.flag_communication,
                "flag_read": co.flag_read,
                "flag_write": co.flag_write,
                "flag_transmit": co.flag_transmit,
                "flag_update": co.flag_update,
            }
            for co in cos
        ]

        remove = DeviceRemoved(
            device_id=1,
            address="1.1.1",
            template_id="t1",
            name="Full Device",
            parameters=param_data,
            com_objects=co_data,
        )
        project.event_store.append(remove)

        assert project.session.get(DeviceModel, 1) is None
        assert project.session.query(ParameterModel).filter_by(device_id=1).count() == 0
        assert project.session.query(ComObjectModel).filter_by(device_id=1).count() == 0

        project.event_store.undo()

        restored = project.session.get(DeviceModel, 1)
        assert restored is not None
        assert restored.name == "Full Device"

        restored_params = (
            project.session.query(ParameterModel).filter_by(device_id=1).all()
        )
        assert len(restored_params) == 2

        restored_cos = (
            project.session.query(ComObjectModel).filter_by(device_id=1).all()
        )
        assert len(restored_cos) == 2
