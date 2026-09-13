"""Unit tests for parser_v2.state: the ParameterState/GlobalState/ModuleState tree that
holds a project's parameter overrides, module instances and active-ref bookkeeping.
"""

from __future__ import annotations

from typing import Any, ClassVar

import pytest

from xknxmono.models.intermediate import (
    ComObjectInstanceRef,
    ModuleInstance,
    ModuleTextArg,
    ParameterInstanceRef,
)
from xknxmono.models.intermediate.module_def_t_arguments import ModuleDefArguments
from xknxmono.models.intermediate.module_def_t_arguments_argument import (
    ModuleDefArgumentsArgument,
)
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg
from xknxmono.product.errors import EncodingError
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.state import (
    GlobalState,
    ModuleState,
    compute_arg_defaults,
    compute_param_ref_defaults,
)

# ---------------------------------------------------------------------------
# compute_arg_defaults
# ---------------------------------------------------------------------------


def test_compute_arg_defaults_none_container_returns_empty() -> None:
    assert (
        compute_arg_defaults(
            None, [ModuleTextArg(ref_id="A1", id="a1", value="x")], "MD1"
        )
        == {}
    )


def test_compute_arg_defaults_matches_text_arg() -> None:
    mod_def_args = ModuleDefArguments(
        argument=[ModuleDefArgumentsArgument(id="A1", name="Width")]
    )
    result = compute_arg_defaults(
        mod_def_args, [ModuleTextArg(ref_id="A1", id="a1", value="10cm")], "MD1"
    )
    assert result == {"Width": "10cm"}


def test_compute_arg_defaults_raises_on_unmatched_ref_id() -> None:
    mod_def_args = ModuleDefArguments(
        argument=[ModuleDefArgumentsArgument(id="A1", name="Width")]
    )
    with pytest.raises(EncodingError, match="NO_SUCH_ARG"):
        compute_arg_defaults(
            mod_def_args,
            [ModuleTextArg(ref_id="NO_SUCH_ARG", id="a1", value="10cm")],
            "MD1",
        )


def test_compute_arg_defaults_skips_non_text_args() -> None:
    mod_def_args = ModuleDefArguments(
        argument=[ModuleDefArgumentsArgument(id="A1", name="Width")]
    )
    numeric = ModuleNumericArg(ref_id="A1", value=5)
    result = compute_arg_defaults(mod_def_args, [numeric], "MD1")
    assert result == {}


# ---------------------------------------------------------------------------
# compute_param_ref_defaults
# ---------------------------------------------------------------------------


def _idx_with_parameters(parameters: dict[str, Any]) -> ApplicationIndexer:
    idx = object.__new__(ApplicationIndexer)
    idx.parameters = parameters  # pyright: ignore[reportAttributeAccessIssue]
    return idx


def test_compute_param_ref_defaults_none_container_returns_empty() -> None:
    idx = _idx_with_parameters({})
    assert compute_param_ref_defaults(None, idx) == {}


def test_compute_param_ref_defaults_empty_parameter_ref_list_returns_empty() -> None:
    class _Refs:
        parameter_ref: ClassVar[list[ParameterInstanceRef]] = []

    idx = _idx_with_parameters({})
    assert compute_param_ref_defaults(_Refs(), idx) == {}


def test_compute_param_ref_defaults_uses_explicit_value() -> None:
    class _Refs:
        parameter_ref: ClassVar = [
            ParameterInstanceRef(id="PR1", ref_id="P1", value="9")
        ]

    idx = _idx_with_parameters({})
    assert compute_param_ref_defaults(_Refs(), idx) == {"PR1": "9"}


def test_compute_param_ref_defaults_falls_back_to_base_parameter_value() -> None:
    class _Base:
        value = "42"

    class _Refs:
        parameter_ref: ClassVar = [
            ParameterInstanceRef(id="PR1", ref_id="P1", value=None)
        ]

    idx = _idx_with_parameters({"P1": _Base()})
    assert compute_param_ref_defaults(_Refs(), idx) == {"PR1": "42"}


def test_compute_param_ref_defaults_skips_when_neither_value_present() -> None:
    class _Refs:
        parameter_ref: ClassVar = [
            ParameterInstanceRef(id="PR1", ref_id="P1", value=None)
        ]

    idx = _idx_with_parameters({})  # P1 not registered, pr.value is None
    assert compute_param_ref_defaults(_Refs(), idx) == {}


# ---------------------------------------------------------------------------
# ParameterState.get / get_arg
# ---------------------------------------------------------------------------


def test_get_value_present_locally() -> None:
    state = GlobalState(values={"P1": "5"})
    assert state.get("P1") == "5"


def test_get_falls_back_to_parent() -> None:
    root = GlobalState(values={"P1": "root-val"})
    child = ModuleState("M1", param_ref_defaults={})
    child._parent = root  # pyright: ignore[reportPrivateUsage]
    assert child.get("P1") == "root-val"


def test_get_falls_back_to_param_ref_defaults() -> None:
    state = GlobalState(param_ref_defaults={"P1": "default-val"})
    assert state.get("P1") == "default-val"


def test_get_arg_base_class_always_none() -> None:
    state = GlobalState()
    assert state.get_arg("anything") is None


# ---------------------------------------------------------------------------
# ComObjectInstanceRef / alloc position bookkeeping
# ---------------------------------------------------------------------------


def test_set_and_get_com_obj_instance_ref_locally() -> None:
    state = GlobalState()
    coir = ComObjectInstanceRef(ref_id="CO1")
    state.set_com_obj_instance_ref("CO1", coir)
    assert state.get_com_obj_instance_ref("CO1") is coir


def test_get_com_obj_instance_ref_falls_back_to_parent() -> None:
    root = GlobalState()
    coir = ComObjectInstanceRef(ref_id="CO1")
    root.set_com_obj_instance_ref("CO1", coir)
    child = root.module_child("M1")
    assert child.get_com_obj_instance_ref("CO1") is coir


def test_alloc_position_default_and_set() -> None:
    state = GlobalState()
    assert state.alloc_position("A1", 3) == 3
    state.set_alloc_position("A1", 7)
    assert state.alloc_position("A1", 3) == 7


# ---------------------------------------------------------------------------
# trim_to_active / active_com_object_refs
# ---------------------------------------------------------------------------


def test_trim_to_active_removes_inactive_module_children() -> None:
    root = GlobalState()
    active_child = root.module_child("ACTIVE")
    root.module_child("INACTIVE")
    root.reset_active()  # clears the _active_module_keys both calls above populated
    root._active_module_keys.add("ACTIVE_MI-1")  # pyright: ignore[reportPrivateUsage]
    root.trim_to_active()
    assert list(root._children.values()) == [active_child]  # pyright: ignore[reportPrivateUsage]


def test_active_com_object_refs_includes_children() -> None:
    root = GlobalState()
    root.mark_active_com_object("ROOT_CO")
    child = root.module_child("M1")
    child.mark_active_com_object("CHILD_CO")
    assert root.active_com_object_refs() == {"ROOT_CO", child.qualify("CHILD_CO")}


# ---------------------------------------------------------------------------
# find_scope_for_qualified / set_instance_ref / clear_instance_ref
# ---------------------------------------------------------------------------


def test_clear_instance_ref_local_when_no_module_scope_matches() -> None:
    state = GlobalState(values={"P1": "5"})
    state.clear_instance_ref("P1")
    assert state.param_ref_id_to_value == {}


def test_set_and_clear_instance_ref_in_module_scope() -> None:
    root = GlobalState()
    m1 = root.module_child("M1", ref_id="MD1")
    root.set_instance_ref("M1_MI-1_P-5_R-2", "val")
    assert m1.param_ref_id_to_value == {"MD1_P-5_R-2": "val"}
    root.clear_instance_ref("M1_MI-1_P-5_R-2")
    assert m1.param_ref_id_to_value == {}


def test_find_scope_for_qualified_returns_none_without_ref_id() -> None:
    root = GlobalState()
    m1 = root.module_child("APP_MD-1_M-100", ref_id=None)
    assert m1.find_scope_for_qualified("APP_MD-1_M-100_MI-1_P-5_R-1") is None


def test_find_scope_for_qualified_recurses_into_nested_child() -> None:
    root = GlobalState()
    m1 = root.module_child("APP_MD-1_M-200", ref_id="APP_MD-1")
    # A sibling under m1 that doesn't match, so m1's own child loop must skip
    # past it before finding the real match.
    m1.module_child("APP_MD-1_M-200_MI-1_SM-9_M-999", ref_id="APP_MD-1_SM-9")
    child = m1.module_child("APP_MD-1_M-200_MI-1_SM-1_M-300", ref_id="APP_MD-1_SM-1")
    found = root.find_scope_for_qualified("APP_MD-1_M-200_MI-1_SM-1_M-300_MI-1_XYZ")
    assert found is not None
    scope, local = found
    assert scope is child
    assert local == "APP_MD-1_SM-1_XYZ"


# ---------------------------------------------------------------------------
# module_instances (base ParameterState + ModuleState override)
# ---------------------------------------------------------------------------


def test_base_module_instances_recurses_children_without_including_self() -> None:
    root = GlobalState()
    root.module_child("M1", ref_id="MD1")
    instances = root.module_instances()
    assert len(instances) == 1
    instance_id, ref_id, _args = instances[0]
    assert instance_id == "M1_MI-1"
    assert ref_id == "MD1"


def test_module_state_module_instances_includes_self_and_children() -> None:
    root = GlobalState()
    m1 = root.module_child("M1", ref_id="MD1")
    m1.module_child("SUB1", ref_id="SMD1")
    instances = m1.module_instances()
    ids = [i[0] for i in instances]
    assert ids == ["M1_MI-1", "SUB1_MI-1"]


# ---------------------------------------------------------------------------
# ModuleState.active_param_refs / active_com_object_refs / parameter_instance_refs
# ---------------------------------------------------------------------------


def test_module_state_active_param_refs_includes_children() -> None:
    root = GlobalState()
    m1 = root.module_child("M1", ref_id="MD1")
    m1.mark_active_param("MD1_P-5_R-1")
    child = m1.module_child("SUB1", ref_id="SMD1")
    child.mark_active_param("SMD1_P-9_R-1")
    result = m1.active_param_refs()
    assert m1.qualify("MD1_P-5_R-1") in result
    assert child.qualify("SMD1_P-9_R-1") in result


def test_module_state_active_com_object_refs_includes_children() -> None:
    root = GlobalState()
    m1 = root.module_child("M1", ref_id="MD1")
    m1.mark_active_com_object("MD1_CO-1")
    child = m1.module_child("SUB1", ref_id="SMD1")
    child.mark_active_com_object("SMD1_CO-2")
    result = m1.active_com_object_refs()
    assert m1.qualify("MD1_CO-1") in result
    assert child.qualify("SMD1_CO-2") in result


def test_module_state_parameter_instance_refs_includes_children() -> None:
    root = GlobalState()
    m1 = root.module_child("M1", ref_id="MD1")
    m1.param_ref_id_to_value["MD1_P-5_R-1"] = "5"
    child = m1.module_child("SUB1", ref_id="SMD1")
    child.param_ref_id_to_value["SMD1_P-9_R-1"] = "9"
    result = m1.parameter_instance_refs()
    assert len(result) == 2


# ---------------------------------------------------------------------------
# GlobalState.from_project
# ---------------------------------------------------------------------------


def test_from_project_empty() -> None:
    root = GlobalState.from_project()
    assert root.param_ref_id_to_value == {}
    assert root.module_children() == []


def test_from_project_skips_module_instance_missing_id_or_ref_id() -> None:
    root = GlobalState.from_project(
        module_instances=[
            ModuleInstance(id=None, ref_id="MD1"),
            ModuleInstance(id="M2", ref_id=None),
        ]
    )
    assert root.module_children() == []


def test_from_project_matches_parameter_instance_ref_to_module() -> None:
    root = GlobalState.from_project(
        module_instances=[ModuleInstance(id="M1", ref_id="MD1")],
        parameter_instance_refs=[
            ParameterInstanceRef(ref_id="APP_M1_P-5_R-1", value="7")
        ],
    )
    m1 = root._children["M1"]  # pyright: ignore[reportPrivateUsage]
    assert m1.param_ref_id_to_value == {"APP_MD1_P-5_R-1": "7"}


def test_from_project_skips_pir_with_none_value() -> None:
    root = GlobalState.from_project(
        module_instances=[ModuleInstance(id="M1", ref_id="MD1")],
        parameter_instance_refs=[
            ParameterInstanceRef(ref_id="APP_M1_P-9_R-2", value=None)
        ],
    )
    m1 = root._children["M1"]  # pyright: ignore[reportPrivateUsage]
    assert m1.param_ref_id_to_value == {}


def test_from_project_unmatched_ref_id_goes_to_root() -> None:
    root = GlobalState.from_project(
        module_instances=[ModuleInstance(id="M1", ref_id="MD1")],
        parameter_instance_refs=[
            ParameterInstanceRef(ref_id="APP_UNRELATED_P-1_R-1", value="9")
        ],
    )
    assert root.param_ref_id_to_value == {"APP_UNRELATED_P-1_R-1": "9"}


def test_from_project_com_object_instance_refs() -> None:
    coir = ComObjectInstanceRef(ref_id="CO1")
    root = GlobalState.from_project(com_object_instance_refs=[coir])
    assert root.get_com_obj_instance_ref("CO1") is coir
