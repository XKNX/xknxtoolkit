from __future__ import annotations

from xknxmono.models.intermediate import ParameterRefRef

from .base import DynamicNode


class ParameterRefRefNode(DynamicNode):
    """Leaf: a direct reference to a parameter widget shown in the UI."""

    def __init__(self, elem: ParameterRefRef):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        return []

    def params(self, state: dict[str, str]) -> list:
        return [self._elem]
