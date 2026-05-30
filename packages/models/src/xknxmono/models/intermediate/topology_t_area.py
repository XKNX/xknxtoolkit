from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.topology_t_area_line import TopologyAreaLine


@dataclass(slots=True, kw_only=True)
class TopologyArea:
    class Meta:
        global_type = False

    line: list[TopologyAreaLine] = field(
        default_factory=list,
        metadata={
            "name": "Line",
            "type": "Element",
            "max_occurs": 16,
        },
    )
