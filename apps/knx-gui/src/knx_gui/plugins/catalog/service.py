"""GUI-facing catalog adapter over the shared `xknxmono.catalog` package.

The package's :class:`~xknxmono.catalog.CatalogService` owns the database (engine + .knxprod store)
and all catalog logic. This wrapper adds the bits the GUI needs on top: an entries cache (the panel
re-reads them every frame), path-based import, and reporting which applications were newly added.
"""

from pathlib import Path

from xknxmono.catalog import ApplicationSummary
from xknxmono.catalog import CatalogService as _CatalogService
from xknxmono.product import Application


class CatalogService:
    def __init__(self, catalog_path: Path) -> None:
        self._service = _CatalogService(catalog_path)
        self._entries: list[ApplicationSummary] | None = None

    def get_entries(self) -> list[ApplicationSummary]:
        if self._entries is None:
            self._entries = self._service.list_applications()
        return self._entries

    def import_knxprod(self, path: Path) -> list[str]:
        """Ingest a .knxprod into the catalog; returns the application ids newly added."""
        before = {e.application_id for e in self.get_entries()}
        self._service.import_knxprod(path.read_bytes())
        self._entries = None
        after = {e.application_id for e in self.get_entries()}
        return sorted(after - before)

    def get_application(self, application_id: str) -> Application | None:
        return self._service.get_application(application_id)

    def refresh(self) -> None:
        self._entries = None
