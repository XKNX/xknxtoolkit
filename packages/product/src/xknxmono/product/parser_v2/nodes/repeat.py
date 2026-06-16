from __future__ import annotations

from xknxmono.models.intermediate import Repeat

from .base import DynamicNode
from ..context import EvalContext
from ..ui import UiNode


class RepeatNode(DynamicNode):
    """Container: repeats its children N times, each under its own repeat context.

    N comes from count, or from a parameter value when count=0 and parameter_ref_id is set.
    Index substitution for non-Module direct children is not yet implemented.
    """

    def __init__(self, elem: Repeat, children: list[DynamicNode | None]):
        self._elem = elem
        self._children = children

    def _count(self, ctx: EvalContext) -> int:
        if self._elem.count != 0:
            return self._elem.count
        if self._elem.parameter_ref_id:
            try:
                return int(ctx.get(self._elem.parameter_ref_id) or "0")
            except ValueError:
                return 0
        return 0

    def _active(self) -> list[DynamicNode]:
        return [c for c in self._children if c is not None]

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        result: list[UiNode] = []
        for i in range(1, self._count(ctx) + 1):
            rctx = ctx.repeat_ctx(i)
            for c in self._active():
                result.extend(c.eval(rctx))
        return result
