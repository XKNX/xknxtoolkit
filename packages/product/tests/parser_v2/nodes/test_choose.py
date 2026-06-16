from xknxmono.product.parser_v2.nodes import ChooseWhenNode, DynamicNode, EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.choose import _token_matches, _value_matches, satisfies

_BASE = "M-0008_A-7072-21-5CC3-O000A"
_REF_MODE = f"{_BASE}_P-1_R-1"


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


class TestChooseWhenNode:
    def test_eval_returns_empty_with_no_conditions_and_no_default(self):
        node = ChooseWhenNode(_REF_MODE, {}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "1"}))) == []

    def test_eval_returns_matching_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "1"}))) == [leaf]

    def test_eval_falls_through_to_default(self):
        leaf = LeafNode()
        default_leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, [default_leaf])
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}))) == [default_leaf]

    def test_eval_default_branch_without_test_condition(self):
        # <when default="true"> with no Test attribute — default_nodes directly, no condition key
        default_leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {}, [default_leaf])
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "anything"}))) == [default_leaf]

    def test_eval_returns_empty_when_no_match_and_no_default(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}))) == []

    def test_eval_uses_empty_string_for_missing_param(self):
        node = ChooseWhenNode(_REF_MODE, {"1": [LeafNode()]}, None)
        assert node.eval(EvalContext(GlobalState())) == []

    def test_params_flatmaps_through_active_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.params(EvalContext(GlobalState({_REF_MODE: "1"}))) == [leaf]

    def test_params_returns_empty_for_inactive_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1": [leaf]}, None)
        assert node.params(EvalContext(GlobalState({_REF_MODE: "99"}))) == []

    def test_eval_matches_value_in_space_separated_condition(self):
        leaf = LeafNode()
        node = ChooseWhenNode(_REF_MODE, {"1 2 130 4 6 134 36 132": [leaf]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "130"}))) == [leaf]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "36"}))) == [leaf]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}))) == []
