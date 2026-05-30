from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class LdCtrlBaseOnError:
    class Meta:
        global_type = False
