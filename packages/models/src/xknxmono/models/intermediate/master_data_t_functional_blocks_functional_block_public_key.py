from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_functional_blocks_functional_block_public_key_rsakey_value import (
    MasterDataFunctionalBlocksFunctionalBlockPublicKeyRsakeyValue,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocksFunctionalBlockPublicKey:
    class Meta:
        global_type = False

    rsakey_value: None | MasterDataFunctionalBlocksFunctionalBlockPublicKeyRsakeyValue = field(
        default=None,
        metadata={
            "name": "RSAKeyValue",
            "type": "Element",
        },
    )
