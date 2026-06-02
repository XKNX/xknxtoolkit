"""Catalog service backed by the shared `xknxmono.catalog` package.

The on-disk catalog (SQLite + stored .knxprod files) and all ingestion/query logic live in
`xknxmono.catalog`; this service owns the engine for the GUI's catalog file and is a thin, caching
adapter over the package. Entries are `ApplicationSummary` rows; selected applications are returned
as IR-backed product `Application` objects.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from xknxmono.catalog import (
    ApplicationSummary,
    get_application_detail_by_id,
    knxprod_dir_for,
    list_applications,
    make_engine,
    upload_knxprod,
)
from xknxmono.product import Application


class CatalogService:
    def __init__(self, catalog_path: Path) -> None:
        self._engine = make_engine(f"sqlite:///{catalog_path}")
        self._knxprod_dir = knxprod_dir_for(catalog_path)
        self._entries: list[ApplicationSummary] | None = None

    def get_entries(self) -> list[ApplicationSummary]:
        if self._entries is None:
            with Session(self._engine) as db:
                self._entries = list_applications(db)
        return self._entries

    def import_knxprod(self, path: Path) -> list[str]:
        """Ingest a .knxprod into the catalog; returns the application ids newly added."""
        before = {e.application_id for e in self.get_entries()}
        upload_knxprod(path.read_bytes(), self._knxprod_dir, self._engine)
        self._entries = None
        after = {e.application_id for e in self.get_entries()}
        return sorted(after - before)

    def get_application(self, application_id: str) -> Application | None:
        with Session(self._engine) as db:
            return get_application_detail_by_id(db, application_id)

    def refresh(self) -> None:
        self._entries = None
