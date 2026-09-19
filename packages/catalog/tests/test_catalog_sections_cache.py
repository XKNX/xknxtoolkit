"""Tests for the catalog-sections HTTP router cache and its invalidation after uploads.

These tests exercise the real router functions (``list_catalog_sections_endpoint`` and
``upload_knxprod``) through FastAPI's :class:`~fastapi.testclient.TestClient` against a
throwaway SQLite database. They cover the stale-cache defect where a successful
``.knxprod`` upload (which upserts ``CatalogSection`` rows the cached trees were built
from) was not reflected in subsequent ``GET /manufacturers/{id}/catalog-sections``
responses, because the module-level cache was populated on first miss and never
invalidated.

Since fabricating a second *valid* ``.knxprod`` archive (a strictly-validated zip+XML
format) is impractical, the end-to-end test drives the exact write path that
``_ingest_catalog`` uses (``session.merge(CatalogSection(...))`` + ``session.commit``)
and then triggers invalidation through the upload router itself — re-uploading the
same fixture short-circuits the DB write (same SHA3-256 content hash) but still runs
the post-upload cache invalidation, which is the code path under test.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from xknxmono.catalog.core.service import CatalogService
from xknxmono.catalog.http.deps import get_service
from xknxmono.catalog.http.routers import catalog_sections, upload
from xknxmono.catalog.models import CatalogSection

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "product"
    / "tests"
    / "fixtures"
    / "gira_2gang_button_interface.knxprod"
)
MFR = "M-0008"


@pytest.fixture
def service(tmp_path: Path) -> CatalogService:
    """A :class:`CatalogService` backed by a fresh temp SQLite DB (and its own .knxprod store)."""
    return CatalogService(tmp_path / "catalog.db")


@pytest.fixture
def client(service: CatalogService) -> Iterator[TestClient]:
    """A :class:`TestClient` wired to a minimal app exposing only the catalog-sections and
    upload routers, with the service dependency overridden so requests hit the temp-DB service
    (and no real lifespan/default DB is touched)."""
    app = FastAPI()
    app.include_router(catalog_sections.router)
    app.include_router(upload.router)
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _isolate_cache() -> Iterator[None]:
    """Ensure the module-level catalog-sections cache never leaks state between tests."""
    catalog_sections._cache.clear()
    yield
    catalog_sections._cache.clear()


def _post_fixture(client: TestClient, content: bytes, filename: str = "gira.knxprod"):
    """Upload ``content`` as a ``.knxprod`` file and return the response."""
    return client.post(
        "/upload", files={"file": (filename, content, "application/octet-stream")}
    )


def test_first_get_populates_cache_and_is_stable(client: TestClient):
    """Regression: the cache still works — the first GET populates the module-level cache
    and a second GET returns the identical (cached) tree without a DB round-trip."""
    _post_fixture(client, FIXTURE.read_bytes())
    first = client.get(f"/manufacturers/{MFR}/catalog-sections").json()
    assert MFR in catalog_sections._cache
    second = client.get(f"/manufacturers/{MFR}/catalog-sections").json()
    assert second == first
    assert MFR in catalog_sections._cache


def test_successful_upload_clears_cache(client: TestClient):
    """The fix: a successful upload invalidates the catalog-sections cache, even when the
    upload itself short-circuits (duplicate content) and writes nothing to the DB."""
    content = FIXTURE.read_bytes()
    _post_fixture(client, content)
    client.get(f"/manufacturers/{MFR}/catalog-sections")  # populate the cache
    assert MFR in catalog_sections._cache

    _post_fixture(client, content)  # short-circuits the DB write, but still invalidates
    assert MFR not in catalog_sections._cache


def test_failed_upload_preserves_cache(client: TestClient):
    """A failed upload (corrupt archive -> ``ArchiveError`` -> 422) must NOT invalidate the
    cache: the DB was not mutated, so any previously-cached tree remains valid."""
    content = FIXTURE.read_bytes()
    _post_fixture(client, content)
    client.get(f"/manufacturers/{MFR}/catalog-sections")  # populate the cache
    assert MFR in catalog_sections._cache

    bad = _post_fixture(client, b"not a zip archive", filename="corrupt.knxprod")
    assert bad.status_code == 422
    assert MFR in catalog_sections._cache  # cache untouched on the failing path


def test_upload_then_get_reflects_db_changes(
    client: TestClient, service: CatalogService
):
    """End-to-end reproduction of the staleness bug, now fixed.

    After a manufacturer's tree is cached, its underlying ``CatalogSection`` rows are changed
    (the exact ``session.merge`` + ``commit`` operation ``_ingest_catalog`` performs for a new
    section). Without invalidation the next GET would serve the stale pre-change tree; with the
    fix, a subsequent upload clears the cache and the GET returns the refreshed tree.
    """
    content = FIXTURE.read_bytes()
    _post_fixture(client, content)
    first = client.get(f"/manufacturers/{MFR}/catalog-sections")
    assert [node["id"] for node in first.json()] == ["M-0008_CS-IN"]

    # Simulate a *different* upload that adds a new top-level section for M-0008 —
    # the precise operation _ingest_catalog performs via session.merge + session.commit.
    with Session(service._engine) as session:
        session.merge(
            CatalogSection(
                id="M-0008_CS-NEW",
                manufacturer_id=MFR,
                parent_id=None,
                name="New Section",
                number="new",
            )
        )
        session.commit()

    # The DB now reflects the new section (sanity: the write path changed the data).
    assert {node.id for node in service.catalog_tree(MFR)} == {
        "M-0008_CS-IN",
        "M-0008_CS-NEW",
    }

    # Re-uploading the same fixture short-circuits the DB write but runs invalidation.
    _post_fixture(client, content)

    refreshed = client.get(f"/manufacturers/{MFR}/catalog-sections").json()
    assert {node["id"] for node in refreshed} == {"M-0008_CS-IN", "M-0008_CS-NEW"}


def test_invalidate_cache_helper_clears_module_state():
    """Unit test for the invalidation primitive: it drops every cached manufacturer tree."""
    catalog_sections._cache["M-0001"] = []
    catalog_sections._cache["M-0002"] = []
    assert catalog_sections._cache

    catalog_sections.invalidate_cache()

    assert catalog_sections._cache == {}
