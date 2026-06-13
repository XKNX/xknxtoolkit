from __future__ import annotations

from xknxmono.models.intermediate import ParameterRefRef

from .base import DynamicNode
from .context import EvalContext


class ParameterRefRefNode(DynamicNode):
    """Leaf: a direct reference to a parameter widget shown in the UI."""

    def __init__(self, elem: ParameterRefRef):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def params(self, ctx: EvalContext) -> list:
        return [ctx.qualify(self._elem.ref_id)] if self._elem.ref_id else []
