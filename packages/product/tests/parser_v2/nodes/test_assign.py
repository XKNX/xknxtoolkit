import pytest

from xknxmono.models.intermediate import ApplicationProgram, Assign
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_refs import (
    ApplicationProgramStaticParameterRefs,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef as IrParameterRef
from xknxmono.product.errors import EncodingError
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.nodes import (
    AssignNode,
    ChooseWhenNode,
    DynamicNode,
    EvalContext,
    GenericCollectionNode,
    GlobalState,
)
from xknxmono.product.parser_v2.ui import UiNode
from xknxmono.product.parser_v2.ui.separator import UiSeparator

_BASE = "M-0008_A-7072-21-5CC3-O000A"
_REF_MODE = f"{_BASE}_P-1_R-1"
_REF_TARGET = f"{_BASE}_P-2_R-2"
_REF_SOURCE = f"{_BASE}_P-3_R-3"
_REF_OTHER = f"{_BASE}_P-4_R-4"
_REF_MISSING = f"{_BASE}_P-5_R-5"


def _indexer_with_param_refs(*ref_ids: str) -> ApplicationIndexer:
    """An indexer whose ParameterRefs each target themselves - enough for
    mark_active_param()'s ref_id -> parameter_id resolution, which AssignNode.eval
    now performs on its target."""
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
        static=ApplicationProgramStatic(
            parameter_refs=ApplicationProgramStaticParameterRefs(
                parameter_ref=[
                    IrParameterRef(id=ref_id, ref_id=ref_id) for ref_id in ref_ids
                ]
            )
        ),
    )
    return ApplicationIndexer(app)


class UiLeaf(DynamicNode):
    """Stub leaf that returns a UiSeparator so we can verify it was included."""

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        return [UiSeparator(id="leaf", text=None)]


class TestAssignNode:
    def test_eval_returns_empty_list(self):
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        assert node.eval(EvalContext(GlobalState(), idx=idx)) == []

    def test_assign_literal_value_mutates_state(self):
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert state.parameter_instance_refs()[_REF_TARGET] == "42"

    def test_assign_copies_source_param(self):
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_SOURCE)
        )
        state = GlobalState({_REF_SOURCE: "7"})
        node.eval(EvalContext(state, idx=idx))
        assert state.parameter_instance_refs()[_REF_TARGET] == "7"

    def test_assign_source_missing_skips_write(self, idx: ApplicationIndexer):
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_MISSING)
        )
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert _REF_TARGET not in state.parameter_instance_refs()

    def test_assign_value_takes_precedence_over_source(self):
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(
            Assign(
                target_param_ref_ref=_REF_TARGET,
                value="literal",
                source_param_ref_ref=_REF_OTHER,
            )
        )
        state = GlobalState({_REF_OTHER: "should-be-ignored"})
        node.eval(EvalContext(state, idx=idx))
        assert state.parameter_instance_refs()[_REF_TARGET] == "literal"

    def test_assign_mutation_visible_to_subsequent_sibling_in_collection(self):
        # Assign fires before choose in eval order, so the leaf is reachable.
        idx = _indexer_with_param_refs(_REF_MODE)
        assign = AssignNode(Assign(target_param_ref_ref=_REF_MODE, value="1"))
        leaf = UiLeaf()
        choose = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        collection = GenericCollectionNode([assign, choose])
        result = collection.eval(EvalContext(GlobalState(), idx=idx))
        assert result == [UiSeparator(id="leaf", text=None)]

    def test_assign_marks_target_param_active(self):
        # After eval, the target ref must be in the scope's active set so
        # trim_to_active() does not evict the override (the AssignNode bug).
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert _REF_TARGET in state.active_param_refs()

    def test_assign_source_arm_marks_target_param_active(self):
        # The source-arm of AssignNode.eval must also mark the target active
        # when the source value is present, since it writes the same override.
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_SOURCE)
        )
        state = GlobalState({_REF_SOURCE: "7"})
        node.eval(EvalContext(state, idx=idx))
        assert _REF_TARGET in state.active_param_refs()

    def test_assign_source_arm_does_not_mark_target_when_source_missing(
        self, idx: ApplicationIndexer
    ):
        # When source is None the source arm must NOT mark the target active —
        # nothing was written, so activity would be spurious.
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_MISSING)
        )
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert _REF_TARGET not in state.active_param_refs()

    def test_assign_override_survives_trim_to_active(self):
        # The end-to-end guarantee the fix restores: without mark_active_param,
        # trim_to_active() evicts the override from param_ref_id_to_value.
        idx = _indexer_with_param_refs(_REF_TARGET)
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        state.trim_to_active()
        assert state.parameter_instance_refs().get(_REF_TARGET) == "42"

    def test_assign_raises_when_both_value_and_source_are_none(
        self, idx: ApplicationIndexer
    ):
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET))
        state = GlobalState()
        with pytest.raises(EncodingError, match=_REF_TARGET):
            node.eval(EvalContext(state, idx=idx))
