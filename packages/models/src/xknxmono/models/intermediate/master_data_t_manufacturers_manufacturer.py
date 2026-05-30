from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer_datapoint_roles import (
    MasterDataManufacturersManufacturerDatapointRoles,
)
from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer_datapoint_types import (
    MasterDataManufacturersManufacturerDatapointTypes,
)
from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer_function_types import (
    MasterDataManufacturersManufacturerFunctionTypes,
)
from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer_public_keys import (
    MasterDataManufacturersManufacturerPublicKeys,
)
from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer_space_usages import (
    MasterDataManufacturersManufacturerSpaceUsages,
)


@dataclass(slots=True, kw_only=True)
class MasterDataManufacturersManufacturer:
    class Meta:
        global_type = False

    order_number_formatting_script: None | str = field(
        default=None,
        metadata={
            "name": "OrderNumberFormattingScript",
            "type": "Element",
        },
    )
    public_keys: None | MasterDataManufacturersManufacturerPublicKeys = field(
        default=None,
        metadata={
            "name": "PublicKeys",
            "type": "Element",
        },
    )
    datapoint_types: None | MasterDataManufacturersManufacturerDatapointTypes = field(
        default=None,
        metadata={
            "name": "DatapointTypes",
            "type": "Element",
        },
    )
    datapoint_roles: None | MasterDataManufacturersManufacturerDatapointRoles = field(
        default=None,
        metadata={
            "name": "DatapointRoles",
            "type": "Element",
        },
    )
    function_types: None | MasterDataManufacturersManufacturerFunctionTypes = field(
        default=None,
        metadata={
            "name": "FunctionTypes",
            "type": "Element",
        },
    )
    space_usages: None | MasterDataManufacturersManufacturerSpaceUsages = field(
        default=None,
        metadata={
            "name": "SpaceUsages",
            "type": "Element",
        },
    )
