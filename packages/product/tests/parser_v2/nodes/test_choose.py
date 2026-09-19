from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.nodes import (
    ChooseWhenNode,
    DynamicNode,
    EvalContext,
    GlobalState,
)
from xknxmono.product.parser_v2.nodes.choose import (
    _token_matches,
    _value_matches,
    satisfies,
)
from xknxmono.product.parser_v2.ui import UiNode
from xknxmono.product.parser_v2.ui.separator import UiSeparator

_BASE = "M-0008_A-7072-21-5CC3-O000A"
_REF_MODE = f"{_BASE}_P-1_R-1"

_UI_A = UiSeparator(id="a", text=None)
_UI_B = UiSeparator(id="b", text=None)


class UiLeaf(DynamicNode):
    """Stub leaf that returns a fixed UiSeparator so we can assert which branch was taken."""

    def __init__(self, marker: UiSeparator) -> None:
        self._marker = marker

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        return [self._marker]


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

    def test_not_equal(self):
        assert _token_matches("3", "!=5") is True
        assert _token_matches("7", "!=5") is True
        assert _token_matches("5", "!=5") is False

    def test_not_equal_negative_operand(self):
        # The XSD pattern `(=|(!=)|>|<|(>=)|(<=))-?\d+` permits a signed operand.
        assert _token_matches("5", "!=-3") is True
        assert _token_matches("-3", "!=-3") is False
        assert _token_matches("0", "!=-3") is True

    def test_equal(self):
        assert _token_matches("5", "=5") is True
        assert _token_matches("3", "=5") is False

    def test_equal_negative_operand(self):
        assert _token_matches("-3", "=-3") is True
        assert _token_matches("3", "=-3") is False

    def test_non_integer_value_with_operator_returns_false(self):
        assert _token_matches("x", ">1") is False
        assert _token_matches("x", "!=1") is False
        assert _token_matches("x", "=1") is False


class TestValueMatches:
    def test_matches_any_token(self):
        assert _value_matches("2", ["1", "2", "3"]) is True
        assert _value_matches("5", ["1", "2", "3"]) is False

    def test_matches_operator_token(self):
        assert _value_matches("10", [">5", "<20"]) is True

    def test_matches_not_equal_token(self):
        assert _value_matches("7", ["!=5"]) is True
        assert _value_matches("5", ["!=5"]) is False

    def test_matches_equal_token(self):
        assert _value_matches("5", ["=5"]) is True
        assert _value_matches("7", ["=5"]) is False


class TestSatisfies:
    def test_none_condition_returns_false(self):
        assert satisfies(None, "1") is False

    def test_space_separated_values(self):
        assert satisfies("1 2 3", "2") is True
        assert satisfies("1 2 3", "5") is False

    def test_operator_in_condition(self):
        assert satisfies(">5", "6") is True
        assert satisfies(">5", "5") is False

    def test_not_equal_condition(self):
        assert satisfies("!=5", "3") is True
        assert satisfies("!=5", "7") is True
        assert satisfies("!=5", "5") is False

    def test_equal_condition(self):
        assert satisfies("=5", "5") is True
        assert satisfies("=5", "3") is False


class TestChooseWhenNode:
    def test_eval_returns_empty_with_no_conditions_and_no_default(
        self, idx: ApplicationIndexer
    ):
        node = ChooseWhenNode(_REF_MODE, {}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "1"}), idx=idx)) == []

    def test_eval_returns_matching_branch(self, idx: ApplicationIndexer):
        node = ChooseWhenNode(_REF_MODE, {"1": [UiLeaf(_UI_A)]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "1"}), idx=idx)) == [_UI_A]

    def test_eval_falls_through_to_default(self, idx: ApplicationIndexer):
        node = ChooseWhenNode(_REF_MODE, {"1": [UiLeaf(_UI_A)]}, [UiLeaf(_UI_B)])
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}), idx=idx)) == [
            _UI_B
        ]

    def test_eval_default_branch_without_test_condition(self, idx: ApplicationIndexer):
        node = ChooseWhenNode(_REF_MODE, {}, [UiLeaf(_UI_B)])
        assert node.eval(
            EvalContext(GlobalState({_REF_MODE: "anything"}), idx=idx)
        ) == [_UI_B]

    def test_eval_returns_empty_when_no_match_and_no_default(
        self, idx: ApplicationIndexer
    ):
        node = ChooseWhenNode(_REF_MODE, {"1": [UiLeaf(_UI_A)]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}), idx=idx)) == []

    def test_eval_uses_empty_string_for_missing_param(self, idx: ApplicationIndexer):
        node = ChooseWhenNode(_REF_MODE, {"1": [UiLeaf(_UI_A)]}, None)
        assert node.eval(EvalContext(GlobalState(), idx=idx)) == []

    def test_eval_matches_value_in_space_separated_condition(
        self, idx: ApplicationIndexer
    ):
        node = ChooseWhenNode(
            _REF_MODE, {"1 2 130 4 6 134 36 132": [UiLeaf(_UI_A)]}, None
        )
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "130"}), idx=idx)) == [
            _UI_A
        ]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "36"}), idx=idx)) == [
            _UI_A
        ]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "99"}), idx=idx)) == []

    def test_eval_matches_not_equal_branch(self, idx: ApplicationIndexer):
        # Regression for the `!=N` operator: previously the branch could never
        # match and `eval` returned the default (or nothing) instead. The branch
        # must now render whenever the parameter value is *not* `N`.
        node = ChooseWhenNode(_REF_MODE, {"!=5": [UiLeaf(_UI_A)]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "3"}), idx=idx)) == [_UI_A]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "7"}), idx=idx)) == [_UI_A]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "5"}), idx=idx)) == []
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "0"}), idx=idx)) == [_UI_A]

    def test_eval_not_equal_branch_does_not_fall_through_to_default(
        self, idx: ApplicationIndexer
    ):
        # Failure mode (a): a `!=N` branch must not be silently replaced by the
        # `default="true"` branch when its condition actually holds.
        node = ChooseWhenNode(_REF_MODE, {"!=5": [UiLeaf(_UI_A)]}, [UiLeaf(_UI_B)])
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "3"}), idx=idx)) == [_UI_A]
        # Only the `!=5` branch's own value (`"5"`) should reach the default.
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "5"}), idx=idx)) == [_UI_B]

    def test_eval_matches_equal_branch(self, idx: ApplicationIndexer):
        # The `=N` form is redundant with the bare-integer form but is XSD-legal
        # and the matcher must handle it.
        node = ChooseWhenNode(_REF_MODE, {"=5": [UiLeaf(_UI_A)]}, [UiLeaf(_UI_B)])
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "5"}), idx=idx)) == [_UI_A]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "3"}), idx=idx)) == [_UI_B]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "5"}), idx=idx)) == [_UI_A]

    def test_eval_not_equal_negative_operand_branch(self, idx: ApplicationIndexer):
        # The XSD permits a signed operand: `(!=)-?\d+`.
        node = ChooseWhenNode(_REF_MODE, {"!=-3": [UiLeaf(_UI_A)]}, None)
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "5"}), idx=idx)) == [_UI_A]
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "-3"}), idx=idx)) == []
        assert node.eval(EvalContext(GlobalState({_REF_MODE: "0"}), idx=idx)) == [_UI_A]
