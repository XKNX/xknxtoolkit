"""Unit tests for parse_catalog_xml: a manufacturer without a Catalog section is skipped,
and multiple top-level sections (across one or more manufacturers) are all walked."""

from __future__ import annotations

from xknxmono.product.catalog import parse_catalog_xml

_NO_CATALOG_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="M-0008" />
  </ManufacturerData>
</KNX>
"""

_NO_MANUFACTURER_DATA_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
</KNX>
"""

_TWO_TOP_LEVEL_SECTIONS_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="M-0008">
      <Catalog>
        <CatalogSection Id="M-0008_CS-1" Name="Section 1" Number="1" />
        <CatalogSection Id="M-0008_CS-2" Name="Section 2" Number="2" />
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>
"""


def test_no_manufacturer_data_yields_no_sections() -> None:
    doc = parse_catalog_xml(_NO_MANUFACTURER_DATA_XML)
    assert doc.sections == {}


def test_manufacturer_without_catalog_yields_no_sections() -> None:
    doc = parse_catalog_xml(_NO_CATALOG_XML)
    assert doc.sections == {}


def test_multiple_top_level_sections_are_all_walked() -> None:
    doc = parse_catalog_xml(_TWO_TOP_LEVEL_SECTIONS_XML)
    assert doc.sections.keys() == {"M-0008_CS-1", "M-0008_CS-2"}
    assert doc.sections["M-0008_CS-1"].parent_id is None
    assert doc.sections["M-0008_CS-2"].parent_id is None
