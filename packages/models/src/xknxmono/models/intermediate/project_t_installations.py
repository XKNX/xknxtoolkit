from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.bus_access_t import BusAccess
from xknxmono.models.intermediate.p2_plinks_t import P2Plinks
from xknxmono.models.intermediate.project_t_installations_installation import (
    ProjectInstallationsInstallation,
)
from xknxmono.models.intermediate.split_infos_t import SplitInfos
from xknxmono.models.intermediate.trades_t import Trades
from xknxmono.models.intermediate.user_file_t import UserFile


@dataclass(slots=True, kw_only=True)
class ProjectInstallations:
    class Meta:
        global_type = False

    installation: list[ProjectInstallationsInstallation] = field(
        default_factory=list,
        metadata={
            "name": "Installation",
            "type": "Element",
            "min_occurs": 1,
            "max_occurs": 16,
        },
    )
    user_file: list[UserFile] = field(
        default_factory=list,
        metadata={
            "name": "UserFile",
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
    p2_plinks: None | P2Plinks = field(
        default=None,
        metadata={
            "name": "P2PLinks",
            "type": "Element",
        },
    )
