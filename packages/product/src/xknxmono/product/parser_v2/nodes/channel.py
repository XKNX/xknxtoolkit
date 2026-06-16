from __future__ import annotations

from ..context import EvalContext
from ..ui import UiNode
from ..ui.tab import UiTab
from .base import DynamicNode


class ChannelNode(DynamicNode):
    """A tab in the UI — either a named Channel or a ChannelIndependentBlock."""

    __slots__ = (
        "_id",
        "_name",
        "_text",
        "_number",
        "_icon",
        "_text_param_ref_id",
        "_children",
    )

    def __init__(
        self,
        children: list[DynamicNode | None],
        id: str | None = None,
        name: str | None = None,
        text: str | None = None,
        number: str | None = None,
        icon: str | None = None,
        text_parameter_ref_id: str | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._text = text
        self._number = number
        self._icon = icon
        self._text_param_ref_id = text_parameter_ref_id
        self._children = children

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        items = [u for c in self._children if c for u in c.eval(ctx)]
        text = (
            ctx.get(self._text_param_ref_id) if self._text_param_ref_id else None
        ) or self._text
        return [
            UiTab(
                children=tuple(items),
                id=self._id,
                name=self._name,
                text=text,
                number=self._number,
                icon=self._icon,
            )
        ]
