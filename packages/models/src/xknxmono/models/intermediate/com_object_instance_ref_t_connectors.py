from __future__ import annotations

from dataclasses import dataclass, field

from xknxmono.models.intermediate.com_object_instance_ref_t_connectors_receive import (
    ComObjectInstanceRefConnectorsReceive,
)
from xknxmono.models.intermediate.com_object_instance_ref_t_connectors_send import (
    ComObjectInstanceRefConnectorsSend,
)


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefConnectors:
    class Meta:
        global_type = False

    send: None | ComObjectInstanceRefConnectorsSend = field(
        default=None,
        metadata={
            "name": "Send",
            "type": "Element",
        },
    )
    receive: list[ComObjectInstanceRefConnectorsReceive] = field(
        default_factory=list,
        metadata={
            "name": "Receive",
            "type": "Element",
        },
    )
