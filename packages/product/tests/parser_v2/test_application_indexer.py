"""Unit tests for ApplicationIndexer's static-section indexing, filling gaps not already
exercised through encode.py's/dynamic.py's own tests: an empty static section (every "if X
is not None" false branch), the script field, segment_base_addr's unknown-id fallback, a
module def with an empty id, real allocators/arguments, and nested sub_module_defs."""

from __future__ import annotations

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.allocator_t import Allocator as IrAllocator
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_script import (
    ApplicationProgramStaticScript,
)
from xknxmono.models.intermediate.application_program_t_module_defs import (
    ApplicationProgramModuleDefs,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.module_def_static_t import ModuleDefStatic
from xknxmono.models.intermediate.module_def_static_t_allocators import (
    ModuleDefStaticAllocators,
)
from xknxmono.models.intermediate.module_def_t import ModuleDef, ModuleDefSubModuleDefs
from xknxmono.models.intermediate.module_def_t_arguments import ModuleDefArguments
from xknxmono.models.intermediate.module_def_t_arguments_argument import (
    ModuleDefArgumentsArgument,
)
from xknxmono.models.intermediate.module_def_t_arguments_argument_alignment import (
    ModuleDefArgumentsArgumentAlignment,
)
from xknxmono.product.parser_v2.allocator import Allocator
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer


def _app(
    static: ApplicationProgramStatic | None = None,
    module_defs: list[ModuleDef] | None = None,
) -> ApplicationProgram:
    return ApplicationProgram(
        id="APP",
        name="",
        application_number=1,
        application_version=1,
        program_type=ApplicationProgramType.APPLICATION_PROGRAM,
        mask_version="BV20",
        load_procedure_style=LoadProcedureStyle.DEFAULT_PROCEDURE,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=static or ApplicationProgramStatic(),
        module_defs=(
            ApplicationProgramModuleDefs(module_def=module_defs)
            if module_defs is not None
            else None
        ),
    )


def test_empty_static_section_indexes_nothing() -> None:
    idx = ApplicationIndexer(_app())
    assert idx.code_segments == {}
    assert idx.parameter_types == {}
    assert idx.parameters == {}
    assert idx.script is None


def test_script_value_is_indexed() -> None:
    static = ApplicationProgramStatic(
        script=ApplicationProgramStaticScript(value="1+1")
    )
    idx = ApplicationIndexer(_app(static))
    assert idx.script == "1+1"


def test_script_empty_value_is_none() -> None:
    static = ApplicationProgramStatic(script=ApplicationProgramStaticScript(value=""))
    idx = ApplicationIndexer(_app(static))
    assert idx.script is None


def test_segment_base_addr_unknown_segment_returns_zero() -> None:
    idx = ApplicationIndexer(_app())
    assert idx.segment_base_addr("NO_SUCH_SEG") == 0


def test_module_def_with_empty_id_is_not_registered() -> None:
    md = ModuleDef(id="", name="", static=ModuleDefStatic())
    idx = ApplicationIndexer(_app(module_defs=[md]))
    assert idx.module_defs == {}


def test_module_def_allocators_and_arguments_are_indexed() -> None:
    md = ModuleDef(
        id="MD1",
        name="",
        static=ModuleDefStatic(
            allocators=ModuleDefStaticAllocators(
                allocator=[
                    IrAllocator(id="L-1", name="Alloc", start=100, max_inclusive=199)
                ]
            )
        ),
        arguments=ModuleDefArguments(
            argument=[
                ModuleDefArgumentsArgument(
                    id="A-1",
                    name="Arg",
                    allocates=3,
                    alignment=ModuleDefArgumentsArgumentAlignment.VALUE_4,
                )
            ]
        ),
    )
    idx = ApplicationIndexer(_app(module_defs=[md]))
    assert idx.allocators["MD1"].keys() == {"L-1"}
    assert isinstance(idx.allocators["MD1"]["L-1"], Allocator)
    assert idx.allocators["MD1"]["L-1"].start == 100
    assert idx.arg_alloc["MD1"] == {"A-1": (3, 4)}


def test_module_def_argument_without_allocates_defaults_to_one() -> None:
    md = ModuleDef(
        id="MD1",
        name="",
        static=ModuleDefStatic(),
        arguments=ModuleDefArguments(
            argument=[
                ModuleDefArgumentsArgument(
                    id="A-1",
                    name="Arg",
                    alignment=ModuleDefArgumentsArgumentAlignment.VALUE_1,
                )
            ]
        ),
    )
    idx = ApplicationIndexer(_app(module_defs=[md]))
    assert idx.arg_alloc["MD1"] == {"A-1": (1, 1)}


def test_nested_sub_module_defs_are_indexed() -> None:
    child = ModuleDef(id="MD1_SM-1_MD2", name="", static=ModuleDefStatic())
    parent = ModuleDef(
        id="MD1",
        name="",
        static=ModuleDefStatic(),
        sub_module_defs=ModuleDefSubModuleDefs(module_def=[child]),
    )
    idx = ApplicationIndexer(_app(module_defs=[parent]))
    assert idx.module_defs.keys() == {"MD1", "MD1_SM-1_MD2"}
