"""Unit tests for DynamicUI.set_parameter_ref()'s L<->R calculation propagation edge
cases that the real Gira fixture (used by test_dynamic.py) doesn't happen to exercise:
a VBScript calculation (evaluate_lr/evaluate_rl raise NotImplementedError, which
set_parameter_ref must swallow and skip) and a calculation whose transformation leaves
one of its declared outputs unset (which must clear that output, not just skip writing
it). The "partial result" contract is asserted for both dispatch paths: the named-
function path (LRTransformationFunc/RLTransformationFunc) and the inline-script path
(LRTransformation/RLTransformation), since the two paths read back unset outputs
differently under dukpy and only the named-function path was previously covered.
Builds a minimal synthetic ApplicationProgram wired with real ParameterCalculation
entries - verified interactively against the real DynamicUI before writing assertions,
since the exact wiring (which ref_id calculations key off) isn't obvious from the source
alone."""

from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramDynamic,
    CalculationParameterRef,
    ChannelIndependentBlock,
    ComObjectParameterBlock,
    ParameterCalculation,
    ParameterCalculationLanguage,
    ParameterCalculationLparameters,
    ParameterCalculationRparameters,
    ParameterRefRef,
)
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_calculations import (
    ApplicationProgramStaticParameterCalculations,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_refs import (
    ApplicationProgramStaticParameterRefs,
)
from xknxmono.models.intermediate.application_program_static_t_parameter_types import (
    ApplicationProgramStaticParameterTypes,
)
from xknxmono.models.intermediate.application_program_static_t_parameters import (
    ApplicationProgramStaticParameters,
)
from xknxmono.models.intermediate.application_program_static_t_parameters_parameter import (
    ApplicationProgramStaticParametersParameter,
)
from xknxmono.models.intermediate.application_program_static_t_script import (
    ApplicationProgramStaticScript,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.models.intermediate.parameter_type_t import ParameterType
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_number_type import (
    ParameterTypeTypeNumberType,
)
from xknxmono.product.parser_v2.dynamic import DynamicUI

# PR-X is the only "real" (active, UI-visible) parameter ref on the named-function side.
# It's the L-side of two calculations (a VBScript one, skipped; a JS one producing PR-A
# but leaving PR-B unset) and the R-side of two more (VBScript, skipped; JS producing
# PR-C but leaving PR-D unset). PR-A/B/C/D never need to be real parameters - the calc
# engine only reads/writes them as bare state keys.
# PR-Y mirrors PR-X for the inline-script side: it's the L-side of an inline JS calc
# producing PR-E but leaving PR-F unset, and the R-side of an inline JS calc producing
# PR-G but leaving PR-H unset. These exercise the inline dispatch path, where —
# under dukpy — a declared-but-unset output is JS `undefined` and marshals to a Python
# `dict()`, which `_read_js_var` stringifies as "{}" unless the output is pre-initialised
# to `null` (the fix under test). The contract: the unset output must be cleared
# (revert to static default), not written verbatim as the literal string "{}".
_SCRIPT = "function toR(i,o,c){o.ra=1;} function toL(i,o,c){o.lc=1;}"


def _ref(ref_id: str, alias_name: str | None = None) -> CalculationParameterRef:
    return CalculationParameterRef(ref_id=ref_id, alias_name=alias_name)


def _app() -> ApplicationProgram:
    pt = ParameterType(
        id="PT1",
        name="T",
        choice=ParameterTypeTypeNumber(
            size_in_bit=8,
            type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
            min_inclusive=0,
            max_inclusive=255,
        ),
    )
    p_x = ApplicationProgramStaticParametersParameter(
        id="P-X", name="", text="", parameter_type="PT1", value="0"
    )
    pr_x = ParameterRef(id="PR-X", ref_id="P-X")
    p_y = ApplicationProgramStaticParametersParameter(
        id="P-Y", name="", text="", parameter_type="PT1", value="0"
    )
    pr_y = ParameterRef(id="PR-Y", ref_id="P-Y")

    calc_l_vbscript = ParameterCalculation(
        id="C1",
        name="",
        language=ParameterCalculationLanguage.VBSCRIPT,
        lparameters=ParameterCalculationLparameters(parameter_ref_ref=[_ref("PR-X")]),
        rparameters=ParameterCalculationRparameters(parameter_ref_ref=[_ref("PR-A")]),
    )
    calc_l_js_partial = ParameterCalculation(
        id="C2",
        name="",
        language=ParameterCalculationLanguage.JAVA_SCRIPT,
        lrtransformation_func="toR",
        lparameters=ParameterCalculationLparameters(
            parameter_ref_ref=[_ref("PR-X", "lx")]
        ),
        rparameters=ParameterCalculationRparameters(
            parameter_ref_ref=[_ref("PR-A", "ra"), _ref("PR-B", "rb")]
        ),
    )
    calc_r_vbscript = ParameterCalculation(
        id="C3",
        name="",
        language=ParameterCalculationLanguage.VBSCRIPT,
        rparameters=ParameterCalculationRparameters(parameter_ref_ref=[_ref("PR-X")]),
        lparameters=ParameterCalculationLparameters(parameter_ref_ref=[_ref("PR-C")]),
    )
    calc_r_js_partial = ParameterCalculation(
        id="C4",
        name="",
        language=ParameterCalculationLanguage.JAVA_SCRIPT,
        rltransformation_func="toL",
        rparameters=ParameterCalculationRparameters(
            parameter_ref_ref=[_ref("PR-X", "rx")]
        ),
        lparameters=ParameterCalculationLparameters(
            parameter_ref_ref=[_ref("PR-C", "lc"), _ref("PR-D", "ld")]
        ),
    )
    calc_l_js_inline = ParameterCalculation(
        id="C5",
        name="",
        language=ParameterCalculationLanguage.JAVA_SCRIPT,
        lrtransformation="re = 2;",  # sets PR-E, leaves PR-F unset
        lparameters=ParameterCalculationLparameters(
            parameter_ref_ref=[_ref("PR-Y", "ly")]
        ),
        rparameters=ParameterCalculationRparameters(
            parameter_ref_ref=[_ref("PR-E", "re"), _ref("PR-F", "rf")]
        ),
    )
    calc_r_js_inline = ParameterCalculation(
        id="C6",
        name="",
        language=ParameterCalculationLanguage.JAVA_SCRIPT,
        rltransformation="rg = 3;",  # sets PR-G, leaves PR-H unset
        rparameters=ParameterCalculationRparameters(
            parameter_ref_ref=[_ref("PR-Y", "ry")]
        ),
        lparameters=ParameterCalculationLparameters(
            parameter_ref_ref=[_ref("PR-G", "rg"), _ref("PR-H", "rh")]
        ),
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
        static=ApplicationProgramStatic(
            parameters=ApplicationProgramStaticParameters(choice=[p_x, p_y]),
            parameter_types=ApplicationProgramStaticParameterTypes(parameter_type=[pt]),
            parameter_refs=ApplicationProgramStaticParameterRefs(
                parameter_ref=[pr_x, pr_y]
            ),
            parameter_calculations=ApplicationProgramStaticParameterCalculations(
                parameter_calculation=[
                    calc_l_vbscript,
                    calc_l_js_partial,
                    calc_r_vbscript,
                    calc_r_js_partial,
                    calc_l_js_inline,
                    calc_r_js_inline,
                ]
            ),
            script=ApplicationProgramStaticScript(value=_SCRIPT),
        ),
        dynamic=ApplicationProgramDynamic(
            choice=[
                ChannelIndependentBlock(
                    choice=[
                        ComObjectParameterBlock(
                            id="PB-1",
                            choice=[
                                ParameterRefRef(ref_id="PR-X"),
                                ParameterRefRef(ref_id="PR-Y"),
                            ],
                        )
                    ]
                )
            ]
        ),
    )


def _dui() -> DynamicUI:
    dui = DynamicUI(_app())
    dui.ui()  # marks PR-X and PR-Y active
    return dui


def test_vbscript_calculation_is_skipped_without_error() -> None:
    dui = _dui()
    dui.set_parameter_ref("PR-X", "5")  # must not raise despite calc_l/r_vbscript


def test_l_to_r_partial_result_sets_and_clears() -> None:
    dui = _dui()
    dui.set_parameter_ref("PR-X", "5")
    assert dui._state.get("PR-A") == "1"  # pyright: ignore[reportPrivateUsage]
    assert dui._state.get("PR-B") is None  # pyright: ignore[reportPrivateUsage]


def test_r_to_l_partial_result_sets_and_clears() -> None:
    dui = _dui()
    dui.set_parameter_ref("PR-X", "5")
    assert dui._state.get("PR-C") == "1"  # pyright: ignore[reportPrivateUsage]
    assert dui._state.get("PR-D") is None  # pyright: ignore[reportPrivateUsage]


def test_l_to_r_inline_partial_result_sets_and_clears() -> None:
    # The inline LRTransformation ("re = 2;") sets only the first declared R-output;
    # the second (PR-F) is left unset and must be cleared (no override), not left as
    # the literal "{}" that a bare `var rf;` would marshal to under dukpy. Mirrors
    # test_l_to_r_partial_result_sets_and_clears for the inline dispatch path, which
    # the named-function-only coverage previously didn't exercise.
    dui = _dui()
    dui.set_parameter_ref("PR-Y", "5")
    assert dui._state.get("PR-E") == "2"  # pyright: ignore[reportPrivateUsage]
    assert dui._state.get("PR-F") is None  # pyright: ignore[reportPrivateUsage]


def test_r_to_l_inline_partial_result_sets_and_clears() -> None:
    # The inline RLTransformation ("rg = 3;") sets only the first declared L-output;
    # the second (PR-H) is left unset and must be cleared (no override), not left as
    # the literal "{}". Mirrors test_r_to_l_partial_result_sets_and_clears for the
    # inline dispatch path.
    dui = _dui()
    dui.set_parameter_ref("PR-Y", "5")
    assert dui._state.get("PR-G") == "3"  # pyright: ignore[reportPrivateUsage]
    assert dui._state.get("PR-H") is None  # pyright: ignore[reportPrivateUsage]
