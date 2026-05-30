from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class AddinData:
    class Meta:
        name = "AddinData_t"

    add_in_id: str = field(
        metadata={
            "name": "AddInId",
            "type": "Attribute",
            "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    addin_id_attribute: str = field(
        metadata={
            "name": "AddinId",
            "type": "Attribute",
        }
    )
