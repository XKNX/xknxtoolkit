from xknxmono.product.parser_v2.nodes import (
    ChooseWhenNode,
    DynamicNode,
    GenericCollectionNode,
)
from xknxmono.product.parser_v2.nodes.choose import (
    _token_matches,
    _value_matches,
    satisfies,
)


class LeafNode(DynamicNode):
    """Test stub: a leaf that returns [] from eval and itself from params."""

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        return []

    def params(self, state: dict[str, str]) -> list:
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


class TestGenericCollectionNode:
    def test_eval_empty_children_returns_empty_list(self):
        node = GenericCollectionNode([])
        assert node.eval({}) == []

    def test_eval_returns_direct_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.eval({}) == [a, b]

    def test_eval_filters_none_children(self):
        a = LeafNode()
        node = GenericCollectionNode([a, None])
        assert node.eval({}) == [a]

    def test_params_flatmaps_through_children(self):
        a = LeafNode()
        b = LeafNode()
        node = GenericCollectionNode([a, b])
        assert node.params({}) == [a, b]

    def test_params_recurses_into_nested_collection(self):
        leaf = LeafNode()
        inner = GenericCollectionNode([leaf])
        outer = GenericCollectionNode([inner])
        assert outer.params({}) == [leaf]


class TestChooseWhenNode:
    def test_eval_returns_empty_with_no_conditions_and_no_default(self):
        node = ChooseWhenNode("param", {}, None)
        assert node.eval({"param": "1"}) == []

    def test_eval_returns_matching_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode("param", {"1": [leaf]}, None)
        assert node.eval({"param": "1"}) == [leaf]

    def test_eval_falls_through_to_default(self):
        leaf = LeafNode()
        default_leaf = LeafNode()
        node = ChooseWhenNode("param", {"1": [leaf], "default": [default_leaf]}, "default")
        assert node.eval({"param": "99"}) == [default_leaf]

    def test_eval_returns_empty_when_no_match_and_no_default(self):
        leaf = LeafNode()
        node = ChooseWhenNode("param", {"1": [leaf]}, None)
        assert node.eval({"param": "99"}) == []

    def test_eval_uses_empty_string_for_missing_param(self):
        node = ChooseWhenNode("param", {"1": [LeafNode()]}, None)
        assert node.eval({}) == []

    def test_params_flatmaps_through_active_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode("param", {"1": [leaf]}, None)
        assert node.params({"param": "1"}) == [leaf]

    def test_params_returns_empty_for_inactive_branch(self):
        leaf = LeafNode()
        node = ChooseWhenNode("param", {"1": [leaf]}, None)
        assert node.params({"param": "99"}) == []
