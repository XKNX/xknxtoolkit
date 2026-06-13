from __future__ import annotations

from xknxmono.models.intermediate import BinaryDataRef

from .base import DynamicNode
from .context import EvalContext


class BinaryDataRefNode(DynamicNode):
    """Leaf: a reference to a static binary data blob defined in the application program."""

    def __init__(self, elem: BinaryDataRef):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []
