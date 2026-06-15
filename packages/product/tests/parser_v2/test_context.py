from xknxmono.models.intermediate import ModuleInstance, ModuleNumericArg, ParameterInstanceRef
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState, ModuleState

_BASE = "M-0008_A-7072-21-5CC3-O000A"

_REF_MODE   = f"{_BASE}_P-1_R-1"
_REF_TARGET = f"{_BASE}_P-2_R-2"

_DEF_PREFIX         = f"{_BASE}_MD-1"
_MODULE_ID          = f"{_BASE}_MD-1_M-C8"           # Module(0xC8 = 200)
_MODULE_INSTANCE_ID = f"{_BASE}_MD-1_M-C8_MI-1"
_LOCAL_REF          = f"{_BASE}_MD-1_P-96_R-F3"      # ParamRef(0x96=150, 0xF3=243)
_QUALIFIED_REF      = f"{_BASE}_MD-1_M-C8_MI-1_P-96_R-F3"
_ARG_REF            = f"{_BASE}_MD-1_A-1"

_SM_DEF_PREFIX         = f"{_BASE}_MD-1_SM-1"
_SM_MODULE_INSTANCE_ID = f"{_BASE}_MD-1_M-64_MI-1_SM-1_M-C8_MI-1"  # Module(0x64=100), SubModule(0xC8=200)
_SM_ARG_REF            = f"{_BASE}_MD-1_SM-1_A-1"
_REL_SM_ARG_REF        = "MD-1_SM-1_A-1"  # relative form; no manufacturer prefix


def _num_arg(ref_id: str, value: int) -> ModuleNumericArg:
    return ModuleNumericArg(ref_id=ref_id, value=value)


def _alloc_arg(ref_id: str, allocator_ref_id: str) -> ModuleNumericArg:
    return ModuleNumericArg(ref_id=ref_id, allocator_ref_id=allocator_ref_id)


class TestModuleStateArguments:
    def test_get_arg_returns_value(self):
        arg = _num_arg(_ARG_REF, 5)
        ms = ModuleState(_MODULE_INSTANCE_ID, {_ARG_REF: arg})
        assert ms.get_arg(_ARG_REF) is arg

    def test_get_arg_returns_none_for_missing(self):
        ms = ModuleState(_MODULE_INSTANCE_ID)
        assert ms.get_arg(_ARG_REF) is None

    def test_args_not_in_parameter_instance_refs(self):
        ms = ModuleState(_MODULE_INSTANCE_ID, {_ARG_REF: _num_arg(_ARG_REF, 5)})
        assert ms.parameter_instance_refs() == {}

    def test_args_not_visible_via_ctx_get(self):
        ms = ModuleState(_MODULE_INSTANCE_ID, {_ARG_REF: _num_arg(_ARG_REF, 5)})
        assert EvalContext(ms).get(_ARG_REF) is None

    def test_as_module_instance_for_submodule_roundtrips_args(self):
        arg = _num_arg(_SM_ARG_REF, 9)
        ms = ModuleState(_SM_MODULE_INSTANCE_ID, {_SM_ARG_REF: arg})
        instance_id, ref_id, args = ms.as_module_instance()
        assert instance_id == _SM_MODULE_INSTANCE_ID
        assert ref_id == f"{_BASE}_MD-1_M-64_MI-1_SM-1_M-C8"
        assert args == {_REL_SM_ARG_REF: arg}

    def test_allocator_arg_stored_without_value(self):
        allocator_ref = f"{_BASE}_MD-1_L-2"
        arg = _alloc_arg(_ARG_REF, allocator_ref)
        ms = ModuleState(_MODULE_INSTANCE_ID, {_ARG_REF: arg})
        result = ms.get_arg(_ARG_REF)
        assert isinstance(result, ModuleNumericArg)
        assert result.value is None
        assert result.allocator_ref_id == allocator_ref


class TestEvalContext:
    def test_get_returns_global_value(self):
        ctx = EvalContext(GlobalState({_REF_MODE: "42"}))
        assert ctx.get(_REF_MODE) == "42"

    def test_get_returns_none_for_missing_key(self):
        ctx = EvalContext(GlobalState())
        assert ctx.get(_REF_MODE) is None

    def test_set_writes_to_global(self):
        state = GlobalState()
        ctx = EvalContext(state)
        ctx.set(_REF_TARGET, "99")
        assert state.parameter_instance_refs() == {_REF_TARGET: "99"}

    def test_module_ctx_set_appears_in_parameter_instance_refs(self):
        state = GlobalState()
        mctx = EvalContext(state).module_ctx(_MODULE_ID)
        mctx.set(_LOCAL_REF, "5")
        assert state.parameter_instance_refs() == {_QUALIFIED_REF: "5"}

    def test_repeat_ctx_sets_instance_idx_for_module(self):
        state = GlobalState()
        mctx = EvalContext(state).repeat_ctx(3).module_ctx(_MODULE_ID)
        mctx.set(_LOCAL_REF, "5")
        expected_ref = f"{_BASE}_MD-1_M-C8_MI-3_P-96_R-F3"
        assert state.parameter_instance_refs() == {expected_ref: "5"}

    def test_module_ctx_reads_initial_value(self):
        state = GlobalState.from_project(
            [ParameterInstanceRef(ref_id=_QUALIFIED_REF, value="7")],
            [ModuleInstance(id=_MODULE_INSTANCE_ID, ref_id=_DEF_PREFIX)],
        )
        mctx = EvalContext(state).module_ctx(_MODULE_ID)
        assert mctx.get(_LOCAL_REF) == "7"

    def test_module_ctx_write_overwrites_initial_value(self):
        state = GlobalState.from_project(
            [ParameterInstanceRef(ref_id=_QUALIFIED_REF, value="old")],
            [ModuleInstance(id=_MODULE_INSTANCE_ID, ref_id=_DEF_PREFIX)],
        )
        mctx = EvalContext(state).module_ctx(_MODULE_ID)
        mctx.set(_LOCAL_REF, "new")
        assert mctx.get(_LOCAL_REF) == "new"
