from __future__ import annotations

from xknxmono.models.intermediate import Rename

from .base import DynamicNode
from ..context import EvalContext
from ..ui import UiNode


class RenameNode(DynamicNode):
    """Leaf: overrides the display text of a ComObjectParameterBlock within a choose branch."""

    __slots__ = ("_elem",)

    def __init__(self, elem: Rename):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        ctx.set_text(self._elem.ref_id, self._elem.text)
        return []
