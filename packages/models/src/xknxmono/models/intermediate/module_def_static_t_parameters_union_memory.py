from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.memory_union_t import MemoryUnion


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticParametersUnionMemory(MemoryUnion):
    class Meta:
        global_type = False
