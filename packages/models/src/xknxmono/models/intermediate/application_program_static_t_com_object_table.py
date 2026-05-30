from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.com_object_t import ComObject


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticComObjectTable:
    """
    :ivar com_object: registration-relevant set
    """

    class Meta:
        global_type = False

    com_object: list[ComObject] = field(
        default_factory=list,
        metadata={
            "name": "ComObject",
            "type": "Element",
        },
    )
