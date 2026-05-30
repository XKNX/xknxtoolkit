from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.bus_access_t import BusAccess
from xknxmono.models.intermediate.device_instance_t import DeviceInstance
from xknxmono.models.intermediate.topology_t_area_line_segment_additional_group_addresses import (
    TopologyAreaLineSegmentAdditionalGroupAddresses,
)


@dataclass(slots=True, kw_only=True)
class TopologyAreaLineSegment:
    class Meta:
        global_type = False

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
    additional_group_addresses: None | TopologyAreaLineSegmentAdditionalGroupAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalGroupAddresses",
            "type": "Element",
        },
    )
