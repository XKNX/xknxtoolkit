from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticParametersParameterMemory(MemoryParameter):
    class Meta:
        global_type = False
