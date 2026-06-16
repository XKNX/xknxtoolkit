from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.parameter_block_layout_t import ParameterBlockLayout


@dataclass(frozen=True, slots=True)
class UiParameterBlock:
    id: str
    children: tuple[object, ...]
    name: str | None = None
    text: str | None = None
    inline: bool = False
    layout: ParameterBlockLayout = ParameterBlockLayout.LIST
