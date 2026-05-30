from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.property_parameter_t import PropertyParameter


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticParametersParameterProperty(PropertyParameter):
    class Meta:
        global_type = False
