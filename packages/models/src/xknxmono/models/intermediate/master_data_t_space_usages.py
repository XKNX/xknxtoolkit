from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_space_usages_public_key import (
    MasterDataSpaceUsagesPublicKey,
)
from xknxmono.models.intermediate.space_usage_t import SpaceUsage


@dataclass(slots=True, kw_only=True)
class MasterDataSpaceUsages:
    class Meta:
        global_type = False

    space_usage: list[SpaceUsage] = field(
        default_factory=list,
        metadata={
            "name": "SpaceUsage",
            "type": "Element",
        },
    )
    public_key: list[MasterDataSpaceUsagesPublicKey] = field(
        default_factory=list,
        metadata={
            "name": "PublicKey",
            "type": "Element",
        },
    )
