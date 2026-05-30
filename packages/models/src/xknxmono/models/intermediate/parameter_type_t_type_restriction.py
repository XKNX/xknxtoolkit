from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.parameter_type_t_type_restriction_enumeration import (
    ParameterTypeTypeRestrictionEnumeration,
)


@dataclass(slots=True, kw_only=True)
class ParameterTypeTypeRestriction:
    """
    :ivar enumeration: registration-relevant set
    """

    class Meta:
        global_type = False

    enumeration: list[ParameterTypeTypeRestrictionEnumeration] = field(
        default_factory=list,
        metadata={
            "name": "Enumeration",
            "type": "Element",
        },
    )
