import pytest

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ModuleArg,
    ModuleInstance,
    ModuleNumericArg,
    ParameterInstanceRef,
)
from xknxmono.models.intermediate.allocator_t import Allocator as IrAllocator
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_t_module_defs import (
    ApplicationProgramModuleDefs,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.module_def_static_t import ModuleDefStatic
from xknxmono.models.intermediate.module_def_static_t_allocators import (
    ModuleDefStaticAllocators,
)
from xknxmono.models.intermediate.module_def_t import ModuleDef
from xknxmono.models.intermediate.module_def_t_arguments import ModuleDefArguments
from xknxmono.models.intermediate.module_def_t_arguments_argument import (
    ModuleDefArgumentsArgument,
)
from xknxmono.models.intermediate.module_def_t_arguments_argument_alignment import (
    ModuleDefArgumentsArgumentAlignment,
)
from xknxmono.product.parser_v2.allocator import Allocator
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.nodes import (
    ChooseWhenNode,
    DynamicNode,
    EvalContext,
    GlobalState,
    ModuleState,
)
from xknxmono.product.parser_v2.ui import UiNode


class _ParamLeaf(DynamicNode):
    """Stub leaf: marks a param ref active as a side effect."""

    def __init__(self, ref_id: str) -> None:
        self._ref_id = ref_id

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        ctx.mark_active_param(self._ref_id)
        return []


_BASE = "M-0008_A-7072-21-5CC3-O000A"

_REF_MODE = f"{_BASE}_P-1_R-1"
_REF_TARGET = f"{_BASE}_P-2_R-2"

_DEF_PREFIX = f"{_BASE}_MD-1"
_MODULE_ID = f"{_BASE}_MD-1_M-C8"  # Module(0xC8 = 200)
_MODULE_INSTANCE_ID = f"{_BASE}_MD-1_M-C8_MI-1"
_LOCAL_REF = f"{_BASE}_MD-1_P-96_R-F3"  # ParamRef(0x96=150, 0xF3=243)
_QUALIFIED_REF = f"{_BASE}_MD-1_M-C8_MI-1_P-96_R-F3"
_ARG_REF = f"{_BASE}_MD-1_A-1"

_SM_DEF_PREFIX = f"{_BASE}_MD-1_SM-1"
_SM_MODULE_INSTANCE_ID = (
    f"{_BASE}_MD-1_M-64_MI-1_SM-1_M-C8_MI-1"  # Module(0x64=100), SubModule(0xC8=200)
)
_SM_ARG_REF = f"{_BASE}_MD-1_SM-1_A-1"
_REL_SM_ARG_REF = "MD-1_SM-1_A-1"  # relative form; no manufacturer prefix


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


class TestTrimToActive:
    def test_hidden_param_is_evicted_after_trim(self):
        state = GlobalState({_REF_MODE: "2", _REF_TARGET: "5"})
        y_leaf = _ParamLeaf(_REF_MODE)
        x_leaf = _ParamLeaf(_REF_TARGET)
        choose = ChooseWhenNode(_REF_MODE, {"1": [x_leaf]}, None)

        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)

        state.trim_to_active()

        assert _REF_MODE in state.param_ref_id_to_value
        assert _REF_TARGET not in state.param_ref_id_to_value

    def test_active_param_is_kept_after_trim(self):
        state = GlobalState({_REF_MODE: "1", _REF_TARGET: "5"})
        y_leaf = _ParamLeaf(_REF_MODE)
        x_leaf = _ParamLeaf(_REF_TARGET)
        choose = ChooseWhenNode(_REF_MODE, {"1": [x_leaf]}, None)

        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)

        state.trim_to_active()

        assert _REF_MODE in state.param_ref_id_to_value
        assert _REF_TARGET in state.param_ref_id_to_value

    def test_stale_rename_text_is_cleared_after_trim(self):
        state = GlobalState()
        state.set_text("some-block-id", "Renamed")
        state.trim_to_active()
        assert state.get_text("some-block-id") is None

    def test_trim_is_clean_for_next_cycle(self):
        state = GlobalState({_REF_MODE: "1", _REF_TARGET: "5"})
        y_leaf = _ParamLeaf(_REF_MODE)
        x_leaf = _ParamLeaf(_REF_TARGET)
        choose = ChooseWhenNode(_REF_MODE, {"1": [x_leaf]}, None)

        state.reset_active()
        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)
        state.trim_to_active()
        assert _REF_TARGET in state.param_ref_id_to_value

        state.set(_REF_MODE, "2")
        state.reset_active()
        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)
        state.trim_to_active()
        assert _REF_TARGET not in state.param_ref_id_to_value

    def test_active_param_refs_returns_marked_refs(self):
        state = GlobalState({_REF_MODE: "1", _REF_TARGET: "5"})
        y_leaf = _ParamLeaf(_REF_MODE)
        x_leaf = _ParamLeaf(_REF_TARGET)
        choose = ChooseWhenNode(_REF_MODE, {"1": [x_leaf]}, None)

        state.reset_active()
        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)
        state.trim_to_active()

        assert state.active_param_refs() == {_REF_MODE, _REF_TARGET}

    def test_active_param_refs_excludes_hidden(self):
        state = GlobalState({_REF_MODE: "2", _REF_TARGET: "5"})
        y_leaf = _ParamLeaf(_REF_MODE)
        x_leaf = _ParamLeaf(_REF_TARGET)
        choose = ChooseWhenNode(_REF_MODE, {"1": [x_leaf]}, None)

        state.reset_active()
        ctx = EvalContext(state)
        y_leaf.eval(ctx)
        choose.eval(ctx)
        state.trim_to_active()

        assert state.active_param_refs() == {_REF_MODE}

    def test_active_param_refs_qualified_in_module_scope(self):
        state = GlobalState()
        ms = state.module_child(_MODULE_ID)
        ms.mark_active_param(_LOCAL_REF)

        assert state.active_param_refs() == {_QUALIFIED_REF}


_ALLOC_ID = f"{_BASE}_MD-1_L-2"


class TestModuleChildMerge:
    def test_arg_overwritten_on_second_visit(self):
        first = ModuleNumericArg(ref_id=_ARG_REF, value=42)
        state = GlobalState()
        child = state.module_child(_MODULE_ID, arguments={_ARG_REF: first})

        second = ModuleNumericArg(ref_id=_ARG_REF, value=99)
        state.module_child(_MODULE_ID, arguments={_ARG_REF: second})

        assert child.get_arg(_ARG_REF) is second


_ARGS: dict[str, ModuleArg] = {
    _ARG_REF: ModuleNumericArg(ref_id=_ARG_REF, allocator_ref_id=_ALLOC_ID)
}


class TestAllocator:
    def test_resolves_at_given_position(self):
        address, next_pos = Allocator(
            id=_ALLOC_ID, start=100, max_inclusive=199
        ).resolve(100, 10, 1, 0)
        assert address == 100
        assert next_pos == 110

    def test_resolves_at_advanced_position(self):
        address, next_pos = Allocator(
            id=_ALLOC_ID, start=100, max_inclusive=199
        ).resolve(110, 10, 1, 0)
        assert address == 110
        assert next_pos == 120

    def test_alignment_rounds_up_position(self):
        # position=103, allocates=3, alignment=4 → aligned to 104, next=107
        address, next_pos = Allocator(
            id=_ALLOC_ID, start=100, max_inclusive=199
        ).resolve(103, 3, 4, 0)
        assert address == 104
        assert next_pos == 107

    def test_overflow_raises(self):
        import pytest

        with pytest.raises(OverflowError):
            Allocator(id=_ALLOC_ID, start=100, max_inclusive=109).resolve(100, 11, 1, 0)


class TestSetInstanceRef:
    def test_global_ref_written_to_root(self):
        state = GlobalState()
        state.set_instance_ref(_REF_TARGET, "42")
        assert state.param_ref_id_to_value[_REF_TARGET] == "42"

    def test_qualified_module_ref_written_to_module_scope(self):
        state = GlobalState()
        _ = state.module_child(_MODULE_ID, ref_id=_DEF_PREFIX)
        state.set_instance_ref(_QUALIFIED_REF, "7")
        ms = next(
            c
            for c in state.module_children()
            if c.module_instance_id == _MODULE_INSTANCE_ID
        )
        assert ms.param_ref_id_to_value[_LOCAL_REF] == "7"

    def test_qualified_ref_visible_via_parameter_instance_refs(self):
        state = GlobalState()
        _ = state.module_child(_MODULE_ID, ref_id=_DEF_PREFIX)
        state.set_instance_ref(_QUALIFIED_REF, "9")
        assert state.parameter_instance_refs()[_QUALIFIED_REF] == "9"

    def test_unknown_ref_written_to_root(self):
        state = GlobalState()
        unknown = f"{_BASE}_P-99_R-99"
        state.set_instance_ref(unknown, "1")
        assert state.param_ref_id_to_value[unknown] == "1"

    def test_no_module_scope_writes_to_root(self):
        # No module_child() called; qualified ref has nowhere to route, lands at root.
        state = GlobalState()
        state.set_instance_ref(_QUALIFIED_REF, "5")
        assert state.param_ref_id_to_value[_QUALIFIED_REF] == "5"


def _indexer_with_allocator(
    def_id: str, alloc_id: str, arg_id: str
) -> ApplicationIndexer:
    md = ModuleDef(
        id=def_id,
        name="",
        static=ModuleDefStatic(
            allocators=ModuleDefStaticAllocators(
                allocator=[
                    IrAllocator(id=alloc_id, name="", start=100, max_inclusive=199)
                ]
            )
        ),
        arguments=ModuleDefArguments(
            argument=[
                ModuleDefArgumentsArgument(
                    id=arg_id,
                    name="",
                    allocates=10,
                    alignment=ModuleDefArgumentsArgumentAlignment.VALUE_1,
                )
            ]
        ),
    )
    app = ApplicationProgram(
        id="APP",
        name="",
        application_number=1,
        application_version=1,
        program_type=ApplicationProgramType.APPLICATION_PROGRAM,
        mask_version="BV20",
        load_procedure_style=LoadProcedureStyle.DEFAULT_PROCEDURE,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=ApplicationProgramStatic(),
        module_defs=ApplicationProgramModuleDefs(module_def=[md]),
    )
    return ApplicationIndexer(app)


class TestEvalContextAllocate:
    def test_allocate_without_indexer_raises(self):
        ctx = EvalContext(GlobalState())
        with pytest.raises(RuntimeError, match="requires an ApplicationIndexer"):
            ctx.allocate("MD1", "L-1", "A-1")

    def test_allocate_returns_start_address_on_first_call(self):
        idx = _indexer_with_allocator("MD1", "L-1", "A-1")
        ctx = EvalContext(GlobalState(), idx=idx)
        assert ctx.allocate("MD1", "L-1", "A-1") == 100

    def test_allocate_advances_position_on_subsequent_calls(self):
        idx = _indexer_with_allocator("MD1", "L-1", "A-1")
        ctx = EvalContext(GlobalState(), idx=idx)
        assert ctx.allocate("MD1", "L-1", "A-1") == 100
        assert ctx.allocate("MD1", "L-1", "A-1") == 110


class TestEvalContextRepeatIdx:
    def test_default_repeat_idx_is_one(self):
        assert EvalContext(GlobalState()).repeat_idx == 1

    def test_repeat_ctx_sets_repeat_idx(self):
        assert EvalContext(GlobalState()).repeat_ctx(5).repeat_idx == 5
