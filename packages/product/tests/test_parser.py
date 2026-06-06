from pathlib import Path

import pytest

from xknxmono.product import ParamTypeKind, load
from xknxmono.product.parser.modules import (
    apply_text_args,
    fill_name,
)
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
    def test_apply_text_args_substitutes_args(self):
        assert apply_text_args("Channel {{ChNo}}: Test", {"ChNo": "A"}) == (
            "Channel A: Test"
        )

    def test_apply_text_args_keeps_name_placeholder(self):
        # the {{0}} name placeholder is left for fill_name (filled from live param values)
        assert apply_text_args("K {{ChNo}} ({{0:...}})", {"ChNo": "1"}) == (
            "K 1 ({{0:...}})"
        )

    def test_fill_name_fills_placeholder(self):
        assert fill_name("Channel ({{0}})", "Hallway") == "Channel (Hallway)"

    def test_fill_name_handles_format_spec(self):
        assert fill_name("K 1 ({{0:...}}) - Output", "Hallway") == (
            "K 1 (Hallway) - Output"
        )

    def test_fill_name_empty_leaves_bare_parens(self):
        assert fill_name("K 1 ({{0:...}}) - Output", "") == "K 1 () - Output"

    def test_fill_name_drops_unresolved_and_tidies(self):
        assert fill_name("  {{Unknown}}  K 1  ", "") == "K 1"

    def test_substitute_template_applies_args_and_drops_rest(self):
        # the label helper: args in, every remaining token out
        assert (
            _substitute_template("{{Unknown}} Channel {{ChNo}}", None, {"ChNo": "A"})
            == "Channel A"
        )

    def test_substitute_template_handles_no_placeholders(self):
        assert _substitute_template("Plain text", None, {"ChNo": "A"}) == "Plain text"
