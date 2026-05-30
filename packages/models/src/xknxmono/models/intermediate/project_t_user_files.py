from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.addin_data_t import AddinData
from xknxmono.models.intermediate.user_file_t import UserFile


@dataclass(slots=True, kw_only=True)
class ProjectUserFiles:
    class Meta:
        global_type = False

    user_file: list[UserFile] = field(
        default_factory=list,
        metadata={
            "name": "UserFile",
            "type": "Element",
        },
    )
    addin_data: list[AddinData] = field(
        default_factory=list,
        metadata={
            "name": "AddinData",
            "type": "Element",
        },
    )
