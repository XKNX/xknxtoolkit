from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_space_usages_public_key_rsakey_value import (
    MasterDataSpaceUsagesPublicKeyRsakeyValue,
)


@dataclass(slots=True, kw_only=True)
class MasterDataSpaceUsagesPublicKey:
    class Meta:
        global_type = False

    rsakey_value: None | MasterDataSpaceUsagesPublicKeyRsakeyValue = field(
        default=None,
        metadata={
            "name": "RSAKeyValue",
            "type": "Element",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    revoked: bool = field(
        default=False,
        metadata={
            "name": "Revoked",
            "type": "Attribute",
        },
    )
