from __future__ import annotations

from xknxmono.models.intermediate import ParameterSeparator

from .base import DynamicNode
from .._name import apply_text_args
from ..context import EvalContext
from ..ui import UiNode
from ..ui.separator import UiSeparator


class ParameterSeparatorNode(DynamicNode):
    """Leaf: a static label or visual separator between parameters in a block."""

    def __init__(self, elem: ParameterSeparator):
        self._elem = elem

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        text = self._elem.text
        if text:
            text = apply_text_args(text, ctx.get_arg_defaults()) or None
        return [UiSeparator(id=self._elem.id, text=text, cell=self._elem.cell)]
