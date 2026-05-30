from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.addin_data_t import AddinData


@dataclass(slots=True, kw_only=True)
class ProjectAddInData1:
    class Meta:
        global_type = False

    add_in_data: list[AddinData] = field(
        default_factory=list,
        metadata={
            "name": "AddInData",
            "type": "Element",
        },
    )
