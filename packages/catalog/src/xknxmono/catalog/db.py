"""Database engine and session management for the catalog SQLite store."""

import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from xknxmono.catalog.models import Base  # noqa: E402

_PACKAGE_DIR = Path(__file__).parents[3]


def get_db_url() -> str:
    """Return the SQLAlchemy database URL from DATABASE_URL env var, falling back to the bundled catalog.db."""
    fallback = _PACKAGE_DIR / "data" / "catalog.db"
    return os.getenv("DATABASE_URL", f"sqlite:///{fallback}")


def get_knxprod_dir() -> Path:
    """Return the directory where uploaded .knxprod files are stored, creating it if necessary."""
    db_path = Path(get_db_url().removeprefix("sqlite:///"))
    dest = db_path.parent / "knxprod"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def _make_engine(url: str):
    """Create and configure a SQLAlchemy engine with SQLite pragmas and auto-created schema."""
    engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_pragmas(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=DELETE")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    return engine


_engine = None


def get_engine():
    """Return the singleton SQLAlchemy engine, creating it on first call."""
    global _engine
    if _engine is None:
        _engine = _make_engine(get_db_url())
    return _engine


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and closes it after the request."""
    with Session(get_engine()) as session:
        yield session
