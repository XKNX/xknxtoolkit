from pathlib import Path

import pytest

from knx_gui.project.database import ProjectDatabase
from knx_gui.project.event_store import EventStore
from knx_gui.project.events import DeviceAdded
from knx_gui.project.models import DeviceModel


@pytest.fixture
def tmp_project_path(tmp_path: Path) -> Path:
    return tmp_path / "test_project.xknx"


class TestProjectDatabaseCreate:
    def test_create_new_project_initializes_schema(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()

        assert tmp_project_path.exists()
        assert db.session is not None
        assert db.event_store is not None

        db.close()

    def test_create_creates_parent_directories(self, tmp_path: Path):
        nested_path = tmp_path / "subdir" / "nested" / "project.xknx"
        db = ProjectDatabase(nested_path)
        db.create()

        assert nested_path.exists()
        db.close()


class TestProjectDatabaseOpen:
    def test_open_existing_project_loads_state(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()
        event = DeviceAdded(device_id=1, template_id="t1", name="Test Device")
        db.event_store.append(event)
        db.close()

        db2 = ProjectDatabase(tmp_project_path)
        db2.open()

        device = db2.session.get(DeviceModel, 1)
        assert device is not None
        assert device.name == "Test Device"
        assert db2.event_store.can_undo() is True

        db2.close()

    def test_open_nonexistent_raises(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)

        with pytest.raises(FileNotFoundError):
            db.open()


class TestProjectDatabaseClose:
    def test_close_releases_resources(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()
        db.close()

        with pytest.raises(RuntimeError):
            _ = db.session

        with pytest.raises(RuntimeError):
            _ = db.event_store


class TestProjectDatabaseEventStore:
    def test_event_store_is_functional(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        db.create()

        assert isinstance(db.event_store, EventStore)

        event = DeviceAdded(device_id=1, template_id="t1", name="D1")
        db.event_store.append(event)

        assert db.session.get(DeviceModel, 1) is not None
        assert db.event_store.can_undo() is True

        db.event_store.undo()
        assert db.session.get(DeviceModel, 1) is None

        db.close()


class TestProjectDatabasePath:
    def test_path_property(self, tmp_project_path: Path):
        db = ProjectDatabase(tmp_project_path)
        assert db.path == tmp_project_path
