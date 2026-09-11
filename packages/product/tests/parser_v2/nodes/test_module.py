"""Unit tests for ModuleNode's argument resolution (_resolve_arguments/_resolved_base):
base_value chaining, allocator-backed args, and the plain base-offset add."""

from __future__ import annotations

from xknxmono.models.intermediate import ApplicationProgram, ModuleTextArg
from xknxmono.models.intermediate.allocator_t import Allocator as IrAllocator
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
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
from xknxmono.models.intermediate.module_def_t import ModuleDef
from xknxmono.models.intermediate.module_def_t_arguments import ModuleDefArguments
from xknxmono.models.intermediate.module_def_t_arguments_argument import (
    ModuleDefArgumentsArgument,
)
from xknxmono.models.intermediate.module_def_t_arguments_argument_alignment import (
    ModuleDefArgumentsArgumentAlignment,
)
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.module import (
    _resolve_arguments,  # pyright: ignore[reportPrivateUsage]
    _resolved_base,  # pyright: ignore[reportPrivateUsage]
)


def _indexer_with_allocator(
    def_id: str, alloc_id: str, arg_ids: list[str]
) -> ApplicationIndexer:
    md = ModuleDef(
        id=def_id,
        name="",
        static=ModuleDefStatic(
            allocators=ModuleDefStaticAllocators(
                allocator=[
                    IrAllocator(id=alloc_id, name="", start=100, max_inclusive=199)
                ]
            )
        ),
        arguments=ModuleDefArguments(
            argument=[
                ModuleDefArgumentsArgument(
                    id=arg_id,
                    name="",
                    allocates=1,
                    alignment=ModuleDefArgumentsArgumentAlignment.VALUE_1,
                )
                for arg_id in arg_ids
            ]
        ),
    )
    app = ApplicationProgram(
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
        static=ApplicationProgramStatic(),
        module_defs=ApplicationProgramModuleDefs(module_def=[md]),
    )
    return ApplicationIndexer(app)


def test_resolved_base_missing_ref_is_zero() -> None:
    assert _resolved_base("A-1", {}) == 0


def test_resolved_base_non_numeric_arg_is_zero() -> None:
    args = {"A-1": ModuleTextArg(ref_id="A-1", id="a1", value="x")}
    assert _resolved_base("A-1", args) == 0


def test_resolved_base_returns_numeric_value() -> None:
    args = {"A-1": ModuleNumericArg(ref_id="A-1", value=7)}
    assert _resolved_base("A-1", args) == 7


def test_resolve_arguments_base_value_chains_to_another_arg() -> None:
    args = {
        "A-1": ModuleNumericArg(ref_id="A-1", value=5),
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
    }
    ctx = EvalContext(GlobalState())
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert resolved["A-2"].value == 15  # pyright: ignore[reportAttributeAccessIssue]


def test_resolve_arguments_allocator_backed_arg() -> None:
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1"])
    ctx = EvalContext(GlobalState(), idx=idx)
    args = {"A-1": ModuleNumericArg(ref_id="A-1", allocator_ref_id="L-1")}
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert resolved["A-1"].value == 100  # pyright: ignore[reportAttributeAccessIssue]


def test_resolve_arguments_allocator_backed_arg_with_base() -> None:
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1", "A-2"])
    ctx = EvalContext(GlobalState(), idx=idx)
    args = {
        "A-1": ModuleNumericArg(ref_id="A-1", value=3),
        "A-2": ModuleNumericArg(ref_id="A-2", allocator_ref_id="L-1", base_value="A-1"),
    }
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert resolved["A-2"].value == 103  # pyright: ignore[reportAttributeAccessIssue]
