"""xknx-catalog: SQLite catalog for KNX hardware, with an optional HTTP API layer.

This package provides two layers:

**Library layer** — pure Python core operations, no FastAPI required::

  from sqlalchemy.orm import Session
  from xknxmono.catalog import get_engine, upload_knxprod, HardwareFilters, list_hardware
  from pathlib import Path

  upload_knxprod(Path("device.knxprod").read_bytes(), dest_dir=Path("data/knxprod"))

  with Session(get_engine()) as db:
      results = list_hardware(db, HardwareFilters(manufacturer_id=["M-0001"]))

**HTTP layer** — a FastAPI application serving the same data over REST::

  from xknxmono.catalog.http import app  # ASGI app for mounting
  # or run the server directly:
  # xknxcatalog
"""

from xknxmono.catalog.core import (
    CatalogSectionNode,
    HardwareFilters,
    build_catalog_tree,
    collect_section_ids,
    get_application_detail,
    get_application_xml,
    get_hardware,
    get_hardware_program,
    get_manufacturer,
    list_catalog_sections,
    list_hardware,
    list_manufacturers,
    upload_knxprod,
)
from xknxmono.catalog.db import get_db, get_db_url, get_engine, get_knxprod_dir

__all__ = [
    "CatalogSectionNode",
    "HardwareFilters",
    "build_catalog_tree",
    "collect_section_ids",
    "get_application_detail",
    "get_application_xml",
    "get_db",
    "get_db_url",
    "get_engine",
    "get_hardware",
    "get_hardware_program",
    "get_knxprod_dir",
    "get_manufacturer",
    "list_catalog_sections",
    "list_hardware",
    "list_manufacturers",
    "upload_knxprod",
]
