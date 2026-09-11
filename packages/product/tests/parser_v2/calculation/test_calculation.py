"""Tests for parser_v2.calculation: the L<->R parameter-calculation engine that
runs real JavaScript (via dukpy) to compute one set of parameter values from
another, as declared in a KNX product's ParameterCalculation blocks.
"""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import (
    CalculationParameterRef,
    ParameterCalculation,
    ParameterCalculationLanguage,
    ParameterCalculationLparameters,
    ParameterCalculationRparameters,
)
from xknxmono.product.parser_v2.calculation import evaluate_lr, evaluate_rl
from xknxmono.product.parser_v2.calculation._js import (
    eval_inline,
    eval_named_func,
)


def _ref(ref_id: str, alias_name: str | None = None) -> CalculationParameterRef:
    return CalculationParameterRef(ref_id=ref_id, alias_name=alias_name)


def _calc(
    *,
    lrtransformation: str | None = None,
    lrtransformation_func: str | None = None,
    lrtransformation_parameters: str | None = None,
    rltransformation: str | None = None,
    rltransformation_func: str | None = None,
    rltransformation_parameters: str | None = None,
    lparams: list[CalculationParameterRef] | None = None,
    rparams: list[CalculationParameterRef] | None = None,
    language: ParameterCalculationLanguage = ParameterCalculationLanguage.JAVA_SCRIPT,
) -> ParameterCalculation:
    return ParameterCalculation(
        id="calc-1",
        name="Test Calc",
        language=language,
        lparameters=ParameterCalculationLparameters(parameter_ref_ref=lparams or []),
        rparameters=ParameterCalculationRparameters(parameter_ref_ref=rparams or []),
        lrtransformation=lrtransformation,
        lrtransformation_func=lrtransformation_func,
        lrtransformation_parameters=lrtransformation_parameters,
        rltransformation=rltransformation,
        rltransformation_func=rltransformation_func,
        rltransformation_parameters=rltransformation_parameters,
    )


# --- _js.eval_inline -----------------------------------------------------


def test_eval_inline_basic_arithmetic() -> None:
    result = eval_inline("y = x + 1;", {"x": "5"}, ["y"])
    assert result == {"y": "6"}


def test_eval_inline_string_concatenation() -> None:
    result = eval_inline("y = x + '!';", {"x": "hi"}, ["y"])
    assert result == {"y": "hi!"}


def test_eval_inline_whole_number_float_becomes_int_string() -> None:
    result = eval_inline("y = x * 2;", {"x": "2.5"}, ["y"])
    assert result == {"y": "5"}


def test_eval_inline_fractional_float_stays_fractional() -> None:
    result = eval_inline("y = x * 1.5;", {"x": "2.5"}, ["y"])
    assert result == {"y": "3.75"}


def test_eval_inline_declared_but_unset_output_reads_back_as_empty_object() -> None:
    # Unlike eval_named_func's outputs (real JS `undefined`, filtered out below),
    # a bare `var y;` hoisted declaration evaluated on its own reads back through
    # dukpy as `{}`, not `None` - so it is *not* excluded. Documenting the actual
    # behavior rather than the (wrong) assumption that it would be.
    result = eval_inline("var unused = 1;", {}, ["y"])
    assert result == {"y": "{}"}


def test_eval_inline_multiple_outputs() -> None:
    result = eval_inline(
        "sum = a + b; diff = a - b;", {"a": "5", "b": "3"}, ["sum", "diff"]
    )
    assert result == {"sum": "8", "diff": "2"}


# --- _js.eval_named_func ---------------------------------------------------


def test_eval_named_func_basic() -> None:
    script = "function calc(i, o, c) { o.result = i.a + i.b; }"
    result = eval_named_func(script, "calc", None, {"a": "3", "b": "4"}, ["result"])
    assert result == {"result": "7"}


def test_eval_named_func_uses_context_parameters() -> None:
    script = "function calc(i, o, c) { o.result = i.a * c.factor; }"
    result = eval_named_func(script, "calc", '{"factor": 3}', {"a": "10"}, ["result"])
    assert result == {"result": "30"}


def test_eval_named_func_unset_output_is_excluded() -> None:
    script = "function calc(i, o, c) { /* doesn't touch o.result */ }"
    result = eval_named_func(script, "calc", None, {}, ["result"])
    assert result == {}


# --- evaluate_lr / evaluate_rl: dispatch and error handling ---------------


def test_evaluate_lr_vbscript_raises_not_implemented() -> None:
    calc = _calc(language=ParameterCalculationLanguage.VBSCRIPT)
    with pytest.raises(NotImplementedError):
        evaluate_lr(calc, {})


def test_evaluate_rl_vbscript_raises_not_implemented() -> None:
    calc = _calc(language=ParameterCalculationLanguage.VBSCRIPT)
    with pytest.raises(NotImplementedError):
        evaluate_rl(calc, {})


def test_evaluate_lr_with_no_transformation_returns_empty() -> None:
    calc = _calc()
    assert evaluate_lr(calc, {"x": "1"}) == {}


def test_evaluate_rl_with_no_transformation_returns_empty() -> None:
    calc = _calc()
    assert evaluate_rl(calc, {"x": "1"}) == {}


def test_evaluate_lr_func_without_script_asserts() -> None:
    calc = _calc(lrtransformation_func="calc")
    with pytest.raises(AssertionError):
        evaluate_lr(calc, {"x": "1"}, script=None)


def test_evaluate_rl_func_without_script_asserts() -> None:
    calc = _calc(rltransformation_func="calc")
    with pytest.raises(AssertionError):
        evaluate_rl(calc, {"x": "1"}, script=None)


# --- evaluate_lr / evaluate_rl: real transformations -----------------------


def test_evaluate_lr_inline_uses_rparameter_alias_names() -> None:
    calc = _calc(
        lrtransformation="celsius = (fahrenheit_in - 32) * 5 / 9;",
        rparams=[_ref("R-1", alias_name="celsius")],
    )
    result = evaluate_lr(calc, {"fahrenheit_in": "32"})
    assert result == {"celsius": "0"}


def test_evaluate_lr_inline_falls_back_to_ref_id_without_alias() -> None:
    calc = _calc(
        lrtransformation="R1 = x * 2;",
        rparams=[_ref("R1")],
    )
    result = evaluate_lr(calc, {"x": "5"})
    assert result == {"R1": "10"}


def test_evaluate_lr_named_func() -> None:
    script = "function toPercent(i, o, c) { o.pct = i.raw / 2.55; }"
    calc = _calc(
        lrtransformation_func="toPercent",
        rparams=[_ref("R-1", alias_name="pct")],
    )
    result = evaluate_lr(calc, {"raw": "255"}, script=script)
    assert result == {"pct": "100"}


def test_evaluate_rl_inline_uses_lparameter_alias_names() -> None:
    calc = _calc(
        rltransformation="fahrenheit_out = celsius * 2;",
        lparams=[_ref("L-1", alias_name="fahrenheit_out")],
    )
    result = evaluate_rl(calc, {"celsius": "10"})
    assert result == {"fahrenheit_out": "20"}


def test_evaluate_rl_named_func() -> None:
    script = "function toRaw(i, o, c) { o.raw = i.pct * 2; }"
    calc = _calc(
        rltransformation_func="toRaw",
        lparams=[_ref("L-1", alias_name="raw")],
    )
    result = evaluate_rl(calc, {"pct": "100"}, script=script)
    assert result == {"raw": "200"}
