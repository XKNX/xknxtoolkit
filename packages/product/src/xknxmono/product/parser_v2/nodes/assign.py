from __future__ import annotations

from xknxmono.models.intermediate import Assign

from .base import DynamicNode


class AssignNode(DynamicNode):
    """Leaf: assigns a fixed value to a parameter — no visible UI element, affects state only."""

    def __init__(self, elem: Assign):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        if self._elem.value is not None:
            state[self._elem.target_param_ref_ref] = self._elem.value
        elif self._elem.source_param_ref_ref is not None:
            state[self._elem.target_param_ref_ref] = state.get(
                self._elem.source_param_ref_ref, ""
            )
        return []
