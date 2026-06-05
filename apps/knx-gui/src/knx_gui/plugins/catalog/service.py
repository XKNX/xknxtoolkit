"""GUI-facing catalog adapter over the shared `xknxmono.catalog` package.

The package's :class:`~xknxmono.catalog.CatalogService` owns the database (engine + .knxprod store)
and all catalog logic. This wrapper adds the bits the GUI needs on top: an entries cache (the panel
re-reads them every frame), path-based import, and reporting which applications were newly added.
"""

from pathlib import Path

from xknxmono.catalog import CatalogService as _CatalogService
from xknxmono.catalog import ProductSummary
from xknxmono.product import Application


class CatalogService:
    def __init__(self, catalog_path: Path) -> None:
        self._service = _CatalogService(catalog_path)
        self._products: list[ProductSummary] | None = None

    def get_products(self) -> list[ProductSummary]:
        """Product-centric browse entries — each carries the product/program refs add_device needs."""
        if self._products is None:
            self._products = self._service.list_products()
        return self._products

    def import_knxprod(self, path: Path) -> list[str]:
        """Ingest a .knxprod into the catalog; returns the product refs newly added."""
        before = {p.product_ref_id for p in self.get_products()}
        self._service.import_knxprod(path.read_bytes())
        self._products = None
        after = {p.product_ref_id for p in self.get_products()}
        return sorted(after - before)

    def get_application(self, application_id: str) -> Application | None:
        return self._service.get_application(application_id)

    def refresh(self) -> None:
        self._products = None
