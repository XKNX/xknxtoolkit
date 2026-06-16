from __future__ import annotations

from xknxmono.models.intermediate import ModuleArg

from .base import DynamicNode
from ..context import EvalContext
from ..ui import UiNode


class ModuleNode(DynamicNode):
    """Container: inlines a module definition's subtree under its own instance scope."""

    def __init__(self, module_id: str, subtree: DynamicNode, arguments: dict[str, ModuleArg] | None = None) -> None:
        self._module_id = module_id
        self._subtree = subtree
        self._arguments = arguments or {}

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        mctx = ctx.module_ctx(self._module_id, self._arguments)
        return self._subtree.eval(mctx)
