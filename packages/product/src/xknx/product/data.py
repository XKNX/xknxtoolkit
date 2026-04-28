from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from xknx.models import (
    SUPPORTED_VERSIONS,
    VERSION_MODULES,
    VERSION_NAMESPACES,
    VERSION_PATTERN,
)
from xknx.product.errors import VersionError

if TYPE_CHECKING:
    from xknx.product.archive import ProductArchive


def detect_version(xml_bytes: bytes) -> str:
    """Detect the KNX schema version from XML bytes."""
    match = VERSION_PATTERN.search(xml_bytes[:2000])
    if match:
        return match.group(1).decode("ascii")
    raise VersionError("Could not detect KNX namespace version")


def get_module_for_version(version: str) -> Any:
    """Return the generated module for a KNX version."""
    if version not in VERSION_MODULES:
        raise VersionError(f"Unsupported KNX version: {version}. Supported: {', '.join(sorted(SUPPORTED_VERSIONS))}")
    return VERSION_MODULES[version]


def _get_parser() -> XmlParser:
    return XmlParser()


def _get_serializer() -> XmlSerializer:
    return XmlSerializer(
        config=SerializerConfig(
            xml_declaration=True,
            encoding="UTF-8",
            indent="  ",
        )
    )


def _render(obj: Any, version: str) -> bytes:
    ns_map = {"": VERSION_NAMESPACES[version]}
    return _get_serializer().render(obj, ns_map=ns_map).encode("utf-8")  # type: ignore[reportUnknownMemberType]


def load_archive(archive: ProductArchive, manufacturer_id: str) -> ProductData:
    """Load and parse product data from an archive for a specific manufacturer."""
    parser = _get_parser()
    master_xml = archive.get_master_xml()
    version = detect_version(master_xml)
    module = get_module_for_version(version)
    model_class = module.Knx

    master = parser.from_bytes(master_xml, model_class)
    catalog = parser.from_bytes(archive.get_catalog_xml(manufacturer_id), model_class)
    hardware = parser.from_bytes(archive.get_hardware_xml(manufacturer_id), model_class)

    applications = [
        parser.from_bytes(app_xml, model_class)
        for app_xml in archive.get_application_xmls(manufacturer_id).values()
    ]

    return ProductData(
        version=version,
        master=master,
        catalog=catalog,
        hardware=hardware,
        applications=applications,
    )


def serialize_master(data: ProductData) -> bytes:
    """Serialize master data to XML bytes."""
    return _render(data.master, data.version)


def serialize_catalog(data: ProductData) -> bytes:
    """Serialize catalog data to XML bytes."""
    return _render(data.catalog, data.version)


def serialize_hardware(data: ProductData) -> bytes:
    """Serialize hardware data to XML bytes."""
    return _render(data.hardware, data.version)


@dataclass(slots=True)
class ProductData:
    """Parsed KNX product data."""

    version: str
    master: Any
    catalog: Any
    hardware: Any
    applications: list[Any]

    @classmethod
    def from_archive(cls, archive: ProductArchive, manufacturer_id: str) -> ProductData:
        """Load product data from an archive for a specific manufacturer."""
        return load_archive(archive, manufacturer_id)

    def to_master_xml(self) -> bytes:
        """Serialize master data to XML bytes."""
        return serialize_master(self)

    def to_catalog_xml(self) -> bytes:
        """Serialize catalog data to XML bytes."""
        return serialize_catalog(self)

    def to_hardware_xml(self) -> bytes:
        """Serialize hardware data to XML bytes."""
        return serialize_hardware(self)
