"""HTTP-level regression guard for ``GET /hardware`` limit/offset validation.

Before the fix, ``?limit=-1`` returned HTTP 200 with every row in the ``hardware`` table
(SQLite treats a negative ``LIMIT`` as "no limit"). After the fix, out-of-range
``limit``/``offset`` are rejected at the Pydantic query boundary (HTTP 422) and never
reach SQLAlchemy. These tests seed a >200-row catalog and exercise the boundary via the
real FastAPI app (``TestClient``) so the cap and the happy path are both pinned.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from xknxmono.catalog.core.hardware import HardwareFilters
from xknxmono.catalog.core.service import CatalogService
from xknxmono.catalog.db import make_engine
from xknxmono.catalog.http.app import app
from xknxmono.catalog.http.deps import get_service
from xknxmono.catalog.models import Hardware, Manufacturer

# A table larger than the 200 cap, so the cap binds and a missing cap would leak rows.
N_ROWS = 300


def _seed(db_path: Path) -> CatalogService:
    engine = make_engine(f"sqlite:///{db_path}")
    with Session(engine) as db:
        db.add(Manufacturer(id="M-0001", name="Test Manufacturer"))
        db.flush()
        for i in range(N_ROWS):
            db.add(
                Hardware(
                    id=f"M-0001_H_{i:04d}",
                    manufacturer_id="M-0001",
                    name=f"Device {i:04d}",
                    order_number=f"ORD-{i:04d}",
                )
            )
        db.commit()
    engine.dispose()
    return CatalogService(db_path)


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    service = _seed(tmp_path / "catalog.db")
    app.dependency_overrides[get_service] = lambda: service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _is_validation_error_for(resp: httpx.Response, field: str) -> bool:
    if resp.status_code != 422:
        return False
    detail: list[dict[str, Any]] = resp.json().get("detail", [])
    return any(field in loc for err in detail for loc in err.get("loc", []))


def test_default_limit_is_bounded(client: TestClient) -> None:
    r = client.get("/hardware")
    assert r.status_code == 200
    assert len(r.json()) == 50


def test_limit_at_cap_is_bounded(client: TestClient) -> None:
    """``?limit=200`` returns exactly 200 rows even though the table has 300."""
    r = client.get("/hardware?limit=200")
    assert r.status_code == 200
    assert len(r.json()) == 200


def test_limit_negative_one_is_rejected(client: TestClient) -> None:
    """The demonstrated exploit: ``?limit=-1`` must 422, not 200-with-all-rows."""
    r = client.get("/hardware?limit=-1")
    assert _is_validation_error_for(r, "limit")
    assert not isinstance(r.json(), list)


def test_limit_above_cap_is_rejected(client: TestClient) -> None:
    assert _is_validation_error_for(client.get("/hardware?limit=201"), "limit")


def test_offset_negative_is_rejected(client: TestClient) -> None:
    assert _is_validation_error_for(client.get("/hardware?offset=-1"), "offset")


def test_pagination_returns_disjoint_pages(client: TestClient) -> None:
    first = client.get("/hardware?limit=5&offset=0").json()
    second = client.get("/hardware?limit=5&offset=5").json()
    assert len(first) == 5
    assert len(second) == 5
    assert {h["id"] for h in first}.isdisjoint({h["id"] for h in second})


def test_core_cannot_construct_unbounded_filters() -> None:
    """The exploit value can't even be constructed, so it can never reach ``.limit()``."""
    with pytest.raises(ValidationError):
        HardwareFilters(limit=-1)
