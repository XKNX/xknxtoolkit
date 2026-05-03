from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from xknx.models import detect_version, load_xml, serialize_xml

if TYPE_CHECKING:
    from xknx.product.archive import ProductArchive


def load_archive(archive: ProductArchive, manufacturer_id: str) -> ProductData:
    master_xml = archive.get_master_xml()
    version = detect_version(master_xml)

    master = load_xml(master_xml, version)
    catalog = load_xml(archive.get_catalog_xml(manufacturer_id), version)
    hardware = load_xml(archive.get_hardware_xml(manufacturer_id), version)
    applications = [load_xml(app_xml, version) for app_xml in archive.get_application_xmls(manufacturer_id).values()]

    return ProductData(
        version=version,
        master=master,
        catalog=catalog,
        hardware=hardware,
        applications=applications,
    )


@dataclass(slots=True)
class ProductData:
    version: str
    master: Any
    catalog: Any
    hardware: Any
    applications: list[Any]

    @classmethod
    def from_archive(cls, archive: ProductArchive, manufacturer_id: str) -> ProductData:
        return load_archive(archive, manufacturer_id)

    def to_master_xml(self) -> bytes:
        return serialize_xml(self.master, self.version)

    def to_catalog_xml(self) -> bytes:
        return serialize_xml(self.catalog, self.version)

    def to_hardware_xml(self) -> bytes:
        return serialize_xml(self.hardware, self.version)
