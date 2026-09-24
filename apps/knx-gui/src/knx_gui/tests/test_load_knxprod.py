"""Unit tests for `KnxGuiApp._load_knxprod` — the File -> Load knxprod... handler.

Builds minimal in-memory .knxprod archives with zipfile/io.BytesIO (no fixture files),
constructs a real `KnxGuiApp` against a tmp_path catalog, and drives the private
handler directly. The handler must recover from every input-corruption failure mode
of `CatalogService.import_knxprod` by converting it into an in-app error task, rather
than letting the exception escape to `hello_imgui.run()` (which re-raises and
terminates the GUI).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from knx_gui.main import KnxGuiApp
from knx_gui.plugins.tasks.service import Task

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


def _no_knx_namespace_entries() -> dict[str, bytes]:
    """Structurally valid ZIP that passes Archive._validate_structure but whose
    knx_master.xml has no KNX namespace, so detect_version raises VersionError."""
    return {
        "knx_master.xml": b'<?xml version="1.0"?><NotKnx/>',
        f"{_MFR}/Catalog.xml": b'<?xml version="1.0"?><NotKnx/>',
        f"{_MFR}/Hardware.xml": b'<?xml version="1.0"?><NotKnx/>',
    }


def _bad_crc_zip(entries: dict[str, bytes]) -> bytes:
    """A structurally valid ZIP whose first member's CRC-32 in the central directory
    is corrupted, so ZipFile.read() raises BadZipFile on member read (not construction)."""
    data = bytearray(_zip_bytes(entries))
    sig = b"PK\x01\x02"  # central directory file header signature
    idx = data.find(sig)
    assert idx != -1, "no central directory header found"
    # CRC-32 sits at offset +16 within the CDF header; flip the top bit so the stored
    # CRC no longer matches the CRC computed over the (still-intact) member data.
    data[idx + 16] ^= 0x80
    return bytes(data)


def _app(tmp_path: Path, db_name: str = "catalog.db") -> KnxGuiApp:
    return KnxGuiApp(tmp_path / db_name)


def _write_knxprod(tmp_path: Path, name: str, content: bytes) -> str:
    path = tmp_path / name
    path.write_bytes(content)
    return str(path)


def _tasks(app: KnxGuiApp) -> list[Task]:
    return app._task_service.tasks()  # pyright: ignore[reportPrivateUsage]


def _load_knxprod(app: KnxGuiApp, path: str) -> None:
    app._load_knxprod(path)  # pyright: ignore[reportPrivateUsage]


def _assert_errored_task(app: KnxGuiApp, label: str, detail_substr: str) -> None:
    tasks = _tasks(app)
    assert len(tasks) == 1
    task = tasks[0]
    assert task.label == label
    assert task.status == "error"
    assert detail_substr in task.detail


# --- the three escaping exception types the handler set was missing -------------


def test_version_error_is_recovered_not_raised(tmp_path: Path) -> None:
    """Regression for the reported crash: a structurally-valid-but-invalid master XML
    raises VersionError out of detect_version; the handler must convert it to an
    error task instead of letting it escape to hello_imgui.run()."""
    app = _app(tmp_path)
    spath = _write_knxprod(
        tmp_path, "version_error.knxprod", _zip_bytes(_no_knx_namespace_entries())
    )

    _load_knxprod(app, spath)  # must not raise

    _assert_errored_task(app, "Loading version_error.knxprod", "namespace version")


def test_parse_error_is_recovered_not_raised(tmp_path: Path) -> None:
    """A namespaced-but-empty Hardware.xml passes detect_version then raises
    product.errors.ParseError (no ManufacturerData); the handler must recover it."""
    app = _app(tmp_path)
    content = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,  # parses cleanly
            f"{_MFR}/Catalog.xml": _MASTER_XML,  # not reached (hardware parsed first)
            f"{_MFR}/Hardware.xml": _MASTER_XML,  # valid namespace, no ManufacturerData
        }
    )
    spath = _write_knxprod(tmp_path, "parse_error.knxprod", content)

    _load_knxprod(app, spath)  # must not raise

    _assert_errored_task(app, "Loading parse_error.knxprod", "ManufacturerData")


def test_bad_zip_file_is_recovered_not_raised(tmp_path: Path) -> None:
    """A CRC mismatch on member read (passes namelist / _validate_structure, fails
    ZipFile.read) raises zipfile.BadZipFile; the handler must recover it."""
    app = _app(tmp_path)
    content = _bad_crc_zip(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": b"<x/>",
            f"{_MFR}/Hardware.xml": b"<x/>",
        }
    )
    spath = _write_knxprod(tmp_path, "bad_crc.knxprod", content)

    _load_knxprod(app, spath)  # must not raise

    _assert_errored_task(app, "Loading bad_crc.knxprod", "Bad CRC-32")


# --- existing handlers must keep working (no regression) -----------------------


def test_archive_error_still_recovered(tmp_path: Path) -> None:
    """A non-ZIP file is wrapped into ArchiveError by Archive.__init__; the existing
    handler must still convert it to an error task."""
    app = _app(tmp_path)
    spath = _write_knxprod(tmp_path, "not_a_zip.knxprod", b"not a zip file at all")

    _load_knxprod(app, spath)  # must not raise

    _assert_errored_task(app, "Loading not_a_zip.knxprod", "Invalid ZIP archive")


def test_os_error_still_recovered(tmp_path: Path) -> None:
    """A missing file makes path.read_bytes() raise FileNotFoundError (an OSError);
    the existing handler must still convert it to an error task."""
    app = _app(tmp_path)
    missing = str(tmp_path / "does_not_exist.knxprod")

    _load_knxprod(app, missing)  # must not raise

    _assert_errored_task(app, "Loading does_not_exist.knxprod", "")


def test_value_error_still_recovered(tmp_path: Path) -> None:
    """An xsdata ParserError (a ValueError subclass) from a structurally broken XML
    must stay caught by the existing (OSError, ValueError) handler."""
    app = _app(tmp_path)
    # A knx_master.xml with a KNX namespace but an element xsdata cannot bind raises
    # xsdata.exceptions.ParserError, which is a ValueError subclass.
    content = _zip_bytes(
        {
            "knx_master.xml": (
                b'<?xml version="1.0"?>'
                b'<KNX xmlns="http://knx.org/xml/project/23">'
                b"<BogusElementThatTheSchemaDoesNotAllow/></KNX>"
            ),
            f"{_MFR}/Catalog.xml": b'<?xml version="1.0"?><NotKnx/>',
            f"{_MFR}/Hardware.xml": b'<?xml version="1.0"?><NotKnx/>',
        }
    )
    spath = _write_knxprod(tmp_path, "value_error.knxprod", content)

    _load_knxprod(app, spath)  # must not raise

    tasks = _tasks(app)
    assert len(tasks) == 1
    assert tasks[0].status == "error"
    assert tasks[0].label == "Loading value_error.knxprod"


# --- success path must keep removing the task ----------------------------------


def test_successful_import_removes_the_task(tmp_path: Path) -> None:
    """A valid .knxprod is ingested and the task is removed (no error badge)."""
    app = _app(tmp_path)
    app_id = f"{_MFR}_A-1"
    content = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml(app_id),
            f"{_MFR}/{app_id}.xml": _application_xml(app_id),
        }
    )
    spath = _write_knxprod(tmp_path, "valid.knxprod", content)

    _load_knxprod(app, spath)  # must not raise

    assert _tasks(app) == [], "task must be removed on success"


def test_idempotent_reimport_removes_the_task(tmp_path: Path) -> None:
    """Re-ingesting the same content finds nothing new but still removes the task."""
    app = _app(tmp_path)
    app_id = f"{_MFR}_A-1"
    content = _zip_bytes(
        {
            "knx_master.xml": _MASTER_XML,
            f"{_MFR}/Catalog.xml": _CATALOG_XML,
            f"{_MFR}/Hardware.xml": _hardware_xml(app_id),
            f"{_MFR}/{app_id}.xml": _application_xml(app_id),
        }
    )
    spath = _write_knxprod(tmp_path, "valid.knxprod", content)

    _load_knxprod(app, spath)  # first import
    assert _tasks(app) == []

    _load_knxprod(app, spath)  # re-import: no new applications, still removes the task
    assert _tasks(app) == []


# --- narrow handler: non-input failures must NOT be masked as import errors ------


def test_programming_bug_is_not_swallowed(tmp_path: Path) -> None:
    """The handler set must stay narrow: a non-input failure from the ingest path
    (e.g. a programming bug raising AttributeError) must propagate, not be masked
    as a benign import-error badge that recurs on every subsequent menu action."""
    app = _app(tmp_path)
    from knx_gui.plugins.catalog.service import CatalogService

    original = CatalogService.import_knxprod

    def boom(self: CatalogService, path: Path) -> list[str]:
        raise AttributeError("simulated programming bug in ingest path")

    CatalogService.import_knxprod = boom  # type: ignore[method-assign]
    try:
        spath = _write_knxprod(tmp_path, "whatever.knxprod", b"whatever")
        with pytest.raises(AttributeError, match="simulated programming bug"):
            _load_knxprod(app, spath)
        # the orphaned task stays "running" because the broad-clause path was NOT taken
        tasks = _tasks(app)
        assert len(tasks) == 1
        assert tasks[0].status == "running"
    finally:
        CatalogService.import_knxprod = original  # type: ignore[method-assign]
