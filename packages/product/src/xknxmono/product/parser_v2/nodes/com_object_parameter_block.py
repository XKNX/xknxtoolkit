from __future__ import annotations

from xknxmono.models.intermediate.application_program_channel_t import (
    ComObjectParameterBlock,
)
from xknxmono.models.intermediate.parameter_base_t import ParameterBase
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef

from .._name import apply_text_args, fill_name
from ..context import EvalContext
from ..ui import UiNode
from ..ui.parameter_block import UiParameterBlock
from .base import DynamicNode


class ComObjectParameterBlockNode(DynamicNode):
    """A parameter group box (ParameterBlock element in the dynamic XML)."""

    __slots__ = ("_children", "_elem", "_param", "_param_ref")

    def __init__(
        self,
        elem: ComObjectParameterBlock,
        children: list[DynamicNode | None],
        param_ref: ParameterRef | None = None,
        param: ParameterBase | None = None,
    ) -> None:
        self._elem = elem
        self._children = children
        self._param_ref = param_ref
        self._param = param

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        items = [u for c in self._children if c for u in c.eval(ctx)]
        arg_defaults = ctx.get_arg_defaults()
        text_ref = self._elem.text_parameter_ref_id
        name_value = ctx.get(text_ref) if text_ref else None
        param_ref_text = (
            self._param_ref.text if self._param_ref is not None else None
        ) or (self._param.text if self._param is not None else None)
        template = (
            ctx.get_text(self._elem.id)
            or self._elem.text
            or param_ref_text
            or self._elem.name
        )
        text = (
            fill_name(apply_text_args(template or "", arg_defaults), name_value or "")
            or None
        )
        rows = self._elem.rows
        cols = self._elem.columns
        row_labels = (
            tuple(
                apply_text_args(r.text or r.name or "", arg_defaults) for r in rows.row
            )
            if rows
            else ()
        )
        column_headers = (
            tuple(
                apply_text_args(c.text or c.name or "", arg_defaults)
                for c in cols.column
            )
            if cols
            else ()
        )
        return [
            UiParameterBlock(
                id=self._elem.id,
                name=self._elem.name,
                text=text,
                inline=self._elem.inline,
                layout=self._elem.layout,
                children=tuple(items),
                row_labels=row_labels,
                column_headers=column_headers,
            )
        ]
