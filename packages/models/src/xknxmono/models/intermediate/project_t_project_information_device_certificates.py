from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.bus_access_t import BusAccess
from xknxmono.models.intermediate.device_certificate_t import DeviceCertificate
from xknxmono.models.intermediate.split_infos_t import SplitInfos
from xknxmono.models.intermediate.trades_t import Trades


@dataclass(slots=True, kw_only=True)
class ProjectProjectInformationDeviceCertificates:
    class Meta:
        global_type = False

    device_certificate: list[DeviceCertificate] = field(
        default_factory=list,
        metadata={
            "name": "DeviceCertificate",
            "type": "Element",
        },
    )
    trades: None | Trades = field(
        default=None,
        metadata={
            "name": "Trades",
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
    split_infos: None | SplitInfos = field(
        default=None,
        metadata={
            "name": "SplitInfos",
            "type": "Element",
        },
    )
