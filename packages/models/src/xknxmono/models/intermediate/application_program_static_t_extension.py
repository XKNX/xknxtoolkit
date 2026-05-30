from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.application_program_static_t_extension_baggage import (
    ApplicationProgramStaticExtensionBaggage,
)


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticExtension:
    class Meta:
        global_type = False

    baggage: list[ApplicationProgramStaticExtensionBaggage] = field(
        default_factory=list,
        metadata={
            "name": "Baggage",
            "type": "Element",
        },
    )
