from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models.intermediate.load_procedure_t import LoadProcedure


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataProceduresProcedure(LoadProcedure):
    class Meta:
        global_type = False
