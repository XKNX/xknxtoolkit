from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.com_object_t import ComObject


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticComObjectsComObject(ComObject):
    class Meta:
        global_type = False
