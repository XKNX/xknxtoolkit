from __future__ import annotations

from .base import DynamicNode
from ..context import EvalContext

_OPERATORS = (">=", "<=", ">", "<")


def _token_matches(value: str, token: str) -> bool:
    """A ``<when Test=...>`` token: an exact value, or a comparison like ``>0`` / ``<=5``."""
    for op in _OPERATORS:
        if token.startswith(op):
            try:
                left, right = int(value), int(token[len(op) :])
            except ValueError:
                return False
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            return left < right
    return value == token


def _value_matches(value: str, test_values: list[str]) -> bool:
    return any(_token_matches(value, t) for t in test_values)


def satisfies(condition: str | None, value: str) -> bool:
    if condition is None:
        return False
    test_values = [v.strip() for v in str(condition).split() if v.strip()]
    return _value_matches(value, test_values)


class ChooseWhenNode(DynamicNode):
    def __init__(
        self,
        param_ref_id: str,
        condition_to_nodes: dict[str, list[DynamicNode | None]],
        default_nodes: list[DynamicNode | None] | None,
    ):
        self._param_ref_id = param_ref_id
        self._condition_to_nodes = condition_to_nodes
        self._default_nodes = default_nodes

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        value = ctx.get(self._param_ref_id) or ""
        for condition, nodes in self._condition_to_nodes.items():
            if satisfies(condition, value):
                return [n for n in nodes if n is not None]
        if self._default_nodes is not None:
            return [n for n in self._default_nodes if n is not None]
        return []
