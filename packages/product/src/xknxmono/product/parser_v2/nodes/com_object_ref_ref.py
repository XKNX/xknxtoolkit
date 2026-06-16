from __future__ import annotations

from xknxmono.models.intermediate import ComObjectRefRef

from .base import DynamicNode
from ..context import EvalContext
from ..ui import UiNode


class ComObjectRefRefNode(DynamicNode):
    """Leaf: a reference to a communication object exposed in the dynamic tree."""

    def __init__(self, elem: ComObjectRefRef):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        ctx.mark_active_com_object(self._elem.ref_id)
        return []
