from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_functional_blocks_public_keys_public_key import (
    MasterDataFunctionalBlocksPublicKeysPublicKey,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocksPublicKeys:
    class Meta:
        global_type = False

    public_key: list[MasterDataFunctionalBlocksPublicKeysPublicKey] = field(
        default_factory=list,
        metadata={
            "name": "PublicKey",
            "type": "Element",
        },
    )
