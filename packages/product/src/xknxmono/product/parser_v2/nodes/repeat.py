from __future__ import annotations

from xknxmono.models.intermediate import Repeat

from .base import DynamicNode


class RepeatNode(DynamicNode):
    """
    Container: repeats its children N times, where N comes from count or from a
    parameter value at eval time (when count=0 and parameter_ref_id is set).

    Each repetition should substitute the loop index into the child ref_ids — this
    index substitution is not yet implemented; all repetitions currently share the
    same child nodes.
    """

    def __init__(self, elem: Repeat, children: list[DynamicNode | None]):
        self._elem = elem
        self._children = children

    def _count(self, state: dict[str, str]) -> int:
        if self._elem.count != 0:
            return self._elem.count
        if self._elem.parameter_ref_id:
            try:
                return int(state.get(self._elem.parameter_ref_id, "0"))
            except ValueError:
                return 0
        return 0

    def eval(self, state: dict[str, str]) -> list[DynamicNode]:
        active = [c for c in self._children if c is not None]
        # TODO: each repetition needs the loop index substituted into ref_ids
        count = self._count(state)
        result: list[DynamicNode] = []
        for _ in range(count):
            result.extend(active)
        return result
