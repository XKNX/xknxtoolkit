from __future__ import annotations

from xknxmono.models.intermediate import ParameterSeparator

from .base import DynamicNode


class ParameterSeparatorNode(DynamicNode):
    """Leaf: a static label or visual separator between parameters in a block."""

    def __init__(self, elem: ParameterSeparator):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        return []

    def ui(self, state: dict[str, str]) -> list:
        return [self._elem]
