from __future__ import annotations

from xknxmono.models.intermediate.application_program_channel_t import ComObjectParameterBlock

from .base import DynamicNode
from ..context import EvalContext
from ..ui import UiNode
from ..ui.parameter_block import UiParameterBlock


class ComObjectParameterBlockNode(DynamicNode):
    """A parameter group box (ParameterBlock element in the dynamic XML)."""

    __slots__ = ("_elem", "_children")

    def __init__(self, elem: ComObjectParameterBlock, children: list[DynamicNode | None]) -> None:
        self._elem = elem
        self._children = children

    def eval(self, ctx: EvalContext) -> list[DynamicNode]:
        return [child for child in self._children if child is not None]

    def ui(self, ctx: EvalContext) -> list[UiNode]:
        items = [item for child in self._children if child for item in child.ui(ctx)]
        text_ref = self._elem.text_parameter_ref_id
        text = (
            ctx.get_text(self._elem.id)
            or (ctx.get(text_ref) if text_ref else None)
            or self._elem.text
        )
        return [UiParameterBlock(
            id=self._elem.id,
            name=self._elem.name,
            text=text,
            inline=self._elem.inline,
            layout=self._elem.layout,
            children=tuple(items),
        )]
