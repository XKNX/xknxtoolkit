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

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        items = [u for c in self._children if c for u in c.eval(ctx)]
        text_ref = self._elem.text_parameter_ref_id
        text = (
            ctx.get_text(self._elem.id)
            or (ctx.get(text_ref) if text_ref else None)
            or self._elem.text
        )
        rows = self._elem.rows
        cols = self._elem.columns
        row_labels = tuple(r.text or r.name or "" for r in rows.row) if rows else ()
        column_headers = tuple(c.text or c.name or "" for c in cols.column) if cols else ()
        return [UiParameterBlock(
            id=self._elem.id,
            name=self._elem.name,
            text=text,
            inline=self._elem.inline,
            layout=self._elem.layout,
            children=tuple(items),
            row_labels=row_labels,
            column_headers=column_headers,
        )]
