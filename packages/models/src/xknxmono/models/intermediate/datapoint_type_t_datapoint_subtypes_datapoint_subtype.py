from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.datapoint_type_t_datapoint_subtypes_datapoint_subtype_format import (
    DatapointTypeDatapointSubtypesDatapointSubtypeFormat,
)


@dataclass(slots=True, kw_only=True)
class DatapointTypeDatapointSubtypesDatapointSubtype:
    class Meta:
        global_type = False

    format: None | DatapointTypeDatapointSubtypesDatapointSubtypeFormat = field(
        default=None,
        metadata={
            "name": "Format",
            "type": "Element",
        },
    )
