"""GUI-facing catalog adapter over the shared `xknxmono.catalog` package.

The package's :class:`~xknxmono.catalog.CatalogService` owns the database (engine + .knxprod store)
and all catalog logic. This wrapper adds the bits the GUI needs on top: an entries cache (the panel
re-reads them every frame), path-based import, and reporting which applications were newly added.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING

from knx_gui.concurrency import io_guarded

if TYPE_CHECKING:
    from knx_gui.plugins.catalog.online_catalog import OnlineManufacturer
    from xknxmono.catalog import ProductSummary
    from xknxmono.product import Application


class CatalogService:
    def __init__(
        self, catalog_path: Path, io_lock: threading.RLock | None = None
    ) -> None:
        from knx_gui.plugins.catalog.online_catalog import OnlineCatalogClient
        from xknxmono.catalog import CatalogService as _CatalogService

        self._service = _CatalogService(catalog_path)
        self._products: list[ProductSummary] | None = None
        # Shared with the project service so a background import can hold both while it writes.
        self._io_lock = io_lock or threading.RLock()
        # Manufacturer list from the KNX online catalog service (cached next to the db).
        self._online_client = OnlineCatalogClient(catalog_path.parent)

    def online_manufacturers(self) -> list[OnlineManufacturer] | None:
        """The cached online manufacturer list, or None when the cache is empty.

        Never touches the network: the panel reads this every frame."""
        return self._online_client.cached_manufacturers()

    def refresh_online_manufacturers(self) -> list[OnlineManufacturer]:
        """Download the manufacturer list now; raises OnlineCatalogError on failure."""
        return self._online_client.refresh_manufacturers()

    @property
    def io_lock(self) -> threading.RLock:
        """The re-entrant lock a background import holds while writing catalog + project data."""
        return self._io_lock

    @io_guarded(list)
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

    @io_guarded(lambda: None)
    def get_application(self, application_id: str) -> Application | None:
        return self._service.get_application(application_id)

    @io_guarded(lambda: None)
    def get_program_source(self, program_id: str) -> tuple[str, str] | None:
        """Return ``(knxprod_path, manufacturer_id)`` for a hardware program id, or ``None``."""
        return self._service.get_program_source(program_id)

    def refresh(self) -> None:
        self._products = None
