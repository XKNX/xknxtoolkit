from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticBinaryDataExcludeProperty:
    class Meta:
        global_type = False
