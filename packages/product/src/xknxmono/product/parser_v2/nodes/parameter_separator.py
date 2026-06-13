from __future__ import annotations

from xknxmono.models.intermediate import ParameterSeparator

from .base import DynamicNode
from .context import EvalContext


class ParameterSeparatorNode(DynamicNode):
    """Leaf: a static label or visual separator between parameters in a block."""

    def __init__(self, elem: ParameterSeparator):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def ui(self, ctx: EvalContext) -> list:
        return [self._elem]
