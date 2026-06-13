from __future__ import annotations

from xknxmono.models.intermediate import Button

from .base import DynamicNode


class ButtonNode(DynamicNode):
    """Leaf: an interactive button element shown in a parameter block."""

    def __init__(self, elem: Button):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        return []

    def ui(self, state: dict[str, str]) -> list:
        return [self._elem]
