from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.rename_t import Rename


@dataclass(slots=True, kw_only=True)
class Rename(Rename):
    class Meta:
        global_type = False
