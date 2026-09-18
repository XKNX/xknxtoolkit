"""Unit tests for ComObjectParameterBlockNode's text resolution - in particular the
ParamRefId -> Parameter.text fallback, added after a real ABB product was found to
give every ParameterBlock a ParamRefId pointing at a label-only "Page" Parameter
instead of setting Text/Name directly, leaving the UI to show the block's internal
Name (e.g. "Alg:_Seite Allgemein") instead of that Parameter's Text ("General").

That resolution happens once in DynamicTreeBuilder._build() (like every other
ParameterRef/ComObjectRef hop there), not in eval() - so this file covers two
different things: `TestBuildTimeResolution` exercises the build-time hop itself
(including dangling-ref edge cases), and the rest exercise eval()'s priority
between an already-resolved `param_ref` and the block's own Text/Name.
"""

from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramDynamic,
    ChannelIndependentBlock,
)
from xknxmono.models.intermediate import Module as DynModule
from xknxmono.models.intermediate.application_program_channel_t import (
    ComObjectParameterBlock,
)
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_refs import (
    ApplicationProgramStaticParameterRefs,
)
from xknxmono.models.intermediate.application_program_static_t_parameters import (
    ApplicationProgramStaticParameters,
)
from xknxmono.models.intermediate.application_program_static_t_parameters_parameter import (
    ApplicationProgramStaticParametersParameter,
)
from xknxmono.models.intermediate.application_program_t_module_defs import (
    ApplicationProgramModuleDefs,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.module_def_dynamic_t import ModuleDefDynamic
from xknxmono.models.intermediate.module_def_static_t import ModuleDefStatic
from xknxmono.models.intermediate.module_def_static_t_parameter_refs import (
    ModuleDefStaticParameterRefs,
)
from xknxmono.models.intermediate.module_def_static_t_parameters import (
    ModuleDefStaticParameters,
)
from xknxmono.models.intermediate.module_def_static_t_parameters_parameter import (
    ModuleDefStaticParametersParameter,
)
from xknxmono.models.intermediate.module_def_t import ModuleDef
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.dynamic import DynamicTreeBuilder
from xknxmono.product.parser_v2.nodes import (
    EvalContext,
    GenericCollectionNode,
    GlobalState,
)
from xknxmono.product.parser_v2.nodes.com_object_parameter_block import (
    ComObjectParameterBlockNode,
)
from xknxmono.product.parser_v2.ui import UiParameterBlock

_BASE = "M-0002_A-A075-20-4647"
_REF_PAGE = f"{_BASE}_P-1_R-1"
_PARAM_PAGE = f"{_BASE}_P-1"


def _eval_text(
    node: ComObjectParameterBlockNode, idx: ApplicationIndexer
) -> str | None:
    ctx = EvalContext(GlobalState(), idx=idx)
    result = node.eval(ctx)
    assert isinstance(result[0], UiParameterBlock)
    return result[0].text


def _page_param(text: str) -> ApplicationProgramStaticParametersParameter:
    return ApplicationProgramStaticParametersParameter(
        id=_PARAM_PAGE, name="", text=text, parameter_type="PT", value=""
    )


def test_param_ref_text_used_when_block_has_no_text_or_name(
    idx: ApplicationIndexer,
) -> None:
    block = ComObjectParameterBlock(id=f"{_BASE}_PB-1")
    node = ComObjectParameterBlockNode(
        block, children=[], param_ref=_page_param("General")
    )
    assert _eval_text(node, idx) == "General"


def test_own_text_takes_priority_over_param_ref_text(idx: ApplicationIndexer) -> None:
    block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", text="Explicit")
    node = ComObjectParameterBlockNode(
        block, children=[], param_ref=_page_param("General")
    )
    assert _eval_text(node, idx) == "Explicit"


def test_name_used_when_no_text_and_no_param_ref(idx: ApplicationIndexer) -> None:
    block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", name="Alg:_Seite Allgemein")
    node = ComObjectParameterBlockNode(block, children=[], param_ref=None)
    assert _eval_text(node, idx) == "Alg:_Seite Allgemein"


def _built_block_node(app: ApplicationProgram) -> ComObjectParameterBlockNode:
    builder = DynamicTreeBuilder(app)
    # tree is _AppNode(GenericCollectionNode([ChannelNode(...)]), ...) - the
    # ChannelIndependentBlock wrapping our block gets built into a ChannelNode
    # (see DynamicTreeBuilder._build()), one level above our block's own node.
    root = builder.tree._subtree  # pyright: ignore[reportAttributeAccessIssue]
    assert isinstance(root, GenericCollectionNode)
    channel_node = root._children[0]  # pyright: ignore[reportAttributeAccessIssue]
    node = channel_node._children[0]  # pyright: ignore[reportAttributeAccessIssue]
    assert isinstance(node, ComObjectParameterBlockNode)
    return node


def _app_with_block(
    block: ComObjectParameterBlock,
    parameter_refs: list[ParameterRef] | None = None,
    parameters: list[ApplicationProgramStaticParametersParameter] | None = None,
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
        static=ApplicationProgramStatic(
            parameters=ApplicationProgramStaticParameters(
                choice=list(parameters or [])
            ),
            parameter_refs=(
                ApplicationProgramStaticParameterRefs(parameter_ref=parameter_refs)
                if parameter_refs is not None
                else None
            ),
        ),
        dynamic=ApplicationProgramDynamic(
            choice=[ChannelIndependentBlock(choice=[block])]
        ),
    )


class TestBuildTimeResolution:
    """DynamicTreeBuilder._build()'s ParamRefId -> Parameter hop, mirroring the
    ParameterRefRef/ComObjectRefRef resolution right next to it in the same method."""

    def test_resolves_param_ref_id_to_target_parameter(self) -> None:
        block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", param_ref_id=_REF_PAGE)
        app = _app_with_block(
            block,
            parameter_refs=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)],
            parameters=[_page_param("General")],
        )
        node = _built_block_node(app)
        param_ref = node._param_ref  # pyright: ignore[reportPrivateUsage]
        assert param_ref is not None
        assert param_ref.text == "General"

    def test_no_param_ref_id_resolves_to_none(self) -> None:
        block = ComObjectParameterBlock(id=f"{_BASE}_PB-1")
        node = _built_block_node(_app_with_block(block))
        assert node._param_ref is None  # pyright: ignore[reportPrivateUsage]

    def test_dangling_param_ref_id_resolves_to_none(self) -> None:
        """No ParameterRef at all matches param_ref_id - e.g. malformed manufacturer XML."""
        block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", param_ref_id="MISSING")
        node = _built_block_node(_app_with_block(block))
        assert node._param_ref is None  # pyright: ignore[reportPrivateUsage]

    def test_dangling_target_parameter_resolves_to_none(self) -> None:
        """The ParameterRef exists but its target Parameter id isn't indexed."""
        block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", param_ref_id=_REF_PAGE)
        app = _app_with_block(
            block, parameter_refs=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)]
        )
        node = _built_block_node(app)
        assert node._param_ref is None  # pyright: ignore[reportPrivateUsage]

    def test_resolves_for_a_block_nested_inside_a_module(self) -> None:
        """ComObjectParameterBlock is a valid ModuleDefDynamic child (see
        module_def_dynamic_t.py) - ApplicationIndexer merges a module's own
        parameters/parameter_refs into the same dicts as the app's own
        (_index_module_def), so the same ParamRefId -> Parameter hop must
        still work for a block living inside a module instead of at the
        top level."""
        block = ComObjectParameterBlock(id=f"{_BASE}_MD-1_PB-1", param_ref_id=_REF_PAGE)
        module_def = ModuleDef(
            id=f"{_BASE}_MD-1",
            name="",
            static=ModuleDefStatic(
                parameters=ModuleDefStaticParameters(
                    choice=[
                        ModuleDefStaticParametersParameter(
                            id=_PARAM_PAGE,
                            name="",
                            text="General",
                            parameter_type="PT",
                            value="",
                        )
                    ]
                ),
                parameter_refs=ModuleDefStaticParameterRefs(
                    parameter_ref=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)]
                ),
            ),
            dynamic=ModuleDefDynamic(choice=[block]),
        )
        module_ref = DynModule(id="MOD-1", ref_id=module_def.id, choice=[])
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
            module_defs=ApplicationProgramModuleDefs(module_def=[module_def]),
            dynamic=ApplicationProgramDynamic(
                choice=[ChannelIndependentBlock(choice=[module_ref])]
            ),
        )

        builder = DynamicTreeBuilder(app)
        root = builder.tree._subtree  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(root, GenericCollectionNode)
        channel_node = root._children[0]  # pyright: ignore[reportAttributeAccessIssue]
        module_node = channel_node._children[0]  # pyright: ignore[reportAttributeAccessIssue]
        module_subtree = module_node._subtree  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(module_subtree, GenericCollectionNode)
        node = module_subtree._children[0]  # pyright: ignore[reportAttributeAccessIssue]
        assert isinstance(node, ComObjectParameterBlockNode)
        param_ref = node._param_ref  # pyright: ignore[reportPrivateUsage]
        assert param_ref is not None
        assert param_ref.text == "General"
