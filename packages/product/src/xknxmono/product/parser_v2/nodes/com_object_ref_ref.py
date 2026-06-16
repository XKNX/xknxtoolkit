from __future__ import annotations

from xknxmono.models.intermediate import ComObjectRefRef

from .base import DynamicNode
from ..context import EvalContext


class ComObjectRefRefNode(DynamicNode):
    """Leaf: a reference to a communication object exposed in the dynamic tree."""

    def __init__(self, elem: ComObjectRefRef):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        ctx.mark_active(self._elem.ref_id)
        return []

    def com_objects(self, ctx: EvalContext) -> list[str]:
        self.eval(ctx)
        return [ctx.qualify(self._elem.ref_id)]
