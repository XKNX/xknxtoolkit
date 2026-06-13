from __future__ import annotations

from abc import ABC, abstractmethod


class DynamicNode(ABC):
    """
    DynamicNode is the base class for all nodes in the dynamic tree.

    eval(state) returns the node's active direct children given the current parameter
    state. Containers return their (conditionally active) children; leaves return [].

    params() and com_objects() recurse through eval() via a flatmap, so the base
    class implementation is correct for all container nodes. Leaf nodes that contribute
    to one of these domains override the relevant method to return their own element.
    """

    @abstractmethod
    def eval(self, state: dict[str, str]) -> list[DynamicNode]: ...

    def params(self, state: dict[str, str]) -> list:
        return [p for node in self.eval(state) for p in node.params(state)]

    def com_objects(self, state: dict[str, str]) -> list:
        return [co for node in self.eval(state) for co in node.com_objects(state)]

    def ui(self, state: dict[str, str]) -> list:
        return [u for node in self.eval(state) for u in node.ui(state)]
