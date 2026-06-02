"""xknx-catalog: SQLite catalog for KNX hardware, with an optional HTTP API layer.

This package provides two layers:

**Library layer** — pure Python core operations, no FastAPI required. The caller owns the engine::

  from pathlib import Path
  from sqlalchemy.orm import Session
  from xknxmono.catalog import make_engine, knxprod_dir_for, upload_knxprod, HardwareFilters, list_hardware

  engine = make_engine("sqlite:///catalog.db")
  upload_knxprod(Path("device.knxprod").read_bytes(), knxprod_dir_for(Path("catalog.db")), engine)

  with Session(engine) as db:
      results = list_hardware(db, HardwareFilters(manufacturer_id=["M-0001"]))

**HTTP layer** — a FastAPI application serving the same data over REST::

  from xknxmono.catalog.http import app  # ASGI app for mounting
  # or run the server directly:
  # xknxcatalog
"""

from xknxmono.catalog.core import (
    ApplicationSummary,
    CatalogSectionNode,
    CatalogService,
    HardwareFilters,
    build_catalog_tree,
    collect_section_ids,
    get_application_detail,
    get_application_detail_by_id,
    get_application_xml,
    get_hardware,
    get_hardware_program,
    get_manufacturer,
    list_applications,
    list_catalog_sections,
    list_hardware,
    list_manufacturers,
    upload_knxprod,
)
from xknxmono.catalog.db import default_db_url, knxprod_dir_for, make_engine

__all__ = [
    "ApplicationSummary",
    "CatalogSectionNode",
    "CatalogService",
    "HardwareFilters",
    "build_catalog_tree",
    "collect_section_ids",
    "default_db_url",
    "get_application_detail",
    "get_application_detail_by_id",
    "get_application_xml",
    "get_hardware",
    "get_hardware_program",
    "get_manufacturer",
    "knxprod_dir_for",
    "list_applications",
    "list_catalog_sections",
    "list_hardware",
    "list_manufacturers",
    "make_engine",
    "upload_knxprod",
]
