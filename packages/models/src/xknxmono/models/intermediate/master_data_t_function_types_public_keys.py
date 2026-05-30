from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_function_types_public_keys_public_key import (
    MasterDataFunctionTypesPublicKeysPublicKey,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionTypesPublicKeys:
    class Meta:
        global_type = False

    public_key: list[MasterDataFunctionTypesPublicKeysPublicKey] = field(
        default_factory=list,
        metadata={
            "name": "PublicKey",
            "type": "Element",
        },
    )
