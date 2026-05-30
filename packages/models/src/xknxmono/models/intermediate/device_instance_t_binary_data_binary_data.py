from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class DeviceInstanceBinaryDataBinaryData:
    class Meta:
        global_type = False

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "format": "base64",
        },
    )
