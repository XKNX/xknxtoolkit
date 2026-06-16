from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramStaticParametersUnion,
    ModuleDef,
    ModuleDefStaticParametersUnion,
    ParameterType,
)
from xknxmono.models.intermediate.parameter_base_t import ParameterBase
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef


class ApplicationIndexer:
    """Pre-built lookup tables for static IR sections (parameters, parameter refs, parameter types, module defs)."""

    __slots__ = ("module_defs", "parameter_refs", "parameters", "parameter_types")

    def __init__(self, app: ApplicationProgram) -> None:
        self.module_defs: dict[str, ModuleDef] = {}
        self.parameter_refs: dict[str, ParameterRef] = {}
        self.parameters: dict[str, ParameterBase] = {}
        self.parameter_types: dict[str, ParameterType] = {}
        self._index_app(app)
        if app.module_defs is not None:
            for md in app.module_defs.module_def:
                self._index_module_def(md)

    def _index_app(self, app: ApplicationProgram) -> None:
        s = app.static
        if s.parameter_types is not None:
            for pt in s.parameter_types.parameter_type:
                self.parameter_types[pt.id] = pt
        if s.parameters is not None:
            for p in s.parameters.choice:
                if isinstance(p, ApplicationProgramStaticParametersUnion):
                    for up in p.parameter:
                        self.parameters[up.id] = up
                else:
                    self.parameters[p.id] = p
        if s.parameter_refs is not None:
            for pr in s.parameter_refs.parameter_ref:
                self.parameter_refs[pr.id] = pr

    def _index_module_def(self, md: ModuleDef) -> None:
        if md.id:
            self.module_defs[md.id] = md
        if md.static.parameters is not None:
            for p in md.static.parameters.choice:
                if isinstance(p, ModuleDefStaticParametersUnion):
                    for up in p.parameter:
                        self.parameters[up.id] = up
                else:
                    self.parameters[p.id] = p
        if md.static.parameter_refs is not None:
            for pr in md.static.parameter_refs.parameter_ref:
                self.parameter_refs[pr.id] = pr
        if md.sub_module_defs is not None:
            for sub in md.sub_module_defs.module_def:
                self._index_module_def(sub)
