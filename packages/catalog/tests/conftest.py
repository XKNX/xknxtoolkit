"""Shared fixtures and in-memory ``.knxprod`` builders for catalog-package tests.

``packages/catalog`` had no tests before this commit; the builders below reuse the
zipfile technique from ``packages/product/tests/test_loader.py`` so the catalog's
ingestion path can be exercised without any fixture files. The templates carry
just enough schema-required attributes for the IR parser to accept them, and a
``<Hardware>`` may carry several ``<Product>`` children (the schema-permitted
multi-SKU case this package finally handles correctly).
"""

from __future__ import annotations

import io
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
from sqlalchemy.engine import Engine

_MFR = "M-0008"

_MASTER_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23"></KNX>'
)


@dataclass(frozen=True, slots=True)
class ProductSpec:
    """A ``<Product>`` SKU's attributes the test builder writes into Hardware.xml."""

    id: str
    name: str
    order_number: str
    is_rail_mounted: bool = False
    width_mm: float | None = None
    visible_description: str | None = None
    default_language: str | None = None


@dataclass(frozen=True, slots=True)
class CatalogItemSpec:
    """A ``<CatalogItem>``'s attributes the test builder writes into Catalog.xml."""

    id: str
    name: str
    number: int
    product_ref_id: str
    hardware2_program_ref_id: str | None = None


def _product_xml(p: ProductSpec) -> str:
    attrs = [
        f'Id="{p.id}"',
        f'Text="{p.name}"',
        f'OrderNumber="{p.order_number}"',
        f'IsRailMounted="{"true" if p.is_rail_mounted else "false"}"',
    ]
    if p.width_mm is not None:
        attrs.append(f'WidthInMillimeter="{p.width_mm:g}"')
    if p.visible_description is not None:
        attrs.append(f'VisibleDescription="{p.visible_description}"')
    if p.default_language is not None:
        attrs.append(f'DefaultLanguage="{p.default_language}"')
    return f"<Product {' '.join(attrs)} />"


def _hardware_xml(
    hardware_id: str,
    hardware_name: str,
    products: list[ProductSpec],
    program_id: str,
    app_ref_id: str | None,
) -> bytes:
    products_xml = (
        f"<Products>{''.join(_product_xml(p) for p in products)}</Products>"
        if products
        else ""
    )
    ref = f'<ApplicationProgramRef RefId="{app_ref_id}" />' if app_ref_id else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Hardware>
        <Hardware Id="{hardware_id}" Name="{hardware_name}" SerialNumber="1" VersionNumber="0"
                  HasIndividualAddress="true" HasApplicationProgram="true">
          {products_xml}
          <Hardware2Programs>
            <Hardware2Program Id="{program_id}">
              {ref}
            </Hardware2Program>
          </Hardware2Programs>
        </Hardware>
      </Hardware>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _catalog_xml(section_id: str, items: list[CatalogItemSpec]) -> bytes:
    items_xml = "".join(
        f'<CatalogItem Id="{it.id}" Name="{it.name}" Number="{it.number}" '
        f'ProductRefId="{it.product_ref_id}"'
        + (
            f' Hardware2ProgramRefId="{it.hardware2_program_ref_id}"'
            if it.hardware2_program_ref_id
            else ""
        )
        + " />"
        for it in items
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Catalog>
        <CatalogSection Id="{section_id}" Name="Test" Number="1">
          {items_xml}
        </CatalogSection>
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def build_knxprod_bytes(
    products: list[ProductSpec],
    catalog_items: list[CatalogItemSpec] | None = None,
    *,
    hardware_id: str = "M-0008_H-1",
    hardware_name: str = "Test Hardware",
    program_id: str = "M-0008_H-1_HP-1",
    section_id: str = "M-0008_CS-1",
    app_ref_id: str | None = None,
    app_xml: bytes | None = None,
) -> bytes:
    """Build a minimal in-memory ``.knxprod`` ZIP.

    The hardware (``M-0008_H-1`` by default) carries the given product SKUs and a
    single ``Hardware2Program`` (``M-0008_H-1_HP-1`` by default); the catalog has
    one top-level section with the given items. When ``app_ref_id`` is set, the
    program references it and the supplied ``app_xml`` is bundled too (otherwise
    the program has no application ref and ingests with ``application_id=None``).
    """
    entries: dict[str, bytes] = {
        "knx_master.xml": _MASTER_XML,
        f"{_MFR}/Hardware.xml": _hardware_xml(
            hardware_id, hardware_name, products, program_id, app_ref_id
        ),
        f"{_MFR}/Catalog.xml": _catalog_xml(section_id, catalog_items or []),
    }
    if app_ref_id is not None and app_xml is not None:
        entries[f"{_MFR}/{app_ref_id}.xml"] = app_xml
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


@pytest.fixture
def catalog_engine(tmp_path: Path) -> Iterator[Engine]:
    """A fresh SQLite engine (backed by a per-test file) with the catalog schema created."""
    from xknxmono.catalog.db import make_engine

    engine = make_engine(f"sqlite:///{tmp_path / 'test_catalog.db'}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def knxprod_dir(tmp_path: Path) -> Path:
    """A clean per-test directory where ``upload_knxprod`` writes the stored file."""
    dest = tmp_path / "knxprod"
    dest.mkdir(parents=True, exist_ok=True)
    return dest
