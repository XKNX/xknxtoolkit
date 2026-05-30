from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_functional_blocks_public_keys_public_key_rsakey_value import (
    MasterDataFunctionalBlocksPublicKeysPublicKeyRsakeyValue,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocksPublicKeysPublicKey:
    class Meta:
        global_type = False

    rsakey_value: None | MasterDataFunctionalBlocksPublicKeysPublicKeyRsakeyValue = field(
        default=None,
        metadata={
            "name": "RSAKeyValue",
            "type": "Element",
        },
    )
