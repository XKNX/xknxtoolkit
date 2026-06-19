from __future__ import annotations

from .base import DynamicNode
from ..state import EvalContext
from ..ui import UiNode


class GenericCollectionNode(DynamicNode):
    """Transparent container: flatmaps children's eval results with no wrapping."""

    def __init__(self, children: list[DynamicNode | None]):
        self._children = children

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        return [u for c in self._children if c for u in c.eval(ctx)]
