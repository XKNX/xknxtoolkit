from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.locations_t import Locations


@dataclass(slots=True, kw_only=True)
class Buildings(Locations):
    class Meta:
        global_type = False
