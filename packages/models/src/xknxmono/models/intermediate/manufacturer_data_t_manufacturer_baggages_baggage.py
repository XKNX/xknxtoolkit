from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.manufacturer_data_t_manufacturer_baggages_baggage_file_info import (
    ManufacturerDataManufacturerBaggagesBaggageFileInfo,
)


@dataclass(slots=True, kw_only=True)
class ManufacturerDataManufacturerBaggagesBaggage:
    class Meta:
        global_type = False

    file_info: ManufacturerDataManufacturerBaggagesBaggageFileInfo = field(
        metadata={
            "name": "FileInfo",
            "type": "Element",
        }
    )
    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "format": "base64",
        },
    )
