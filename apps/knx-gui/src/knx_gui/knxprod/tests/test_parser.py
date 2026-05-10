import pytest
from pathlib import Path

from knx_gui.knxprod import parse_archive, ParamTypeKind


MDT_ARCHIVE = Path("/Users/user/Documents/projects/personal/xknxproduct/tests/resources/MDT/MDT_AKD-02x0CC-02_KP_V31.knxprod")


@pytest.mark.skipif(not MDT_ARCHIVE.exists(), reason="MDT archive not available")
class TestParseArchive:
    def test_parses_applications(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        assert len(apps) >= 1

    def test_extracts_com_objects(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        app = apps[0]
        assert len(app.com_objects) > 0
        co = app.com_objects[0]
        assert co.id
        assert co.name

    def test_extracts_parameters_with_types(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        app = apps[0]
        assert len(app.parameters) > 0

        enum_params = [p for p in app.parameters if p.param_type and p.param_type.kind == ParamTypeKind.ENUM]
        assert len(enum_params) > 0

        sample = enum_params[0]
        assert sample.param_type is not None
        assert len(sample.param_type.options) > 0

    def test_extracts_dynamic_structure(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        app = apps[0]
        assert app.dynamic is not None
        assert len(app.dynamic.chooses) > 0

    def test_visible_parameters_filters_correctly(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        app = apps[0]

        all_params = app.parameters
        visible_params = app.visible_parameters()

        assert len(visible_params) < len(all_params)
        assert len(visible_params) > 0

    def test_longitude_params_filtered(self):
        apps = parse_archive(str(MDT_ARCHIVE))
        app = apps[0]

        all_lon = [p for p in app.parameters if "ongitud" in p.text.lower()]
        visible_lon = [p for p in app.visible_parameters() if "ongitud" in p.text.lower()]

        assert len(visible_lon) < len(all_lon)
