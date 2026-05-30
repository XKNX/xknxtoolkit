from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.application_program_static_t_fixup_list_baggage import (
    ApplicationProgramStaticFixupListBaggage,
)
from xknxmono.models.intermediate.fixup_t import Fixup


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticFixupList:
    """
    :ivar fixup: registration-relevant set
    :ivar baggage:
    """

    class Meta:
        global_type = False

    fixup: list[Fixup] = field(
        default_factory=list,
        metadata={
            "name": "Fixup",
            "type": "Element",
            "min_occurs": 1,
        },
    )
    baggage: list[ApplicationProgramStaticFixupListBaggage] = field(
        default_factory=list,
        metadata={
            "name": "Baggage",
            "type": "Element",
        },
    )
