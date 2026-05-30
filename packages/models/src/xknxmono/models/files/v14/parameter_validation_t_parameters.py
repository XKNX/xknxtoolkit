from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.files.v14.parameter_validation_t_parameters_parameter_ref_ref import (
    ParameterValidationParametersParameterRefRef,
)

__NAMESPACE__ = "http://knx.org/xml/project/14"


@dataclass(slots=True, kw_only=True)
class ParameterValidationParameters:
    """
    :ivar parameter_ref_ref: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_ref_ref: list[ParameterValidationParametersParameterRefRef] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/14",
            "min_occurs": 1,
        },
    )
