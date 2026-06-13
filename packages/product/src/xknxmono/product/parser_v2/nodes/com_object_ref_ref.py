from __future__ import annotations

from xknxmono.models.intermediate import ComObjectRefRef

from .base import DynamicNode


class ComObjectRefRefNode(DynamicNode):
    """Leaf: a reference to a communication object exposed in the dynamic tree."""

    def __init__(self, elem: ComObjectRefRef):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        return []

    def com_objects(self, state: dict[str, str]) -> list:
        return [self._elem]
