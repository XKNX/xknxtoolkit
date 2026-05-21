from pathlib import Path

import pytest

from xknxmono.product import ParamTypeKind, parse_archive
from xknxmono.product.parser import _substitute_template

MDT_ARCHIVE = Path(
    "/Users/user/Documents/projects/personal/xknxproduct/tests/resources/MDT/MDT_AKD-02x0CC-02_KP_V31.knxprod"
)


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

        enum_params = [
            p
            for p in app.parameters
            if p.param_type and p.param_type.kind == ParamTypeKind.ENUM
        ]
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
        visible_lon = [
            p for p in app.visible_parameters() if "ongitud" in p.text.lower()
        ]

        assert len(visible_lon) < len(all_lon)


class TestTemplateSubstitution:
    def test_substitutes_function_text(self):
        result = _substitute_template("Channel: {{0}}", "Switch", {})
        assert result == "Channel: Switch"

    def test_substitutes_text_args(self):
        result = _substitute_template("Channel {{ChNo}}: Test", None, {"ChNo": "A"})
        assert result == "Channel A: Test"

    def test_substitutes_both(self):
        result = _substitute_template(
            "Channel {{ChNo}}: {{0}}", "Dimming", {"ChNo": "B"}
        )
        assert result == "Channel B: Dimming"

    def test_removes_unresolved_placeholders(self):
        result = _substitute_template(
            "{{Unknown}} Channel {{ChNo}}", None, {"ChNo": "A"}
        )
        assert result == "Channel A"

    def test_handles_no_placeholders(self):
        result = _substitute_template("Plain text", "Unused", {"ChNo": "A"})
        assert result == "Plain text"

    def test_handles_empty_text_args(self):
        result = _substitute_template("Channel {{ChNo}}: {{0}}", "Switch", {})
        assert result == "Channel : Switch"

    def test_collapses_multiple_spaces(self):
        result = _substitute_template("A {{X}}  {{Y}} B", None, {})
        assert result == "A B"

    def test_strips_whitespace(self):
        result = _substitute_template("  {{0}}  ", "Test", {})
        assert result == "Test"
