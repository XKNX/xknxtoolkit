from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.hardware_t_products_product_attributes import (
    HardwareProductsProductAttributes,
)
from xknxmono.models.intermediate.hardware_t_products_product_baggages import (
    HardwareProductsProductBaggages,
)
from xknxmono.models.intermediate.registration_info_t import RegistrationInfo


@dataclass(slots=True, kw_only=True)
class HardwareProductsProduct:
    class Meta:
        global_type = False

    baggages: None | HardwareProductsProductBaggages = field(
        default=None,
        metadata={
            "name": "Baggages",
            "type": "Element",
        },
    )
    attributes: None | HardwareProductsProductAttributes = field(
        default=None,
        metadata={
            "name": "Attributes",
            "type": "Element",
        },
    )
    registration_info: None | RegistrationInfo = field(
        default=None,
        metadata={
            "name": "RegistrationInfo",
            "type": "Element",
        },
    )
