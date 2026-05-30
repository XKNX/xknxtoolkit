from __future__ import annotations

import re
from typing import Any

from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig

from xknxmono.models.files import v10, v11, v12, v13, v14, v20, v21, v22, v23

SUPPORTED_VERSIONS = frozenset({"10", "11", "12", "13", "14", "20", "21", "22", "23"})

VERSION_PATTERN = re.compile(rb'xmlns="http://knx\.org/xml/project/(\d+)"')

VERSION_MODULES = {
    "10": v10,
    "11": v11,
    "12": v12,
    "13": v13,
    "14": v14,
    "20": v20,
    "21": v21,
    "22": v22,
    "23": v23,
}

VERSION_NAMESPACES = {v: f"http://knx.org/xml/project/{v}" for v in SUPPORTED_VERSIONS}

_parser = XmlParser()
_serializer = XmlSerializer(
    config=SerializerConfig(
        xml_declaration=True,
        encoding="UTF-8",
        indent="  ",
    )
)


class VersionError(Exception):
    pass


def detect_version(xml_bytes: bytes) -> str:
    match = VERSION_PATTERN.search(xml_bytes[:2000])
    if match:
        return match.group(1).decode("ascii")
    raise VersionError("Could not detect KNX namespace version")


def get_model_class(version: str) -> type[Any]:
    if version not in VERSION_MODULES:
        raise VersionError(f"Unsupported KNX version: {version}. Supported: {', '.join(sorted(SUPPORTED_VERSIONS))}")
    return VERSION_MODULES[version].Knx


def load_xml(source: bytes, version: str | None = None) -> Any:
    if version is None:
        version = detect_version(source)
    model_class = get_model_class(version)
    return _parser.from_bytes(source, model_class)


def serialize_xml(obj: object, version: str) -> bytes:
    ns_map = {"": VERSION_NAMESPACES[version]}
    return _serializer.render(obj, ns_map=ns_map).encode("utf-8")  # type: ignore[reportUnknownMemberType]
