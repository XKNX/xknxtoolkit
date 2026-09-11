from typing import Any

import pytest

from xknxmono.product.parser_v2.knx_id import (
    AddressSpace,
    AllocatorRef,
    Application,
    ArgRef,
    Baggage,
    BinaryInput,
    BitmapDef,
    Block,
    Channel,
    ComObject,
    ComObjectRef,
    KnxId,
    Module,
    ModuleDef,
    Parameter,
    ParameterBlock,
    ParameterBlockCell,
    ParameterBlockRef,
    ParameterCalc,
    ParameterRename,
    ParameterSeparator,
    ParameterType,
    ParameterValue,
    ParamRef,
    RepeatPath,
    ResourceSpec,
    StatusResponse,
    SubModule,
    SubModuleDef,
    UnionParameter,
    UnionParameterRef,
)

_MFR = "0008"
_APP = "7072-21-5CC3-O000A"
_BASE = f"M-{_MFR}_A-{_APP}"


class TestFromString:
    def test_manufacturer_only(self):
        k = KnxId.from_string("M-0008")
        assert k.manufacturer == 0x0008
        assert k.content is None

    def test_manufacturer_and_application(self):
        k = KnxId.from_string(_BASE)
        assert k.manufacturer == 0x0008
        assert isinstance(k.content, Application)
        assert k.content.number == 0x7072
        assert k.content.version == 0x21
        assert k.content.fingerprint == 0x5CC3
        assert k.content.order == "O000A"
        assert k.content.content is None

    def test_app_level_param_ref(self):
        k = KnxId.from_string(f"{_BASE}_P-1_R-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ParamRef(1, 1)

    def test_app_level_repeat(self):
        k = KnxId.from_string(f"{_BASE}_X-4")
        assert isinstance(k.content, Application)
        assert k.content.content == RepeatPath(4)

    def test_module_def(self):
        k = KnxId.from_string(f"{_BASE}_MD-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1)

    def test_module_def_param_ref(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_P-150_R-243")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, ParamRef(0x150, 0x243))

    def test_module_def_argument(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_A-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, ArgRef(1))

    def test_module_def_allocator(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_L-2")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, AllocatorRef(2))

    def test_module_def_level_repeat(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_X-4")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, RepeatPath(4))

    def test_module_ref_without_instance(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-200")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, Module(0x200))

    def test_module_instance(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-200_MI-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, Module(0x200, instance=1))

    def test_module_instance_repeat_index(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-200_MI-3")
        assert isinstance(k.content, Application)
        assert isinstance(k.content.content, ModuleDef)
        assert isinstance(k.content.content.content, Module)
        assert k.content.content.content.instance == 3

    def test_module_instance_param_ref(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-200_MI-1_P-150_R-243")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(
            1, Module(0x200, 1, ParamRef(0x150, 0x243))
        )

    def test_submodule_def_under_module_def(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_SM-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, SubModuleDef(1))

    def test_submodule_def_argument(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_SM-1_A-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, SubModuleDef(1, ArgRef(1)))

    def test_submodule_def_level_repeat(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_SM-1_X-4")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, SubModuleDef(1, RepeatPath(4)))

    def test_submodule_instance(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(
            1, Module(0x100, 1, SubModuleDef(1, SubModule(0x200, 1)))
        )

    def test_submodule_instance_param_ref(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1_P-150_R-243")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(
            1,
            Module(
                0x100, 1, SubModuleDef(1, SubModule(0x200, 1, ParamRef(0x150, 0x243)))
            ),
        )

    def test_nested_repeats(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_X-1_X-2")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, RepeatPath(1, RepeatPath(2)))

    def test_wrong_first_prefix_raises(self):
        with pytest.raises(ValueError):
            KnxId.from_string("A-0008_M-app")


class TestStr:
    def test_round_trip_manufacturer_only(self):
        s = "M-0008"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_app_level_param_ref(self):
        s = f"{_BASE}_P-1_R-1"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_app_level_repeat(self):
        s = f"{_BASE}_X-4"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_def_param_ref(self):
        s = f"{_BASE}_MD-1_P-150_R-243"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_def_argument(self):
        s = f"{_BASE}_MD-1_A-1"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_def_allocator(self):
        s = f"{_BASE}_MD-1_L-2"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_def_level_repeat(self):
        s = f"{_BASE}_MD-1_X-4"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_instance(self):
        s = f"{_BASE}_MD-1_M-200_MI-1"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_instance_param_ref(self):
        s = f"{_BASE}_MD-1_M-200_MI-1_P-150_R-243"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_submodule_def_argument(self):
        s = f"{_BASE}_MD-1_SM-1_A-1"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_submodule_def_level_repeat(self):
        s = f"{_BASE}_MD-1_SM-1_X-4"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_submodule_instance(self):
        s = f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_submodule_instance_param_ref(self):
        s = f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1_P-150_R-243"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_nested_repeats(self):
        s = f"{_BASE}_MD-1_X-1_X-2"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_app_without_order_suffix(self):
        s = "M-0008_A-1234-01-ABCD"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_submodule_content_arg_ref(self):
        s = f"{_BASE}_MD-1_SM-1_M-200_A-5"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_module_content_arg_ref_via_parse_module(self):
        s = f"{_BASE}_MD-1_M-100_A-5"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_parameter_calc_without_suffix(self):
        s = f"{_BASE}_MD-1_SM-1_PC-1"
        assert str(KnxId.from_string(s)) == s


class TestRoundTripAppLevelBranches:
    """Every branch of parse_app_content(), each round-tripped through
    from_string -> __str__ to exercise both the parser branch and the
    corresponding leaf class's to_parts()."""

    @pytest.mark.parametrize(
        "suffix",
        [
            "P-1",
            "PB-1",
            "PB-1_R-2",
            "PB-1_C-2",
            "PS-1",
            "PT-foo",
            "PT-foo_EN-1",
            "UP-1",
            "UP-1_R-2",
            "AS-01-00000",
            "PC-1_foo_bar",
            "RS-01-00000",
            "L-1",
            "M-200",
            "BI-1",
            "SR-1",
            "PV-1",
            "PR-1",
            "B-1",
            "BD-1",
            "CH-1",
            "O-1",
            "O-1_R-2",
        ],
    )
    def test_round_trip(self, suffix: str):
        s = f"{_BASE}_{suffix}"
        assert str(KnxId.from_string(s)) == s

    def test_round_trip_baggage(self):
        s = f"M-{_MFR}_BG-mybag"
        assert str(KnxId.from_string(s)) == s

    def test_baggage_content(self):
        k = KnxId.from_string(f"M-{_MFR}_BG-mybag")
        assert k.content == Baggage("mybag")

    def test_unknown_app_content_prefix_yields_no_content(self):
        k = KnxId.from_string(f"{_BASE}_ZZ-1")
        assert isinstance(k.content, Application)
        assert k.content.content is None
        assert str(k) == _BASE


class TestRoundTripModuleDefLevelBranches:
    """Every branch of parse_module_def_content()."""

    @pytest.mark.parametrize(
        "suffix",
        [
            "P-150",
            "PB-1",
            "PB-1_R-2",
            "PB-1_C-2",
            "PS-1",
            "UP-1",
            "UP-1_R-2",
            "CH-1",
            "PC-1_foo",
            "O-1",
            "O-1_R-2",
            "PV-1",
            "B-1",
            "PR-1",
        ],
    )
    def test_round_trip(self, suffix: str):
        s = f"{_BASE}_MD-1_{suffix}"
        assert str(KnxId.from_string(s)) == s

    def test_unknown_module_def_content_prefix_yields_no_content(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_ZZ-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1)
        assert str(k) == f"{_BASE}_MD-1"


class TestRoundTripSubModuleDefBranches:
    """Every branch of parse_sub_module_def() (SubModuleDef nested directly
    under a ModuleDef, not under a Module)."""

    @pytest.mark.parametrize(
        "suffix",
        [
            "CH-1",
            "O-1",
            "O-1_R-2",
            "P-1",
            "P-1_R-2",
            "PB-1",
            "PB-1_R-2",
            "PB-1_C-2",
            "PS-1",
            "UP-1",
            "UP-1_R-2",
            "L-1",
            "PC-1_foo",
        ],
    )
    def test_round_trip(self, suffix: str):
        s = f"{_BASE}_MD-1_SM-1_{suffix}"
        assert str(KnxId.from_string(s)) == s

    def test_unknown_sub_module_def_content_prefix_yields_no_content(self):
        k = KnxId.from_string(f"{_BASE}_MD-1_SM-1_ZZ-1")
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, SubModuleDef(1))
        assert str(k) == f"{_BASE}_MD-1_SM-1"


class TestFromStringEdgeCases:
    """A bare P-N with no following R-N isn't a ParamRef, per
    parse_param_ref's docstring comment - it's left unconsumed and silently
    dropped by the enclosing SubModule/Module, rather than raising."""

    def test_bare_param_terminal_in_submodule_content_is_dropped(self):
        s = f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1_P-5"
        k = KnxId.from_string(s)
        assert isinstance(k.content, Application)
        assert isinstance(k.content.content, ModuleDef)
        assert isinstance(k.content.content.content, Module)
        submodule_def = k.content.content.content.content
        assert isinstance(submodule_def, SubModuleDef)
        assert submodule_def.sub_module == SubModule(0x200, instance=1, content=None)

    def test_bare_param_followed_by_other_token_in_submodule_content_is_dropped(self):
        s = f"{_BASE}_MD-1_M-100_MI-1_SM-1_M-200_MI-1_P-5_CH-1"
        k = KnxId.from_string(s)
        assert isinstance(k.content, Application)
        assert isinstance(k.content.content, ModuleDef)
        assert isinstance(k.content.content.content, Module)
        submodule_def = k.content.content.content.content
        assert isinstance(submodule_def, SubModuleDef)
        assert submodule_def.sub_module == SubModule(0x200, instance=1, content=None)

    def test_bare_param_terminal_in_module_content_is_dropped(self):
        s = f"{_BASE}_MD-1_M-100_P-5"
        k = KnxId.from_string(s)
        assert isinstance(k.content, Application)
        assert k.content.content == ModuleDef(1, Module(0x100))


class TestKnxIdProperties:
    def test_app_property(self):
        k = KnxId(1, content=Application(1, 2, 3))
        assert k.app == Application(1, 2, 3)
        assert k.baggage is None

    def test_baggage_property(self):
        k = KnxId(1, content=Baggage("x"))
        assert k.baggage == Baggage("x")
        assert k.app is None

    def test_no_content(self):
        k = KnxId(1)
        assert k.app is None
        assert k.baggage is None


_SUB_MODULE_PROPS = ["param_ref", "arg_ref"]

_SUB_MODULE_DEF_PROPS = [
    "sub_module",
    "arg_ref",
    "repeat_path",
    "channel",
    "com_object",
    "com_object_ref",
    "param_ref",
    "parameter",
    "parameter_block",
    "parameter_block_ref",
    "parameter_block_cell",
    "parameter_separator",
    "parameter_calc",
    "allocator_ref",
    "union_parameter",
    "union_parameter_ref",
]

_MODULE_PROPS = ["sub_module_def", "param_ref", "arg_ref"]

_MODULE_DEF_PROPS = [
    "module",
    "sub_module_def",
    "param_ref",
    "arg_ref",
    "allocator_ref",
    "repeat_path",
    "parameter",
    "parameter_block",
    "parameter_block_ref",
    "parameter_block_cell",
    "parameter_separator",
    "parameter_calc",
    "union_parameter",
    "union_parameter_ref",
    "channel",
    "com_object",
    "com_object_ref",
    "parameter_value",
    "parameter_record",
    "block",
]

_APPLICATION_PROPS = [
    "module_def",
    "module",
    "param_ref",
    "parameter",
    "parameter_block",
    "parameter_block_ref",
    "parameter_block_cell",
    "parameter_separator",
    "parameter_type",
    "union_parameter",
    "union_parameter_ref",
    "allocator_ref",
    "address_space",
    "parameter_calc",
    "binary_input",
    "status_response",
    "resource_spec",
    "parameter_value",
    "parameter_record",
    "block",
    "bitmap_def",
    "channel",
    "com_object",
    "com_object_ref",
    "repeat_path",
]


def _assert_only_property_set(
    obj: object, props: list[str], active: str | None
) -> None:
    for name in props:
        value = getattr(obj, name)
        if name == active:
            assert value is not None
        else:
            assert value is None, f"{name} should be None, got {value!r}"


class TestSubModuleProperties:
    @pytest.mark.parametrize(
        ("content", "active"),
        [
            (ParamRef(1, 2), "param_ref"),
            (ArgRef(1), "arg_ref"),
            (None, None),
        ],
    )
    def test_properties(self, content: Any, active: str | None):
        sm = SubModule(1, content=content)
        _assert_only_property_set(sm, _SUB_MODULE_PROPS, active)


class TestSubModuleDefProperties:
    @pytest.mark.parametrize(
        ("content", "active"),
        [
            (SubModule(1), "sub_module"),
            (ArgRef(1), "arg_ref"),
            (RepeatPath(1), "repeat_path"),
            (Channel("1"), "channel"),
            (ComObject("1"), "com_object"),
            (ComObjectRef("1", 2), "com_object_ref"),
            (ParamRef(1, 2), "param_ref"),
            (Parameter(1), "parameter"),
            (ParameterBlock(1), "parameter_block"),
            (ParameterBlockRef(1, 2), "parameter_block_ref"),
            (ParameterBlockCell(1, 2), "parameter_block_cell"),
            (ParameterSeparator(1), "parameter_separator"),
            (ParameterCalc(1), "parameter_calc"),
            (AllocatorRef(1), "allocator_ref"),
            (UnionParameter(1), "union_parameter"),
            (UnionParameterRef(1, 2), "union_parameter_ref"),
            (None, None),
        ],
    )
    def test_properties(self, content: Any, active: str | None):
        smd = SubModuleDef(1, content=content)
        _assert_only_property_set(smd, _SUB_MODULE_DEF_PROPS, active)
        if active is not None:
            assert getattr(smd, active) == content


class TestModuleProperties:
    @pytest.mark.parametrize(
        ("content", "active"),
        [
            (SubModuleDef(1), "sub_module_def"),
            (ParamRef(1, 2), "param_ref"),
            (ArgRef(1), "arg_ref"),
            (None, None),
        ],
    )
    def test_properties(self, content: Any, active: str | None):
        m = Module(1, content=content)
        _assert_only_property_set(m, _MODULE_PROPS, active)


class TestModuleDefProperties:
    @pytest.mark.parametrize(
        ("content", "active"),
        [
            (Module(1), "module"),
            (SubModuleDef(1), "sub_module_def"),
            (ParamRef(1, 2), "param_ref"),
            (ArgRef(1), "arg_ref"),
            (AllocatorRef(1), "allocator_ref"),
            (RepeatPath(1), "repeat_path"),
            (Parameter(1), "parameter"),
            (ParameterBlock(1), "parameter_block"),
            (ParameterBlockRef(1, 2), "parameter_block_ref"),
            (ParameterBlockCell(1, 2), "parameter_block_cell"),
            (ParameterSeparator(1), "parameter_separator"),
            (ParameterCalc(1), "parameter_calc"),
            (UnionParameter(1), "union_parameter"),
            (UnionParameterRef(1, 2), "union_parameter_ref"),
            (Channel("1"), "channel"),
            (ComObject("1"), "com_object"),
            (ComObjectRef("1", 2), "com_object_ref"),
            (ParameterValue(1), "parameter_value"),
            (ParameterRename(1), "parameter_record"),
            (Block(1), "block"),
            (None, None),
        ],
    )
    def test_properties(self, content: Any, active: str | None):
        md = ModuleDef(1, content=content)
        _assert_only_property_set(md, _MODULE_DEF_PROPS, active)


class TestApplicationProperties:
    @pytest.mark.parametrize(
        ("content", "active"),
        [
            (ModuleDef(1), "module_def"),
            (Module(1), "module"),
            (ParamRef(1, 2), "param_ref"),
            (Parameter(1), "parameter"),
            (ParameterBlock(1), "parameter_block"),
            (ParameterBlockRef(1, 2), "parameter_block_ref"),
            (ParameterBlockCell(1, 2), "parameter_block_cell"),
            (ParameterSeparator(1), "parameter_separator"),
            (ParameterType("x"), "parameter_type"),
            (UnionParameter(1), "union_parameter"),
            (UnionParameterRef(1, 2), "union_parameter_ref"),
            (AllocatorRef(1), "allocator_ref"),
            (AddressSpace("x"), "address_space"),
            (ParameterCalc(1), "parameter_calc"),
            (BinaryInput(1), "binary_input"),
            (StatusResponse(1), "status_response"),
            (ResourceSpec("x"), "resource_spec"),
            (ParameterValue(1), "parameter_value"),
            (ParameterRename(1), "parameter_record"),
            (Block(1), "block"),
            (BitmapDef("x"), "bitmap_def"),
            (Channel("1"), "channel"),
            (ComObject("1"), "com_object"),
            (ComObjectRef("1", 2), "com_object_ref"),
            (RepeatPath(1), "repeat_path"),
            (None, None),
        ],
    )
    def test_properties(self, content: Any, active: str | None):
        app = Application(1, 2, 3, content=content)
        _assert_only_property_set(app, _APPLICATION_PROPS, active)
