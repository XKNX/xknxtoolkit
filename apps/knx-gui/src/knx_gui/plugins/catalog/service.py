from dataclasses import dataclass
from pathlib import Path

from knx_gui.plugins.catalog.db import (
    ApplicationModel,
    CatalogDatabase,
    get_application_xml,
    load_knxprod_to_catalog,
)


@dataclass
class CatalogEntry:
    application_id: str
    manufacturer_id: str
    manufacturer_name: str
    name: str


class CatalogService:
    def __init__(self, catalog: CatalogDatabase) -> None:
        self._catalog = catalog
        self._entries: list[CatalogEntry] | None = None

    @property
    def session(self):
        return self._catalog.session

    def get_entries(self) -> list[CatalogEntry]:
        if self._entries is not None:
            return self._entries
        entries: list[CatalogEntry] = []
        for app in self._catalog.session.query(ApplicationModel).all():
            entries.append(
                CatalogEntry(
                    application_id=app.application_id,
                    manufacturer_id=app.manufacturer_id,
                    manufacturer_name=app.manufacturer_name,
                    name=app.name,
                )
            )
        self._entries = entries
        return entries

    def import_knxprod(self, path: Path) -> list[str]:
        added = load_knxprod_to_catalog(self._catalog, path)
        if added:
            self._entries = None
        return added

    def get_application_xml(self, application_id: str) -> bytes | None:
        return get_application_xml(self._catalog, application_id)

    def refresh(self) -> None:
        self._entries = None
