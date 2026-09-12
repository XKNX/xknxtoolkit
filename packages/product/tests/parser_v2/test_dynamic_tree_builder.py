"""Unit tests for DynamicTreeBuilder._build()'s leaf-node branches that the real Gira
fixture's own dynamic section (used by test_dynamic.py/test_encode.py) doesn't happen to
exercise: a multi-branch Choose (default + test branches, several when entries), Repeat,
a Module referencing a module def with no dynamic section, Button, BinaryDataRef, Assign
and Rename. Builds a minimal synthetic ApplicationProgram directly - no fixture file."""

from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramDynamic,
    Assign,
    BinaryDataRef,
    Button,
    ChannelChoose,
    ChannelIndependentBlock,
    ComObjectParameterBlock,
    Rename,
    Repeat,
)
from xknxmono.models.intermediate import Module as DynModule
from xknxmono.models.intermediate.application_program_channel_t import ChannelChooseWhen
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
from xknxmono.models.intermediate.module_def_t import ModuleDef
from xknxmono.product.parser_v2.dynamic import DynamicTreeBuilder
from xknxmono.product.parser_v2.nodes import (
    AssignNode,
    ButtonNode,
    ChooseWhenNode,
    GenericCollectionNode,
    RenameNode,
    RepeatNode,
)
from xknxmono.product.parser_v2.nodes.binary_data_ref import BinaryDataRefNode

_BASE = "M-0008_A-7072-21-5CC3-O000A"


def _app() -> ApplicationProgram:
    module_def_no_dynamic = ModuleDef(
        id="MD-NODYN", name="", static=ModuleDefStatic(), dynamic=None
    )
    block = ComObjectParameterBlock(
        id=f"{_BASE}_PB-1",
        choice=[
            Button(id=f"{_BASE}_BTN-1", text="Go"),
            BinaryDataRef(ref_id=f"{_BASE}_BD-1"),
            Assign(target_param_ref_ref=f"{_BASE}_P-1_R-1", value="1"),
        ],
    )
    choose = ChannelChoose(
        param_ref_id=f"{_BASE}_P-2_R-2",
        when=[
            ChannelChooseWhen(
                default=True, choice=[Rename(id="RN-1", ref_id="CO-1", text="Renamed")]
            ),
            ChannelChooseWhen(test="1", choice=[]),
        ],
    )
    repeat = Repeat(id="RPT-1", name="Repeat", choice=[], count=2)
    module_ref = DynModule(id="MOD-1", ref_id="MD-NODYN", choice=[])

    unrecognized = object()  # not a valid schema type; exercises _build()'s fallback
    dynamic = ApplicationProgramDynamic(
        choice=[
            ChannelIndependentBlock(
                choice=[block, choose, repeat, module_ref, unrecognized]  # pyright: ignore[reportArgumentType]
            ),
        ]
    )

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
        static=ApplicationProgramStatic(),
        module_defs=ApplicationProgramModuleDefs(module_def=[module_def_no_dynamic]),
        dynamic=dynamic,
    )


def test_builds_without_error() -> None:
    builder = DynamicTreeBuilder(_app())
    assert builder.tree is not None


def _channel_independent_children() -> list[object]:
    builder = DynamicTreeBuilder(_app())
    # tree is _AppNode(GenericCollectionNode([ChannelNode(...)]), ...)
    app_node = builder.tree
    root = app_node._subtree  # pyright: ignore[reportAttributeAccessIssue]
    assert isinstance(root, GenericCollectionNode)
    channel_node = root._children[0]  # pyright: ignore[reportAttributeAccessIssue]
    return channel_node._children  # pyright: ignore[reportAttributeAccessIssue]


def test_button_binary_data_ref_and_assign_are_built() -> None:
    children = _channel_independent_children()
    block_node = children[0]
    from xknxmono.product.parser_v2.nodes import ComObjectParameterBlockNode

    assert isinstance(block_node, ComObjectParameterBlockNode)
    inner = block_node._children  # pyright: ignore[reportAttributeAccessIssue]
    assert isinstance(inner[0], ButtonNode)
    assert isinstance(inner[1], BinaryDataRefNode)
    assert isinstance(inner[2], AssignNode)


def test_choose_with_default_and_test_branches_is_built() -> None:
    children = _channel_independent_children()
    choose_node = children[1]
    assert isinstance(choose_node, ChooseWhenNode)


def test_rename_inside_choose_default_branch_is_built() -> None:
    children = _channel_independent_children()
    choose_node = children[1]
    assert isinstance(choose_node, ChooseWhenNode)
    default_nodes = choose_node._default_nodes  # pyright: ignore[reportAttributeAccessIssue]
    assert default_nodes is not None
    assert isinstance(default_nodes[0], RenameNode)


def test_repeat_is_built() -> None:
    children = _channel_independent_children()
    assert isinstance(children[2], RepeatNode)


def test_module_with_no_dynamic_section_builds_to_none() -> None:
    builder = DynamicTreeBuilder(_app())
    assert builder.idx.module_defs["MD-NODYN"].dynamic is None
    children = _channel_independent_children()
    # None children are filtered out at eval time, not build time (see GenericCollectionNode).
    assert children[-2] is None


def test_unrecognized_element_builds_to_none() -> None:
    children = _channel_independent_children()
    assert children[-1] is None
