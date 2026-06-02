"""Core catalog operations — database queries and ingestion — with no FastAPI dependency.

These functions operate directly on a SQLAlchemy :class:`~sqlalchemy.orm.Session`
and return ORM model instances or plain dataclasses. They can be used from any
Python context (scripts, GUI applications, tests) without starting an HTTP server.

Example::

  from pathlib import Path
  from sqlalchemy.orm import Session
  from xknxmono.catalog.db import make_engine, knxprod_dir_for
  from xknxmono.catalog.core import HardwareFilters, list_hardware, upload_knxprod

  engine = make_engine("sqlite:///catalog.db")
  upload_knxprod(Path("device.knxprod").read_bytes(), knxprod_dir_for(Path("catalog.db")), engine)

  with Session(engine) as db:
      results = list_hardware(db, HardwareFilters(manufacturer_id=["M-0001"], limit=10))
      for hw in results:
          print(hw.name, hw.order_number)
"""

from xknxmono.catalog.core.applications import (
    ApplicationSummary,
    get_application_detail_by_id,
    list_applications,
)
from xknxmono.catalog.core.catalog_sections import (
    CatalogSectionNode,
    build_catalog_tree,
    collect_section_ids,
    list_catalog_sections,
)
from xknxmono.catalog.core.hardware import (
    HardwareFilters,
    get_application_detail,
    get_application_xml,
    get_hardware,
    get_hardware_program,
    list_hardware,
)
from xknxmono.catalog.core.manufacturers import get_manufacturer, list_manufacturers
from xknxmono.catalog.core.upload import upload_knxprod

__all__ = [
    "ApplicationSummary",
    "CatalogSectionNode",
    "HardwareFilters",
    "build_catalog_tree",
    "collect_section_ids",
    "get_application_detail",
    "get_application_detail_by_id",
    "get_application_xml",
    "get_hardware",
    "get_hardware_program",
    "get_manufacturer",
    "list_applications",
    "list_catalog_sections",
    "list_hardware",
    "list_manufacturers",
    "upload_knxprod",
]
