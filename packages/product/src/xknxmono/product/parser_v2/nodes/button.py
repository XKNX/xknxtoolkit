from __future__ import annotations

from xknxmono.models.intermediate import Button

from .base import DynamicNode
from ..context import EvalContext


class ButtonNode(DynamicNode):
    """Leaf: an interactive button element shown in a parameter block."""

    def __init__(self, elem: Button):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def ui(self, ctx: EvalContext) -> list:
        return [self._elem]
