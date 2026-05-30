from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.application_program_static_t_binary_data_exclude_memory import (
    ApplicationProgramStaticBinaryDataExcludeMemory,
)
from xknxmono.models.intermediate.application_program_static_t_binary_data_exclude_property import (
    ApplicationProgramStaticBinaryDataExcludeProperty,
)
from xknxmono.models.intermediate.binary_data_t import BinaryData


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticBinaryData:
    class Meta:
        global_type = False

    binary_data: list[BinaryData] = field(
        default_factory=list,
        metadata={
            "name": "BinaryData",
            "type": "Element",
        },
    )
    exclude_memory: list[ApplicationProgramStaticBinaryDataExcludeMemory] = field(
        default_factory=list,
        metadata={
            "name": "ExcludeMemory",
            "type": "Element",
        },
    )
    exclude_property: list[ApplicationProgramStaticBinaryDataExcludeProperty] = field(
        default_factory=list,
        metadata={
            "name": "ExcludeProperty",
            "type": "Element",
        },
    )
