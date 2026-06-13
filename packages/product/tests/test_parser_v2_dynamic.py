from xknxmono.models.intermediate import Assign
from xknxmono.product.parser_v2.nodes import (
    AssignNode,
    ChooseWhenNode,
    DynamicNode,
    EvalContext,
    GenericCollectionNode,
    ModuleScope,
)
from xknxmono.product.parser_v2.nodes.choose import (
    _token_matches,
    _value_matches,
    satisfies,
)


def _ref(
    manufacturer: str, app: str, param: int, ref: int, module_def: int | None = None
) -> str:
    base = f"M-{manufacturer}_A-{app}"
    if module_def is not None:
        return f"{base}_MD-{module_def}_P-{param}_R-{ref}"
    return f"{base}_P-{param}_R-{ref}"


_MFR = "0008"
_APP = "7072-21-5CC3-O000A"
_REF_MODE = _ref(_MFR, _APP, 1, 1)
_REF_TARGET = _ref(_MFR, _APP, 2, 2)
_REF_SOURCE = _ref(_MFR, _APP, 3, 3)
_REF_OTHER = _ref(_MFR, _APP, 4, 4)
_REF_MISSING = _ref(_MFR, _APP, 5, 5)


class LeafNode(DynamicNode):
    """Test stub: a leaf that returns [] from eval and itself from params."""

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def params(self, ctx: EvalContext) -> list:
        return [self]


class TestTokenMatches:
    def test_exact_match(self):
        assert _token_matches("1", "1") is True
        assert _token_matches("1", "2") is False

    def test_greater_than(self):
        assert _token_matches("5", ">4") is True
        assert _token_matches("4", ">4") is False

    def test_greater_than_or_equal(self):
        assert _token_matches("4", ">=4") is True
        assert _token_matches("3", ">=4") is False

    def test_less_than(self):
        assert _token_matches("3", "<4") is True
        assert _token_matches("4", "<4") is False

    def test_less_than_or_equal(self):
        assert _token_matches("4", "<=4") is True
        assert _token_matches("5", "<=4") is False

    def test_non_integer_value_with_operator_returns_false(self):
        assert _token_matches("x", ">1") is False


class TestValueMatches:
    def test_matches_any_token(self):
        assert _value_matches("2", ["1", "2", "3"]) is True
        assert _value_matches("5", ["1", "2", "3"]) is False

    def test_matches_operator_token(self):
        assert _value_matches("10", [">5", "<20"]) is True


class TestSatisfies:
    def test_none_condition_returns_false(self):
        assert satisfies(None, "1") is False

    def test_space_separated_values(self):
        assert satisfies("1 2 3", "2") is True
        assert satisfies("1 2 3", "5") is False

    def test_operator_in_condition(self):
        assert satisfies(">5", "6") is True
        assert satisfies(">5", "5") is False


class TestEvalContext:
    def test_get_returns_state_value(self):
        ctx = EvalContext({_REF_MODE: "42"})
        assert ctx.get(_REF_MODE) == "42"

    def test_get_returns_default_for_missing_key(self):
        ctx = EvalContext({})
        assert ctx.get(_REF_MODE) == ""
        assert ctx.get(_REF_MODE, "7") == "7"

    def test_set_writes_to_underlying_state(self):
        state: dict[str, str] = {}
        ctx = EvalContext(state)
        ctx.set(_REF_TARGET, "99")
        assert state[_REF_TARGET] == "99"

    def test_qualify_returns_ref_id_unchanged_without_mappings(self):
        ctx = EvalContext({})
        assert ctx.qualify(_REF_MODE) == _REF_MODE

    def test_qualify_applies_module_prefix_substitution(self):
        def_prefix = "M-0008_A-7072-21-5CC3-O000A_MD-1"
        module_id = "M-0008_A-7072-21-5CC3-O000A_MD-1_M-200"
        ctx = EvalContext({}, scope=ModuleScope(module_id, def_prefix))
        ref_id = f"{def_prefix}_P-150_R-243"
        assert ctx.qualify(ref_id) == f"{module_id}_MI-1_P-150_R-243"

    def test_repeat_ctx_sets_instance_idx(self):
        state: dict[str, str] = {}
        def_prefix = "M-0008_A-7072-21-5CC3-O000A_MD-1"
        module_id = "M-0008_A-7072-21-5CC3-O000A_MD-1_M-200"
        ctx = EvalContext(state).repeat_ctx(3)
        module_ctx = ctx.module_ctx(module_id, def_prefix)
        ref_id = f"{def_prefix}_P-150_R-243"
        assert module_ctx.qualify(ref_id) == f"{module_id}_MI-3_P-150_R-243"

    def test_module_ctx_uses_default_instance_idx_of_1(self):
        def_prefix = "M-0008_A-7072-21-5CC3-O000A_MD-1"
        module_id = "M-0008_A-7072-21-5CC3-O000A_MD-1_M-200"
        ctx = EvalContext({})
        module_ctx = ctx.module_ctx(module_id, def_prefix)
        ref_id = f"{def_prefix}_P-150_R-243"
        assert module_ctx.qualify(ref_id) == f"{module_id}_MI-1_P-150_R-243"

    def test_qualify_no_mapping_returns_ref_id_unchanged(self):
        ctx = EvalContext({})
        ref_id = "M-0008_A-7072-21-5CC3-O000A_MD-1_P-150_R-243"
        assert ctx.qualify(ref_id) == ref_id


class TestGenericCollectionNode:
    def test_eval_empty_children_returns_empty_list(self):
        node = GenericCollectionNode([])
        assert node.eval(EvalContext({})) == []

    def test_eval_returns_direct_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.eval(EvalContext({})) == [a, b]

    def test_eval_filters_none_children(self):
        a = LeafNode()
        node = GenericCollectionNode([a, None])
        assert node.eval(EvalContext({})) == [a]

    def test_params_flatmaps_through_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.params(EvalContext({})) == [a, b]

    def test_params_recurses_into_nested_collection(self):
        leaf = LeafNode()
        inner = GenericCollectionNode([leaf])
        outer = GenericCollectionNode([inner])
        assert outer.params(EvalContext({})) == [leaf]


class TestChooseWhenNode:
    def test_eval_returns_empty_with_no_conditions_and_no_default(self):
        node = ChooseWhenNode(_REF_MODE, {}, None)
        assert node.eval(EvalContext({_REF_MODE: "1"})) == []

    def test_eval_returns_matching_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.eval(EvalContext({_REF_MODE: "1"})) == [leaf]

    def test_eval_falls_through_to_default(self):
        leaf = LeafNode()
        default_leaf = LeafNode()
        node = ChooseWhenNode(
            _REF_MODE, {"1": [leaf], "default": [default_leaf]}, "default"
        )
        assert node.eval(EvalContext({_REF_MODE: "99"})) == [default_leaf]

    def test_eval_returns_empty_when_no_match_and_no_default(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.eval(EvalContext({_REF_MODE: "99"})) == []

    def test_eval_uses_empty_string_for_missing_param(self):
        node = ChooseWhenNode(_REF_MODE, {"1": [LeafNode()]}, None)
        assert node.eval(EvalContext({})) == []

    def test_params_flatmaps_through_active_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.params(EvalContext({_REF_MODE: "1"})) == [leaf]

    def test_params_returns_empty_for_inactive_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.params(EvalContext({_REF_MODE: "99"})) == []


class TestAssignNode:
    def test_eval_returns_empty_list(self):
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        assert node.eval(EvalContext({})) == []

    def test_assign_literal_value_mutates_state(self):
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET, value="42"))
        state: dict[str, str] = {}
        node.eval(EvalContext(state))
        assert state[_REF_TARGET] == "42"

    def test_assign_copies_source_param(self):
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_SOURCE)
        )
        state = {_REF_SOURCE: "7"}
        node.eval(EvalContext(state))
        assert state[_REF_TARGET] == "7"

    def test_assign_source_missing_writes_empty_string(self):
        node = AssignNode(
            Assign(target_param_ref_ref=_REF_TARGET, source_param_ref_ref=_REF_MISSING)
        )
        state: dict[str, str] = {}
        node.eval(EvalContext(state))
        assert state[_REF_TARGET] == ""

    def test_assign_value_takes_precedence_over_source(self):
        node = AssignNode(
            Assign(
                target_param_ref_ref=_REF_TARGET,
                value="literal",
                source_param_ref_ref=_REF_OTHER,
            )
        )
        state = {_REF_OTHER: "should-be-ignored"}
        node.eval(EvalContext(state))
        assert state[_REF_TARGET] == "literal"

    def test_assign_mutation_visible_to_subsequent_sibling_in_collection(self):
        assign = AssignNode(Assign(target_param_ref_ref=_REF_MODE, value="1"))
        leaf = LeafNode()
        choose = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        collection = GenericCollectionNode([assign, choose])
        assert collection.params(EvalContext({})) == [leaf]

    def test_assign_no_op_when_both_value_and_source_are_none(self):
        node = AssignNode(Assign(target_param_ref_ref=_REF_TARGET))
        state: dict[str, str] = {}
        node.eval(EvalContext(state))
        assert state == {}
