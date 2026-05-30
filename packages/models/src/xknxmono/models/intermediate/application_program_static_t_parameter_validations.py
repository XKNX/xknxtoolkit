from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.com_object_t import ComObject
from xknxmono.models.intermediate.parameter_validation_t import ParameterValidation


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticParameterValidations:
    """
    :ivar parameter_validation: registration-relevant set
    :ivar com_object: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_validation: list[ParameterValidation] = field(
        default_factory=list,
        metadata={
            "name": "ParameterValidation",
            "type": "Element",
        },
    )
    com_object: list[ComObject] = field(
        default_factory=list,
        metadata={
            "name": "ComObject",
            "type": "Element",
        },
    )
