"""Unit tests for ComObjectParameterBlockNode.eval()'s text resolution - in particular
the ParamRefId -> Parameter.text fallback (EvalContext.get_param_ref_text /
ApplicationIndexer.resolve_parameter), added after a real ABB product was found to
give every ParameterBlock a ParamRefId pointing at a label-only "Page" Parameter
instead of setting Text/Name directly, leaving the UI to show the block's internal
Name (e.g. "Alg:_Seite Allgemein") instead of that Parameter's Text ("General")."""

from __future__ import annotations

from xknxmono.models.intermediate import ApplicationProgram
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
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.com_object_parameter_block import (
    ComObjectParameterBlockNode,
)
from xknxmono.product.parser_v2.ui import UiParameterBlock

_BASE = "M-0002_A-A075-20-4647"
_REF_PAGE = f"{_BASE}_P-1_R-1"
_PARAM_PAGE = f"{_BASE}_P-1"


def _indexer(
    parameter_refs: list[ParameterRef] | None = None,
    parameters: list[ApplicationProgramStaticParametersParameter] | None = None,
) -> ApplicationIndexer:
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
    )
    return ApplicationIndexer(app)


def _page_param(text: str) -> ApplicationProgramStaticParametersParameter:
    return ApplicationProgramStaticParametersParameter(
        id=_PARAM_PAGE, name="", text=text, parameter_type="PT", value=""
    )


def _eval_text(block: ComObjectParameterBlock, idx: ApplicationIndexer) -> str | None:
    node = ComObjectParameterBlockNode(block, children=[])
    ctx = EvalContext(GlobalState(), idx=idx)
    result = node.eval(ctx)
    assert isinstance(result[0], UiParameterBlock)
    return result[0].text


def test_text_resolves_via_param_ref_id_when_block_has_no_text_or_name() -> None:
    block = ComObjectParameterBlock(id=f"{_BASE}_PB-1", param_ref_id=_REF_PAGE)
    idx = _indexer(
        parameter_refs=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)],
        parameters=[_page_param("General")],
    )
    assert _eval_text(block, idx) == "General"


def test_own_text_takes_priority_over_param_ref_id() -> None:
    block = ComObjectParameterBlock(
        id=f"{_BASE}_PB-1", text="Explicit", param_ref_id=_REF_PAGE
    )
    idx = _indexer(
        parameter_refs=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)],
        parameters=[_page_param("General")],
    )
    assert _eval_text(block, idx) == "Explicit"


def test_falls_back_to_name_when_param_ref_id_is_dangling() -> None:
    """No ParameterRef at all matches param_ref_id - e.g. malformed manufacturer XML."""
    block = ComObjectParameterBlock(
        id=f"{_BASE}_PB-1", name="Alg:_Seite Allgemein", param_ref_id="MISSING"
    )
    idx = _indexer()
    assert _eval_text(block, idx) == "Alg:_Seite Allgemein"


def test_falls_back_to_name_when_param_ref_target_parameter_is_missing() -> None:
    """The ParameterRef exists but its target Parameter id isn't indexed."""
    block = ComObjectParameterBlock(
        id=f"{_BASE}_PB-1", name="Alg:_Seite Allgemein", param_ref_id=_REF_PAGE
    )
    idx = _indexer(parameter_refs=[ParameterRef(id=_REF_PAGE, ref_id=_PARAM_PAGE)])
    assert _eval_text(block, idx) == "Alg:_Seite Allgemein"
