from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.segment_base_t import SegmentBase


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticCodeAbsoluteSegment(SegmentBase):
    class Meta:
        global_type = False
