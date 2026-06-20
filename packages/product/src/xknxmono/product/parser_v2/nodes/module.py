from __future__ import annotations

from xknxmono.models.intermediate import ModuleArg

from ..context import EvalContext
from ..ui import UiNode
from .base import DynamicNode


class ModuleNode(DynamicNode):
    """Container: inlines a module definition's subtree under its own instance scope."""

    def __init__(self, module_id: str, subtree: DynamicNode, arguments: dict[str, ModuleArg] | None = None, param_ref_defaults: dict[str, str] | None = None, arg_defaults: dict[str, str] | None = None, def_id: str | None = None) -> None:
        self._module_id = module_id
        self._def_id = def_id
        self._subtree = subtree
        self._arguments = arguments or {}
        self._param_ref_defaults: dict[str, str] = param_ref_defaults or {}
        self._arg_defaults: dict[str, str] = arg_defaults or {}

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        mctx = ctx.module_ctx(self._module_id, self._arguments, param_ref_defaults=self._param_ref_defaults, arg_defaults=self._arg_defaults, def_id=self._def_id)
        return self._subtree.eval(mctx)
