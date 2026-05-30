from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.addin_data_t import AddinData
from xknxmono.models.intermediate.buildings import Buildings
from xknxmono.models.intermediate.group_addresses_t import GroupAddresses
from xknxmono.models.intermediate.locations import Locations
from xknxmono.models.intermediate.p2_plinks_t import P2Plinks
from xknxmono.models.intermediate.split_infos_t import SplitInfos
from xknxmono.models.intermediate.topology_t import Topology
from xknxmono.models.intermediate.trades_t import Trades
from xknxmono.models.intermediate.user_file_t import UserFile


@dataclass(slots=True, kw_only=True)
class ProjectInstallationsInstallation:
    class Meta:
        global_type = False

    topology: Topology = field(
        metadata={
            "name": "Topology",
            "type": "Element",
        }
    )
    choice: None | Locations | Buildings = field(
        default=None,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Locations",
                    "type": Locations,
                },
                {
                    "name": "Buildings",
                    "type": Buildings,
                },
            ),
        },
    )
    group_addresses: GroupAddresses = field(
        metadata={
            "name": "GroupAddresses",
            "type": "Element",
        }
    )
    p2_plinks: None | P2Plinks = field(
        default=None,
        metadata={
            "name": "P2PLinks",
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
    split_infos: None | SplitInfos = field(
        default=None,
        metadata={
            "name": "SplitInfos",
            "type": "Element",
        },
    )
    add_in_data_element: list[AddinData] = field(
        default_factory=list,
        metadata={
            "name": "AddInData",
            "type": "Element",
        },
    )
    addin_data: list[AddinData] = field(
        default_factory=list,
        metadata={
            "name": "AddinData",
            "type": "Element",
        },
    )
    user_file: list[UserFile] = field(
        default_factory=list,
        metadata={
            "name": "UserFile",
            "type": "Element",
        },
    )
