from __future__ import annotations

from xknxmono.models.intermediate import Assign

from .base import DynamicNode


class AssignNode(DynamicNode):
    """Leaf: assigns a fixed value to a parameter — no visible UI element, affects state only."""

    def __init__(self, elem: Assign):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        # TODO: apply the assignment to state before eval propagates further
        return []
