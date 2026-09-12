"""Unit tests for Archive, the .knxprod ZIP-reader. Builds minimal in-memory ZIP
files with zipfile/io.BytesIO - no fixture files needed."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from xknxmono.product.archive import Archive
from xknxmono.product.errors import ArchiveError

_MFR = "M-0008"


def _zip_bytes(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def _valid_entries(**extra: bytes) -> dict[str, bytes]:
    entries = {
        "knx_master.xml": b"<Master/>",
        f"{_MFR}/Catalog.xml": b"<Catalog/>",
        f"{_MFR}/Hardware.xml": b"<Hardware/>",
    }
    entries.update(extra)
    return entries


def test_open_from_bytes() -> None:
    with Archive(_zip_bytes(_valid_entries())) as archive:
        assert archive.manufacturer_ids == {_MFR}


def test_open_from_path(tmp_path: Path) -> None:
    p = tmp_path / "product.knxprod"
    p.write_bytes(_zip_bytes(_valid_entries()))
    with Archive(p) as archive:
        assert archive.manufacturer_ids == {_MFR}


def test_open_from_path_as_str(tmp_path: Path) -> None:
    p = tmp_path / "product.knxprod"
    p.write_bytes(_zip_bytes(_valid_entries()))
    with Archive(str(p)) as archive:
        assert archive.manufacturer_ids == {_MFR}


def test_open_missing_path_raises() -> None:
    with pytest.raises(ArchiveError, match="File not found"):
        Archive("/no/such/file.knxprod")


def test_open_invalid_zip_bytes_raises() -> None:
    with pytest.raises(ArchiveError, match="Invalid ZIP archive"):
        Archive(b"not a zip file")


def test_open_invalid_zip_path_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.knxprod"
    p.write_bytes(b"not a zip file")
    with pytest.raises(ArchiveError, match="Invalid ZIP archive"):
        Archive(p)


def test_no_manufacturer_directory_raises() -> None:
    with pytest.raises(ArchiveError, match="No manufacturer directory"):
        Archive(_zip_bytes({"knx_master.xml": b"<Master/>"}))


def test_missing_master_xml_raises() -> None:
    entries = _valid_entries()
    del entries["knx_master.xml"]
    with pytest.raises(ArchiveError, match=r"Missing required file: knx_master\.xml"):
        Archive(_zip_bytes(entries))


def test_missing_catalog_xml_raises() -> None:
    entries = _valid_entries()
    del entries[f"{_MFR}/Catalog.xml"]
    with pytest.raises(ArchiveError, match="Missing required file"):
        Archive(_zip_bytes(entries))


def test_missing_hardware_xml_raises() -> None:
    entries = _valid_entries()
    del entries[f"{_MFR}/Hardware.xml"]
    with pytest.raises(ArchiveError, match="Missing required file"):
        Archive(_zip_bytes(entries))


def test_validate_manufacturer_id_unknown_raises() -> None:
    with (
        Archive(_zip_bytes(_valid_entries())) as archive,
        pytest.raises(ArchiveError, match="Unknown manufacturer ID"),
    ):
        archive.get_catalog_xml("M-9999")


def test_get_master_xml() -> None:
    with Archive(_zip_bytes(_valid_entries())) as archive:
        assert archive.get_master_xml() == b"<Master/>"


def test_get_catalog_and_hardware_xml() -> None:
    with Archive(_zip_bytes(_valid_entries())) as archive:
        assert archive.get_catalog_xml(_MFR) == b"<Catalog/>"
        assert archive.get_hardware_xml(_MFR) == b"<Hardware/>"


def test_get_application_xmls() -> None:
    app_id = f"{_MFR}_A-1234-01-ABCD"
    entries = _valid_entries(**{f"{_MFR}/{app_id}.xml": b"<App/>"})
    with Archive(_zip_bytes(entries)) as archive:
        apps = archive.get_application_xmls(_MFR)
        assert apps == {app_id: b"<App/>"}


def test_get_application_xmls_ignores_non_matching_files() -> None:
    entries = _valid_entries(**{f"{_MFR}/readme.txt": b"not an app"})
    with Archive(_zip_bytes(entries)) as archive:
        assert archive.get_application_xmls(_MFR) == {}


def test_get_signature_present() -> None:
    entries = _valid_entries(**{f"{_MFR}.signature": b"sig-bytes"})
    with Archive(_zip_bytes(entries)) as archive:
        assert archive.get_signature(_MFR) == b"sig-bytes"


def test_get_signature_absent() -> None:
    with Archive(_zip_bytes(_valid_entries())) as archive:
        assert archive.get_signature(_MFR) is None


def test_list_entries_and_iter() -> None:
    with Archive(_zip_bytes(_valid_entries())) as archive:
        entries = archive.list_entries()
        assert set(entries) == {
            "knx_master.xml",
            f"{_MFR}/Catalog.xml",
            f"{_MFR}/Hardware.xml",
        }
        assert set(iter(archive)) == set(entries)


def test_close_from_path_source_has_no_holder(tmp_path: Path) -> None:
    p = tmp_path / "product.knxprod"
    p.write_bytes(_zip_bytes(_valid_entries()))
    archive = Archive(p)
    archive.close()  # no BytesIO source_holder to close - must not raise
