from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from knx_gui.catalog.models import Base


class CatalogDatabase:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._engine = create_engine(f"sqlite:///{path}")
        self._session_factory = sessionmaker(bind=self._engine)
        self._session: Session | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Database not open")
        return self._session

    def create(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(self._engine)
        self._session = self._session_factory()
        self._stamp_head()

    def open(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Catalog not found: {self._path}")
        self._run_migrations()
        self._session = self._session_factory()

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def _get_alembic_config(self) -> Config:
        migrations_dir = Path(__file__).parent / "migrations"
        config = Config()
        config.set_main_option("script_location", str(migrations_dir))
        config.set_main_option("sqlalchemy.url", f"sqlite:///{self._path}")
        return config

    def _run_migrations(self) -> None:
        config = self._get_alembic_config()
        command.upgrade(config, "head")

    def _stamp_head(self) -> None:
        config = self._get_alembic_config()
        command.stamp(config, "head")
