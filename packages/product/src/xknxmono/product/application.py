"""`Application` — the resolution facade over a single IR application program.

It wraps one `intermediate.ApplicationProgram` (the IR is exposed directly as `.program`) and
resolves the per-program views consumers care about: com objects, parameters, parameter types,
the dynamic visibility tree, code, and load procedures.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

from xknxmono.models import detect_version

from .data import to_ir

if TYPE_CHECKING:
    from xknxmono.models.intermediate.application_program_static_t_code import (
        ApplicationProgramStaticCode,
    )
    from xknxmono.models.intermediate.application_program_t import ApplicationProgram
    from xknxmono.models.intermediate.knx import Knx
    from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
    from xknxmono.models.intermediate.load_procedures_t import LoadProcedures

    from .parser.com_objects import ComObject
    from .parser.dynamic import DynamicElement, VisibleNode
    from .parser.parameters import Parameter, ParamType
    from .parser_v2.dynamic import DynamicUI


@dataclass(slots=True)
class Application:
    """One application program, resolved on demand. `program` is the raw IR; the methods return
    the computed value types."""

    program: ApplicationProgram
    version: str
    manufacturer_id: str
    _params: list[Parameter] | None = field(default=None, repr=False, compare=False)
    _values: dict[str, str] | None = field(default=None, repr=False, compare=False)
    _tree: DynamicElement | None = field(default=None, repr=False, compare=False)
    _tree_built: bool = field(default=False, repr=False, compare=False)

    @property
    def id(self) -> str:
        return self.program.id

    @property
    def name(self) -> str:
        return self.program.name or self.program.id

    # --- resolved views ------------------------------------------------------
    def param_types(self) -> dict[str, ParamType]:
        from .parser.parameters import extract_types as _extract_types
        return _extract_types(self.program)

    def parameters(self) -> list[Parameter]:
        if self._params is None:
            from .parser.parameters import extract as _extract_params
            self._params = _extract_params(self.program)
        return self._params

    def com_objects(self) -> list[ComObject]:
        from .parser.com_objects import extract as _extract_com_objects
        return _extract_com_objects(self.program)

    def dynamic_tree(self) -> DynamicElement | None:
        if not self._tree_built:
            from .parser.dynamic import build_app_dynamic_tree as _build_tree
            self._tree = _build_tree(self.program)
            self._tree_built = True
        return self._tree

    @property
    def code(self) -> ApplicationProgramStaticCode | None:
        return self.program.static.code if self.program.static else None

    @property
    def load_procedures(self) -> LoadProcedures | None:
        return self.program.static.load_procedures if self.program.static else None

    @property
    def load_procedure_style(self) -> LoadProcedureStyle | None:
        return self.program.load_procedure_style

    def dynamic_ui(self) -> DynamicUI | None:
        """Create a fresh DynamicUI for this application. Returns None if the application has no
        dynamic section. The caller owns the returned instance and its embedded GlobalState."""
        if self.program.dynamic is None:
            return None
        from .parser_v2.dynamic import DynamicUI as _DynamicUI
        return _DynamicUI(self.program)

    def default_values(self) -> dict[str, str]:
        """Every parameter's default value (incl. non-displayable params), keyed by ParameterRef id.
        This is the complete map the dynamic visibility tree must be evaluated against."""
        if self._values is None:
            from .parser.parameters import extract_values as _extract_values
            self._values = _extract_values(self.program)
        return self._values

    # --- dynamic visibility --------------------------------------------------
    def _values_or_defaults(self, values: dict[str, str] | None) -> dict[str, str]:
        if values is not None:
            return values
        return self.default_values()

    def visible_tree(self, values: dict[str, str] | None = None) -> list[VisibleNode]:
        from .parser import dynamic as _dy
        return _dy.evaluate_tree(
            self.dynamic_tree(),
            self._values_or_defaults(values),
            {p.id: p for p in self.parameters()},
        )

    def visible_parameters(
        self, values: dict[str, str] | None = None
    ) -> list[Parameter]:
        from .parser import dynamic as _dy
        return _dy.visible_parameters(self.parameters(), self.dynamic_tree(), values)

    def visible_com_objects(
        self, values: dict[str, str] | None = None
    ) -> list[ComObject]:
        from .parser import dynamic as _dy
        resolved = self._values_or_defaults(values)
        visible = _dy.filter_visible_com_objects(
            self.com_objects(), self.dynamic_tree(), resolved
        )
        return [_named(co, resolved) for co in visible]


def _named(co: ComObject, values: dict[str, str]) -> ComObject:
    """Fill a com-object's name placeholder from its name parameter's current value."""
    if not co.name_param_ref_id:
        return co
    from .parser.modules import fill_name as _fill_name
    name = _fill_name(co.name_template, values.get(co.name_param_ref_id, ""))
    return replace(co, name=name) if name != co.name else co


def _programs(knx: Knx) -> Iterator[ApplicationProgram]:
    if knx.manufacturer_data is None:
        return
    for manufacturer in knx.manufacturer_data.manufacturer:
        if manufacturer.application_programs is not None:
            yield from manufacturer.application_programs.application_program


def parse_application_xml(xml_bytes: bytes, manufacturer_id: str) -> list[Application]:
    """Load a single application XML in isolation (no hardware/catalog context)."""
    version = detect_version(xml_bytes)
    knx = to_ir(xml_bytes, version)
    return [
        Application(program=p, version=version, manufacturer_id=manufacturer_id)
        for p in _programs(knx)
    ]
