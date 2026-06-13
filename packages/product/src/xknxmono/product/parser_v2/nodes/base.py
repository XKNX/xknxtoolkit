from __future__ import annotations

from abc import ABC, abstractmethod

from .context import EvalContext


class DynamicNode(ABC):
    """
    DynamicNode is the base class for all nodes in the dynamic tree.

    eval(ctx) returns the node's active direct children given the current parameter
    state. Containers return their (conditionally active) children; leaves return [].

    params() and com_objects() recurse through eval() via a flatmap, so the base
    class implementation is correct for all container nodes. Leaf nodes that contribute
    to one of these domains override the relevant method to return their own element.

    RepeatNode and ModuleNode bypass the base-class flatmap entirely — they return []
    from eval() and override params/com_objects/ui to manage their own context.
    """

    @abstractmethod
    def eval(self, ctx: EvalContext) -> list[DynamicNode]: ...

    def params(self, ctx: EvalContext) -> list:
        return [p for node in self.eval(ctx) for p in node.params(ctx)]

    def com_objects(self, ctx: EvalContext) -> list:
        return [co for node in self.eval(ctx) for co in node.com_objects(ctx)]

    def ui(self, ctx: EvalContext) -> list:
        return [u for node in self.eval(ctx) for u in node.ui(ctx)]
