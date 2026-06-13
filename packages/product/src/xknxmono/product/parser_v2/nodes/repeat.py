from __future__ import annotations

from xknxmono.models.intermediate import Repeat

from .base import DynamicNode
from .context import EvalContext


class RepeatNode(DynamicNode):
    """
    Container: repeats its children N times, where N comes from count or from a
    parameter value at eval time (when count=0 and parameter_ref_id is set).

    Bypasses the base-class eval flatmap — returns [] from eval() and overrides
    params/com_objects/ui directly so each iteration gets its own repeat_ctx(i),
    which ModuleNode children use to qualify their instance prefix as MI-{i}.

    Index substitution into ref_ids per repetition is not yet implemented.
    """

    def __init__(self, elem: Repeat, children: list[DynamicNode | None]):
        self._elem = elem
        self._children = children

    def _count(self, ctx: EvalContext) -> int:
        if self._elem.count != 0:
            return self._elem.count
        if self._elem.parameter_ref_id:
            try:
                return int(ctx.get(self._elem.parameter_ref_id, "0"))
            except ValueError:
                return 0
        return 0

    def _active(self) -> list[DynamicNode]:
        return [c for c in self._children if c is not None]

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def params(self, ctx: EvalContext) -> list:
        result = []
        for i in range(1, self._count(ctx) + 1):
            repeat_ctx = ctx.repeat_ctx(i)
            for c in self._active():
                result.extend(c.params(repeat_ctx))
        return result

    def com_objects(self, ctx: EvalContext) -> list:
        result = []
        for i in range(1, self._count(ctx) + 1):
            repeat_ctx = ctx.repeat_ctx(i)
            for c in self._active():
                result.extend(c.com_objects(repeat_ctx))
        return result

    def ui(self, ctx: EvalContext) -> list:
        result = []
        for i in range(1, self._count(ctx) + 1):
            repeat_ctx = ctx.repeat_ctx(i)
            for c in self._active():
                result.extend(c.ui(repeat_ctx))
        return result
