from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from knx_gui.project.event_store import EventStore
from knx_gui.project.models import Base

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


class ProjectDatabase:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._engine = None
        self._session_factory = None
        self._session: Session | None = None
        self._event_store: EventStore | None = None

    def create(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(f"sqlite:///{self._path}")
        Base.metadata.create_all(self._engine)
        self._stamp_head()
        self._session_factory = sessionmaker(bind=self._engine)
        self._session = self._session_factory()
        self._event_store = EventStore(self._session)

    def open(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Project file not found: {self._path}")
        self._engine = create_engine(f"sqlite:///{self._path}")
        self._run_migrations()
        self._session_factory = sessionmaker(bind=self._engine)
        self._session = self._session_factory()
        self._event_store = EventStore(self._session)

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None
        if self._engine:
            self._engine.dispose()
            self._engine = None
        self._event_store = None
        self._session_factory = None

    def _get_alembic_config(self) -> Config:
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", str(MIGRATIONS_DIR))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{self._path}")
        return alembic_cfg

    def _stamp_head(self) -> None:
        command.stamp(self._get_alembic_config(), "head")

    def _run_migrations(self) -> None:
        command.upgrade(self._get_alembic_config(), "head")

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Database not open")
        return self._session

    @property
    def event_store(self) -> EventStore:
        if self._event_store is None:
            raise RuntimeError("Database not open")
        return self._event_store

    @property
    def path(self) -> Path:
        return self._path
