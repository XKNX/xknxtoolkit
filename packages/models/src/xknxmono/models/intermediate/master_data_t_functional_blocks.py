from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_functional_blocks_functional_block import (
    MasterDataFunctionalBlocksFunctionalBlock,
)
from xknxmono.models.intermediate.master_data_t_functional_blocks_parameters import (
    MasterDataFunctionalBlocksParameters,
)
from xknxmono.models.intermediate.master_data_t_functional_blocks_public_keys import (
    MasterDataFunctionalBlocksPublicKeys,
)


@dataclass(slots=True, kw_only=True)
class MasterDataFunctionalBlocks:
    class Meta:
        global_type = False

    functional_block: list[MasterDataFunctionalBlocksFunctionalBlock] = field(
        default_factory=list,
        metadata={
            "name": "FunctionalBlock",
            "type": "Element",
        },
    )
    order_number_formatting_script: None | str = field(
        default=None,
        metadata={
            "name": "OrderNumberFormattingScript",
            "type": "Element",
        },
    )
    public_keys: None | MasterDataFunctionalBlocksPublicKeys = field(
        default=None,
        metadata={
            "name": "PublicKeys",
            "type": "Element",
        },
    )
    parameters: list[MasterDataFunctionalBlocksParameters] = field(
        default_factory=list,
        metadata={
            "name": "Parameters",
            "type": "Element",
        },
    )
