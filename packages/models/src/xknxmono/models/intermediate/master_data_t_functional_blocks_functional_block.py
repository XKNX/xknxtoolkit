from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_functional_blocks_functional_block_parameters import (
    MasterDataFunctionalBlocksFunctionalBlockParameters,
)
from xknxmono.models.intermediate.master_data_t_functional_blocks_functional_block_public_key import (
    MasterDataFunctionalBlocksFunctionalBlockPublicKey,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocksFunctionalBlock:
    class Meta:
        global_type = False

    parameters: list[MasterDataFunctionalBlocksFunctionalBlockParameters] = field(
        default_factory=list,
        metadata={
            "name": "Parameters",
            "type": "Element",
        },
    )
    public_key: list[MasterDataFunctionalBlocksFunctionalBlockPublicKey] = field(
        default_factory=list,
        metadata={
            "name": "PublicKey",
            "type": "Element",
        },
    )
