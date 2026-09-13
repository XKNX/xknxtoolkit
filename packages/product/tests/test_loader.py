"""Unit tests for loader.load() - builds minimal in-memory .knxprod archives with
zipfile/io.BytesIO, no fixture files needed."""

from __future__ import annotations

import io
import zipfile

import pytest

from xknxmono.product.errors import ArchiveError
from xknxmono.product.loader import load

_MFR = "M-0008"

_MASTER_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23"></KNX>'
)

_CATALOG_XML = f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Catalog />
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _hardware_xml(app_ref_id: str | None) -> bytes:
    ref = f'<ApplicationProgramRef RefId="{app_ref_id}" />' if app_ref_id else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Hardware>
        <Hardware Id="{_MFR}_H-1" Name="Test" SerialNumber="1" VersionNumber="0"
                  HasIndividualAddress="true" HasApplicationProgram="true">
          <Hardware2Programs>
            <Hardware2Program Id="{_MFR}_H-1_HP-1">
              {ref}
            </Hardware2Program>
          </Hardware2Programs>
        </Hardware>
      </Hardware>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _application_xml(app_id: str) -> bytes:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <ApplicationPrograms>
        <ApplicationProgram Id="{app_id}" Name="Test" ApplicationNumber="1"
                             ApplicationVersion="1" ProgramType="ApplicationProgram"
                             MaskVersion="MASK0001" LoadProcedureStyle="DefaultProcedure"
                             PeiType="0" DefaultLanguage="en-US"
                             DynamicTableManagement="false" Linkable="false">
          <Static>
            <Code />
          </Static>
        </ApplicationProgram>
      </ApplicationPrograms>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _zip_bytes(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_load_raises_when_program_references_unbundled_application() -> None:
    archive_bytes = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml("M-0008_A-NOT-BUNDLED"),
        }
    )
    with pytest.raises(ArchiveError, match="M-0008_A-NOT-BUNDLED"):
        load(archive_bytes)


def test_load_succeeds_when_referenced_application_is_bundled() -> None:
    app_id = f"{_MFR}_A-1"
    archive_bytes = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml(app_id),
            f"{_MFR}/{app_id}.xml": _application_xml(app_id),
        }
    )
    registry = load(archive_bytes)
    assert registry.program_to_application[f"{_MFR}_H-1_HP-1"] == [app_id]


def test_load_skips_program_to_application_edge_when_no_refs() -> None:
    archive_bytes = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml(None),
        }
    )
    registry = load(archive_bytes)
    assert f"{_MFR}_H-1_HP-1" not in registry.program_to_application
