from __future__ import annotations

from .base import DynamicNode
from ..context import EvalContext


class GenericCollectionNode(DynamicNode):
    """
    GenericCollectionNode is a node that is just a collection of
    children to be evaluate, e.g Dynamic section in itself.
    """

    def __init__(self, children: list[DynamicNode | None]):
        self._children = children

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return [c for c in self._children if c is not None]
