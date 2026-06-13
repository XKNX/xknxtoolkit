from __future__ import annotations

from xknxmono.models.intermediate import Rename

from .base import DynamicNode


class RenameNode(DynamicNode):
    """Leaf: overrides the display name of a channel or element within a choose branch."""

    def __init__(self, elem: Rename):
        self._elem = elem

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        # TODO: propagate the rename to the target element
        return []
