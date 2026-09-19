"""HTTP-level tests for the ``/upload`` router's exception-to-status-code mapping.

Build minimal in-memory ``.knxprod`` archives with ``zipfile``/``io.BytesIO`` (no fixture files
needed) and exercise the real FastAPI app, the real SQLAlchemy engine, and the real on-disk
``.knxprod`` store via ``TestClient`` with a throwaway ``CatalogService``.

The central guarantee: every malformed-archive input — a bad ZIP container (``ArchiveError``),
structurally-valid-ZIP-but-malformed-XML (``ParseError``), or XML lacking a KNX namespace
(``models.schema.VersionError``) — is mapped to HTTP 422, not 500. The router's neighboring
``ArchiveError`` branch establishes that archive-validation failures map to 422; the parser
raises ``ParseError`` and ``models.schema.VersionError`` (a *distinct* class from
``product.errors.VersionError``) for the same conceptual category, so they must land in the same
branch.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from xknxmono.catalog.core.service import CatalogService
from xknxmono.catalog.http.app import app
from xknxmono.catalog.http.deps import get_service
from xknxmono.models.schema import VersionError as SchemaVersionError
from xknxmono.product.errors import VersionError as ProductVersionError

_MFR = "M-0008"

_MASTER_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23"></KNX>'
)

_CATALOG_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23">'
    b'<ManufacturerData><Manufacturer RefId="M-0008"><Catalog /></Manufacturer></ManufacturerData>'
    b"</KNX>"
)


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


def _no_namespace_xml() -> bytes:
    return b'<?xml version="1.0"?><Foo></Foo>'


def _no_manufacturer_data_xml() -> bytes:
    # Valid KNX namespace (detect_version succeeds) but the body has no ManufacturerData,
    # so parse_hardware_xml raises ParseError while Archive._validate_structure passes.
    return b'<?xml version="1.0" encoding="utf-8"?><KNX xmlns="http://knx.org/xml/project/23"></KNX>'


def _valid_archive() -> bytes:
    app_id = f"{_MFR}_A-1"
    return _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml(app_id),
            f"{_MFR}/{app_id}.xml": _application_xml(app_id),
        }
    )


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    """A TestClient wired to a throwaway CatalogService (the package's bundled
    ``data/catalog.db`` is never touched)."""
    service = CatalogService(tmp_path / "catalog.db")
    app.dependency_overrides[get_service] = lambda: service
    client = TestClient(app)
    yield client  # type: ignore[misc]
    app.dependency_overrides.clear()


def _upload(client: TestClient, name: str, content: bytes) -> int:
    return client.post(
        "/upload",
        files={"file": (name, content, "application/octet-stream")},
    ).status_code


def test_two_version_errors_are_distinct_classes() -> None:
    """``models.schema.VersionError`` (raised by ``detect_version`` on the load() path) and
    ``product.errors.VersionError`` are two different classes. Catching the product one would
    NOT cover the no-namespace path — guards against importing the wrong ``VersionError``."""
    assert SchemaVersionError is not ProductVersionError


def test_upload_returns_422_for_parse_error_missing_manufacturer_data(
    client: TestClient,
) -> None:
    """Valid ZIP but Hardware.xml with no ManufacturerData passes Archive structure validation
    (the entry exists) and raises ParseError in the parser -> must be 422, not 500."""
    archive = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _no_manufacturer_data_xml(),
        }
    )
    resp = client.post(
        "/upload",
        files={"file": ("bad.knxprod", archive, "application/octet-stream")},
    )
    assert resp.status_code == 422, (resp.status_code, resp.text)
    assert resp.json() == {"detail": "hardware XML has no ManufacturerData section"}


def test_upload_returns_422_for_schema_version_error_no_namespace(
    client: TestClient,
) -> None:
    """XMLs lacking a KNX namespace raise models.schema.VersionError (a class distinct from
    ArchiveError and product.errors.VersionError) -> must be 422. An
    ``except (ArchiveError, ParseError)``-only fix would miss this."""
    no_ns = _no_namespace_xml()
    archive = _zip_bytes(
        {
            "knx_master.xml": no_ns,
            f"{_MFR}/Catalog.xml": no_ns,
            f"{_MFR}/Hardware.xml": no_ns,
        }
    )
    resp = client.post(
        "/upload",
        files={"file": ("nonamespace.knxprod", archive, "application/octet-stream")},
    )
    assert resp.status_code == 422, (resp.status_code, resp.text)
    assert resp.json() == {"detail": "Could not detect KNX namespace version"}


def test_upload_returns_422_for_invalid_zip(client: TestClient) -> None:
    """A byte stream that is not a ZIP -> ArchiveError -> 422 (pre-existing behavior)."""
    assert _upload(client, "badzip.knxprod", b"not a zip file") == 422


def test_upload_returns_400_for_non_knxprod_filename(client: TestClient) -> None:
    """A filename not ending in .knxprod is rejected before ingestion -> 400."""
    resp = client.post(
        "/upload",
        files={
            "file": ("notmatching.zip", _valid_archive(), "application/octet-stream")
        },
    )
    assert resp.status_code == 400, (resp.status_code, resp.text)
    assert resp.json() == {"detail": "File must be a .knxprod archive"}


def test_upload_returns_200_for_valid_archive(client: TestClient) -> None:
    """A well-formed .knxprod ingests successfully and returns the content-hash filename."""
    resp = client.post(
        "/upload",
        files={"file": ("good.knxprod", _valid_archive(), "application/octet-stream")},
    )
    assert resp.status_code == 200, (resp.status_code, resp.text)
    body = resp.json()
    assert body["filename"].endswith(".knxprod")
    assert body["filename"] != "good.knxprod"


def test_upload_is_idempotent_for_duplicate_content(client: TestClient) -> None:
    """Re-uploading identical content returns the same filename and does not error."""
    content = _valid_archive()
    first = client.post(
        "/upload",
        files={"file": ("good.knxprod", content, "application/octet-stream")},
    )
    second = client.post(
        "/upload",
        files={"file": ("good_copy.knxprod", content, "application/octet-stream")},
    )
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
