"""Engine and storage helpers for a project's SQLite document.

A project *is* an on-disk SQLite file. There is no global engine and no in-memory mode: callers
create one with :func:`make_engine` and own its lifetime (:class:`ProjectService` keeps one per open
project). :func:`url_for` turns a project path into the SQLAlchemy URL.
"""

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from xknxmono.project.models import Base


def url_for(path: Path) -> str:
    """The SQLAlchemy URL for a project stored at ``path``."""
    return f"sqlite:///{path}"


def make_engine(url: str) -> Engine:
    """Create a configured SQLAlchemy engine (SQLite pragmas + auto-created schema). The caller owns it."""
    engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_pragmas(dbapi_conn: Any, _: Any) -> None:  # pyright: ignore[reportUnusedFunction]
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=DELETE")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    return engine
