from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.files.v10.parameter_calculation_t_rparameters_parameter_ref_ref import (
    ParameterCalculationRparametersParameterRefRef,
)

__NAMESPACE__ = "http://knx.org/xml/project/10"


@dataclass(slots=True, kw_only=True)
class ParameterCalculationRparameters:
    """
    :ivar parameter_ref_ref: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_ref_ref: list[ParameterCalculationRparametersParameterRefRef] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
