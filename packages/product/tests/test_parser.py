from pathlib import Path

import pytest

from xknxmono.product import ParamTypeKind, load
from xknxmono.product.parser.modules import (
    substitute_template as _substitute_template,
)

MDT_ARCHIVE = Path(
    "/Users/user/Documents/projects/personal/xknxproduct/tests/resources/MDT/MDT_AKD-02x0CC-02_KP_V31.knxprod"
)


def _applications(path: Path):
    return list(load(str(path)).applications.values())


@pytest.mark.skipif(not MDT_ARCHIVE.exists(), reason="MDT archive not available")
class TestRegistry:
    def test_has_applications(self):
        assert len(_applications(MDT_ARCHIVE)) >= 1

    def test_extracts_com_objects(self):
        app = _applications(MDT_ARCHIVE)[0]
        com_objects = app.com_objects()
        assert len(com_objects) > 0
        assert com_objects[0].id and com_objects[0].name

    def test_extracts_parameters_with_types(self):
        app = _applications(MDT_ARCHIVE)[0]
        params = app.parameters()
        assert len(params) > 0

        enum_params = [
            p
            for p in params
            if p.param_type and p.param_type.kind == ParamTypeKind.ENUM
        ]
        assert len(enum_params) > 0
        assert len(enum_params[0].param_type.options) > 0

    def test_extracts_dynamic_structure(self):
        app = _applications(MDT_ARCHIVE)[0]
        tree = app.dynamic_tree()
        assert tree is not None
        assert len(tree.chooses) > 0

    def test_visible_parameters_filters_correctly(self):
        app = _applications(MDT_ARCHIVE)[0]
        visible = app.visible_parameters()
        assert 0 < len(visible) < len(app.parameters())

    def test_registry_links_hardware_to_application(self):
        reg = load(str(MDT_ARCHIVE))
        assert reg.hardware
        assert reg.catalog_items
        assert any(reg.applications_for_hardware(hw_id) for hw_id in reg.hardware)
        assert any(reg.products_for_hardware(hw_id) for hw_id in reg.hardware)


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
