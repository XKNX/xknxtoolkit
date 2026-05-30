from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.files.v11.parameter_ref_ref_t import ParameterRefRef

__NAMESPACE__ = "http://knx.org/xml/project/11"


@dataclass(slots=True, kw_only=True)
class ParameterCalculationRparametersParameterRefRef(ParameterRefRef):
    """
    :ivar alias_name: registration-relevant
    """

    class Meta:
        global_type = False

    alias_name: None | str = field(
        default=None,
        metadata={
            "name": "AliasName",
            "type": "Attribute",
            "max_length": 50,
        },
    )
