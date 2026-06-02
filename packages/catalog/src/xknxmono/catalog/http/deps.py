"""FastAPI dependencies for the catalog HTTP layer.

Sessions are created from the engine the application owns (``app.state.engine``, set up in the
lifespan handler in :mod:`xknxmono.catalog.http.app`) — there is no global engine.
"""

from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    """Yield a session bound to the application's engine, closing it after the request."""
    with Session(request.app.state.engine) as session:
        yield session
