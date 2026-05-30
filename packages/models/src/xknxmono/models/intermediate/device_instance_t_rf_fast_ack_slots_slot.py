from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class DeviceInstanceRfFastAckSlotsSlot:
    class Meta:
        global_type = False
