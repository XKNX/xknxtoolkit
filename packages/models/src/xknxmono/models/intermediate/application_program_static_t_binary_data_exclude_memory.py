from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticBinaryDataExcludeMemory:
    class Meta:
        global_type = False

    code_segment: str = field(
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
