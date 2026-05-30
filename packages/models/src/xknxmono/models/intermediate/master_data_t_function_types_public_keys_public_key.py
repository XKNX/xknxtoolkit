from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_function_types_public_keys_public_key_rsakey_value import (
    MasterDataFunctionTypesPublicKeysPublicKeyRsakeyValue,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionTypesPublicKeysPublicKey:
    class Meta:
        global_type = False

    rsakey_value: None | MasterDataFunctionTypesPublicKeysPublicKeyRsakeyValue = field(
        default=None,
        metadata={
            "name": "RSAKeyValue",
            "type": "Element",
        },
    )
