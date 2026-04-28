import re

from xknx.models.generated import v10, v11, v12, v13, v14, v20, v21, v22, v23

__version__ = "0.1.0"

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

__all__ = [
    "SUPPORTED_VERSIONS",
    "VERSION_MODULES",
    "VERSION_NAMESPACES",
    "VERSION_PATTERN",
    "v10",
    "v11",
    "v12",
    "v13",
    "v14",
    "v20",
    "v21",
    "v22",
    "v23",
]
