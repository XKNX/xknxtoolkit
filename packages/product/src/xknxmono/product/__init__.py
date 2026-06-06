from __future__ import annotations

__version__ = "0.1.0"

from .application import Application, parse_application_xml
from .archive import Archive
from .catalog import CatalogItem, CatalogSection, parse_catalog_xml
from .hardware import DeviceProgram, Hardware, HardwareDoc, Product, parse_hardware_xml
from .loader import load
from .master import MasterData, parse_master_xml
from .parser.com_objects import ComObject, ComObjectFlags
from .parser.dynamic import (
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
    GridCell,
    GridLayout,
    VisibleNode,
)
from .parser.parameters import EnumOption, Parameter, ParamType, ParamTypeKind
from .registry import Registry

__all__ = [
    "Application",
    "Archive",
    "CatalogItem",
    "CatalogSection",
    "ComObject",
    "ComObjectFlags",
    "DeviceProgram",
    "DynamicChoose",
    "DynamicElement",
    "DynamicWhen",
    "EnumOption",
    "GridCell",
    "GridLayout",
    "Hardware",
    "HardwareDoc",
    "MasterData",
    "ParamType",
    "ParamTypeKind",
    "Parameter",
    "Product",
    "Registry",
    "VisibleNode",
    "load",
    "parse_application_xml",
    "parse_catalog_xml",
    "parse_hardware_xml",
    "parse_master_xml",
]
