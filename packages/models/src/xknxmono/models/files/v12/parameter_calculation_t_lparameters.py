from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.files.v12.parameter_calculation_t_lparameters_parameter_ref_ref import (
    ParameterCalculationLparametersParameterRefRef,
)

__NAMESPACE__ = "http://knx.org/xml/project/12"


@dataclass(slots=True, kw_only=True)
class ParameterCalculationLparameters:
    """
    :ivar parameter_ref_ref: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_ref_ref: list[ParameterCalculationLparametersParameterRefRef] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )
