from __future__ import annotations

from xknxmono.models.intermediate import Rename

from .base import DynamicNode
from ..context import EvalContext


class RenameNode(DynamicNode):
    """Leaf: overrides the display text of a ComObjectParameterBlock within a choose branch.

    The side effect fires in eval() so that the enclosing block can read the renamed text
    after evaluating its children. The base-class ui() calls self.eval() naturally, so no
    ui() override is needed.
    """

    __slots__ = ("_elem",)

    def __init__(self, elem: Rename):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        ctx.set_text(self._elem.ref_id, self._elem.text)
        return []
