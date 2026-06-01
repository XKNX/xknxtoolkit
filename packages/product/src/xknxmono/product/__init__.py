from __future__ import annotations

from typing import TYPE_CHECKING

__version__ = "0.1.0"

from .application import (
    ComObject,
    ComObjectFlags,
    DeviceApplication,
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
    EnumOption,
    Parameter,
    ParamType,
    ParamTypeKind,
)
from .parser import parse_application_xml, parse_archive

if TYPE_CHECKING:
    from .protocols import LoadProcedures

from .models import AbsoluteSegment, Code, MemoryType, RelativeSegment

__all__ = [
    "AbsoluteSegment",
    "Code",
    "ComObject",
    "ComObjectFlags",
    "DeviceApplication",
    "DynamicChoose",
    "DynamicElement",
    "DynamicWhen",
    "EnumOption",
    "LoadProcedures",
    "MemoryType",
    "ParamType",
    "ParamTypeKind",
    "Parameter",
    "RelativeSegment",
    "parse_application_xml",
    "parse_archive",
]
