from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.property_union_t import PropertyUnion


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticParametersUnionProperty(PropertyUnion):
    class Meta:
        global_type = False
