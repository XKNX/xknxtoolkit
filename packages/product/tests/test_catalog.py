"""Unit tests for parse_catalog_xml: structural validation (no ManufacturerData /
Catalog section raises, multiple top-level sections are all walked) and the
duplicate-Id guards (duplicate CatalogSection Id / CatalogItem Id raise ParseError,
and a valid nested catalog still parses cleanly)."""

from __future__ import annotations

import pytest

from xknxmono.product.catalog import parse_catalog_xml
from xknxmono.product.errors import ParseError

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


def test_no_manufacturer_data_raises() -> None:
    with pytest.raises(ParseError):
        parse_catalog_xml(_NO_MANUFACTURER_DATA_XML)


def test_manufacturer_without_catalog_raises() -> None:
    with pytest.raises(ParseError, match="M-0008"):
        parse_catalog_xml(_NO_CATALOG_XML)


def test_multiple_top_level_sections_are_all_walked() -> None:
    doc = parse_catalog_xml(_TWO_TOP_LEVEL_SECTIONS_XML)
    assert doc.sections.keys() == {"M-0008_CS-1", "M-0008_CS-2"}
    assert doc.sections["M-0008_CS-1"].parent_id is None
    assert doc.sections["M-0008_CS-2"].parent_id is None


_DUPLICATE_ITEM_ID_ACROSS_SECTIONS_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="M-0008">
      <Catalog>
        <CatalogSection Id="M-0008_CS-A" Name="A" Number="1">
          <CatalogItem Id="M-0008_CI-DUP" Name="first" Number="1"
            ProductRefId="M-0008_P-1" Hardware2ProgramRefId="M-0008_HP-1" />
        </CatalogSection>
        <CatalogSection Id="M-0008_CS-B" Name="B" Number="2">
          <CatalogItem Id="M-0008_CI-DUP" Name="second" Number="2"
            ProductRefId="M-0008_P-2" Hardware2ProgramRefId="M-0008_HP-2" />
        </CatalogSection>
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>
"""

_DUPLICATE_SECTION_ID_TOP_LEVEL_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="M-0008">
      <Catalog>
        <CatalogSection Id="M-0008_CS-X" Name="first" Number="1" />
        <CatalogSection Id="M-0008_CS-X" Name="second" Number="2" />
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>
"""

_VALID_NESTED_CATALOG_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="M-0008">
      <Catalog>
        <CatalogSection Id="M-0008_CS-ROOT" Name="root" Number="1">
          <CatalogItem Id="M-0008_CI-ROOT-1" Name="root item" Number="1"
            ProductRefId="M-0008_P-1" Hardware2ProgramRefId="M-0008_HP-1" />
          <CatalogSection Id="M-0008_CS-CHILD" Name="child" Number="2">
            <CatalogItem Id="M-0008_CI-CHILD-1" Name="child item" Number="1"
              ProductRefId="M-0008_P-2" Hardware2ProgramRefId="M-0008_HP-2" />
          </CatalogSection>
        </CatalogSection>
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>
"""


def test_parse_catalog_xml_rejects_duplicate_catalog_item_id() -> None:
    with pytest.raises(ParseError, match="duplicate CatalogItem Id"):
        parse_catalog_xml(_DUPLICATE_ITEM_ID_ACROSS_SECTIONS_XML)


def test_parse_catalog_xml_duplicate_item_id_error_reports_offending_id() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_catalog_xml(_DUPLICATE_ITEM_ID_ACROSS_SECTIONS_XML)
    assert "M-0008_CI-DUP" in str(exc_info.value)


def test_parse_catalog_xml_rejects_duplicate_catalog_section_id() -> None:
    with pytest.raises(ParseError, match="duplicate CatalogSection Id"):
        parse_catalog_xml(_DUPLICATE_SECTION_ID_TOP_LEVEL_XML)


def test_parse_catalog_xml_duplicate_section_id_error_reports_offending_id() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_catalog_xml(_DUPLICATE_SECTION_ID_TOP_LEVEL_XML)
    assert "M-0008_CS-X" in str(exc_info.value)


def test_parse_catalog_xml_preserves_unique_ids_with_items_and_subsections() -> None:
    doc = parse_catalog_xml(_VALID_NESTED_CATALOG_XML)
    assert doc.sections.keys() == {"M-0008_CS-ROOT", "M-0008_CS-CHILD"}
    assert doc.items.keys() == {"M-0008_CI-ROOT-1", "M-0008_CI-CHILD-1"}
    assert doc.sections["M-0008_CS-ROOT"].parent_id is None
    assert doc.sections["M-0008_CS-CHILD"].parent_id == "M-0008_CS-ROOT"
    assert doc.section_to_subsection["M-0008_CS-ROOT"] == ["M-0008_CS-CHILD"]
    assert doc.section_to_subsection["M-0008_CS-CHILD"] == []
    assert doc.section_to_item["M-0008_CS-ROOT"] == ["M-0008_CI-ROOT-1"]
    assert doc.section_to_item["M-0008_CS-CHILD"] == ["M-0008_CI-CHILD-1"]
    assert doc.items["M-0008_CI-ROOT-1"].product_ref_id == "M-0008_P-1"
    assert doc.items["M-0008_CI-CHILD-1"].product_ref_id == "M-0008_P-2"
