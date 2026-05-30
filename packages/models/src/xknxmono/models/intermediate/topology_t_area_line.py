from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.bus_access_t import BusAccess
from xknxmono.models.intermediate.device_instance_t import DeviceInstance
from xknxmono.models.intermediate.topology_t_area_line_additional_group_addresses import (
    TopologyAreaLineAdditionalGroupAddresses,
)
from xknxmono.models.intermediate.topology_t_area_line_segment import TopologyAreaLineSegment


@dataclass(slots=True, kw_only=True)
class TopologyAreaLine:
    class Meta:
        global_type = False

    segment: list[TopologyAreaLineSegment] = field(
        default_factory=list,
        metadata={
            "name": "Segment",
            "type": "Element",
            "max_occurs": 128,
        },
    )
    device_instance: list[DeviceInstance] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstance",
            "type": "Element",
        },
    )
    bus_access: None | BusAccess = field(
        default=None,
        metadata={
            "name": "BusAccess",
            "type": "Element",
        },
    )
    additional_group_addresses: None | TopologyAreaLineAdditionalGroupAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalGroupAddresses",
            "type": "Element",
        },
    )
