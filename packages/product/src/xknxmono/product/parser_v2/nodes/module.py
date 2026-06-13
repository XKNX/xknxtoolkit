from __future__ import annotations

from .base import DynamicNode
from .context import EvalContext


class ModuleNode(DynamicNode):
    """
    Container: inlines a module definition's dynamic subtree at the correct instance scope.

    Bypasses the base-class eval flatmap — returns [] from eval() and overrides
    params/com_objects/ui to evaluate the pre-built subtree under a module_ctx that
    maps module-def-relative ref IDs to instance-qualified ones (MI-{instance_idx}).

    instance_idx is 1 by default (no enclosing Repeat) and is set by RepeatNode via
    repeat_ctx(i) before ModuleNode.params/com_objects/ui is called.
    """

    def __init__(self, module_id: str, def_ref_id: str, subtree: DynamicNode) -> None:
        self._module_id = module_id
        self._def_ref_id = def_ref_id
        self._subtree = subtree

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return []

    def _module_ctx(self, ctx: EvalContext) -> EvalContext:
        return ctx.module_ctx(self._module_id, self._def_ref_id)

    def params(self, ctx: EvalContext) -> list:
        return self._subtree.params(self._module_ctx(ctx))

    def com_objects(self, ctx: EvalContext) -> list:
        return self._subtree.com_objects(self._module_ctx(ctx))

    def ui(self, ctx: EvalContext) -> list:
        return self._subtree.ui(self._module_ctx(ctx))
