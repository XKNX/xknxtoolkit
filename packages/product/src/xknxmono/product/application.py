"""`Application` — the resolution facade over a single IR application program.

It wraps one `intermediate.ApplicationProgram` (the IR is exposed directly as `.program`) and
resolves the per-program views consumers care about: com objects, parameters, parameter types,
the dynamic visibility tree, code, and load procedures.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from xknxmono.models import detect_version
from xknxmono.models.intermediate.application_program_t import ApplicationProgram
from xknxmono.models.intermediate.knx import Knx
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle

from .data import to_ir
from .parser import (
    build_app_dynamic_tree,
    extract_app_com_objects,
    extract_app_param_types,
    extract_app_param_values,
    extract_app_parameters,
)
from .parser import dynamic as dy
from .parser.com_objects import ComObject
from .parser.parameters import Parameter, ParamType

if TYPE_CHECKING:
    from xknxmono.models.intermediate.application_program_static_t_code import (
        ApplicationProgramStaticCode,
    )
    from xknxmono.models.intermediate.load_procedures_t import LoadProcedures

    from .parser.dynamic import DynamicElement, VisibleNode


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
        return extract_app_param_types(self.program)

    def parameters(self) -> list[Parameter]:
        if self._params is None:
            self._params = extract_app_parameters(self.program)
        return self._params

    def com_objects(self) -> list[ComObject]:
        return extract_app_com_objects(self.program)

    def dynamic_tree(self) -> DynamicElement | None:
        if not self._tree_built:
            self._tree = build_app_dynamic_tree(self.program)
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

    def default_values(self) -> dict[str, str]:
        """Every parameter's default value (incl. non-displayable params), keyed by ParameterRef id.
        This is the complete map the dynamic visibility tree must be evaluated against."""
        if self._values is None:
            self._values = extract_app_param_values(self.program)
        return self._values

    # --- dynamic visibility --------------------------------------------------
    def _values_or_defaults(self, values: dict[str, str] | None) -> dict[str, str]:
        if values is not None:
            return values
        return self.default_values()

    def visible_tree(self, values: dict[str, str] | None = None) -> list[VisibleNode]:
        return dy.evaluate_tree(
            self.dynamic_tree(),
            self._values_or_defaults(values),
            {p.id: p for p in self.parameters()},
        )

    def visible_parameters(
        self, values: dict[str, str] | None = None
    ) -> list[Parameter]:
        return dy.visible_parameters(self.parameters(), self.dynamic_tree(), values)

    def visible_com_objects(
        self, values: dict[str, str] | None = None
    ) -> list[ComObject]:
        return dy.filter_visible_com_objects(
            self.com_objects(), self.dynamic_tree(), self._values_or_defaults(values)
        )


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
