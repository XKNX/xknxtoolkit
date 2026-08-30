"""Tests for the online catalog client (parsers, cache) and the panel fetch state."""

import json

import pytest

from knx_gui.plugins.catalog.online_catalog import (
    OnlineCatalogClient,
    OnlineCatalogError,
    OnlineManufacturer,
    parse_manufacturer_ids,
    parse_manufacturer_names,
)

_MANUFACTURERS_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<ArrayOfunsignedShort xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays">'
    b"<unsignedShort>2</unsignedShort>"
    b"<unsignedShort>1</unsignedShort>"
    b"<unsignedShort>10</unsignedShort>"
    b"</ArrayOfunsignedShort>"
)

_MASTER_XML = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23">'
    b"<MasterData Id=\"MD-1\" Version=\"1\">"
    b'<Manufacturer Id="M-0001" KnxManufacturerId="1" Name="Siemens" />'
    b'<Manufacturer Id="M-0002" KnxManufacturerId="2" Name="ABB" />'
    b"<Manufacturers></Manufacturers>"
    b"</MasterData>"
    b"</KNX>"
)


class TestParse:
    def test_manufacturer_ids_sorted_and_namespaced(self) -> None:
        assert parse_manufacturer_ids(_MANUFACTURERS_XML) == [1, 2, 10]

    def test_manufacturer_ids_empty_raises(self) -> None:
        with pytest.raises(OnlineCatalogError):
            parse_manufacturer_ids(b"<ArrayOfunsignedShort></ArrayOfunsignedShort>")

    def test_manufacturer_names(self) -> None:
        assert parse_manufacturer_names(_MASTER_XML) == {1: "Siemens", 2: "ABB"}

    def test_manufacturer_names_empty_raises(self) -> None:
        with pytest.raises(OnlineCatalogError):
            parse_manufacturer_names(b"<KNX><MasterData></MasterData></KNX>")


class TestClient:
    def test_cache_roundtrip(self, tmp_path) -> None:
        client = OnlineCatalogClient(tmp_path)
        assert client.cached_manufacturers() is None

        client._save_cache([OnlineManufacturer(1, "Siemens")])
        assert [m.name for m in client.cached_manufacturers()] == ["Siemens"]

    def test_cache_ignores_corrupt_file(self, tmp_path) -> None:
        (tmp_path / "online_catalog_manufacturers.json").write_text("not json", "utf-8")
        assert OnlineCatalogClient(tmp_path).cached_manufacturers() is None

    def test_cache_survives_reload(self, tmp_path) -> None:
        OnlineCatalogClient(tmp_path)._save_cache(
            [OnlineManufacturer(7, "Berker"), OnlineManufacturer(1, "Siemens")]
        )
        reloaded = OnlineCatalogClient(tmp_path).cached_manufacturers()
        assert [m.id for m in reloaded] == [7, 1]
        assert json.loads(
            (tmp_path / "online_catalog_manufacturers.json").read_text("utf-8")
        ) == [{"id": 7, "name": "Berker"}, {"id": 1, "name": "Siemens"}]


class TestPanelOnlineState:
    """The panel's fetch flag logic (imgui rendering is exercised by the app itself)."""

    def test_refresh_flag_lifecycle(self, tmp_path) -> None:
        from knx_gui.plugins.catalog.ui.panel import CatalogPanel

        panel = CatalogPanel(
            get_products=list,
            on_select=lambda product: None,
            get_online_manufacturers=lambda: None,
            on_online_refresh=lambda: None,
        )
        assert not panel._online_shown
        assert not panel._online_loading

        panel._fetch_online()  # success path sets shown, clears loading
        assert panel._online_shown
        assert not panel._online_loading

        def failing_refresh() -> None:
            raise OnlineCatalogError("no network")

        panel._on_online_refresh = failing_refresh
        panel._fetch_online()  # error path keeps the list hidden, clears loading
        assert panel._online_error
        assert panel._online_shown  # a previous successful list stays visible
