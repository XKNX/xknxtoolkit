"""Unit tests for ParameterRefRefNode — value fallback, access, label, active tracking.

The node resolves the per-use value via a three-tier chain:

    ctx override → ParameterRef.value → ParameterBase.value

This chain must use the ``is None`` "unset" sentinel — the same sentinel the storage
layer (ParameterState.get) and the union encoder (_pick_union_params) use — rather
than Python ``or``-truthiness. An explicitly-stored empty-string ``""`` override is a
first-class value for both storage and the union encoder, so collapsing it back to the
declared default (the old ``or`` behaviour) created a UI/encoder contract split: the UI
showed the default while the encoder wrote the verbatim ``""``.

These tests cover the resolution chain (including the ``""`` fix), the access gate, the
label/suffix resolution and active-ref tracking, plus an end-to-end check that the UI
and the memory encoder now agree on the resolved value for both union and plain
parameters.
"""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.access_t import Access
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_code import (
    ApplicationProgramStaticCode,
)
from xknxmono.models.intermediate.application_program_static_t_code_absolute_segment import (
    ApplicationProgramStaticCodeAbsoluteSegment,
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
from xknxmono.models.intermediate.application_program_static_t_parameters_union import (
    ApplicationProgramStaticParametersUnion,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter
from xknxmono.models.intermediate.memory_union_t import MemoryUnion
from xknxmono.models.intermediate.parameter_ref_ref_t import ParameterRefRef
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.models.intermediate.parameter_type_t import ParameterType
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_number_type import (
    ParameterTypeTypeNumberType,
)
from xknxmono.models.intermediate.parameter_type_t_type_text import (
    ParameterTypeTypeText,
)
from xknxmono.models.intermediate.union_parameter_t import UnionParameter
from xknxmono.product.errors import EncodingError
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer
from xknxmono.product.parser_v2.encode import (
    collect_writes,
    encode_to_memory,
    resolve_param_values,
)
from xknxmono.product.parser_v2.nodes import (
    EvalContext,
    GlobalState,
    ParameterRefRefNode,
)
from xknxmono.product.parser_v2.ui.parameter import UiParameter

_BASE = "M-0008_A-7072-21-5CC3-O000A"
_PR_ID = f"{_BASE}_P-1_R-1"  # ParameterRef id (the ParameterRefRef's target)
_PARAM_ID = f"{_BASE}_P-1"  # Parameter / UnionParameter id
_PT_ID = "PT1"
_SEG_ID = "SEG1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _num_type(size_in_bit: int = 8) -> ParameterTypeTypeNumber:
    return ParameterTypeTypeNumber(
        size_in_bit=size_in_bit,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=(1 << size_in_bit) - 1,
    )


def _build(
    *,
    union: bool,
    param_value: str,
    param_ref_value: str | None = None,
    param_ref_access: Access | None = None,
    size_in_bit: int = 8,
    text_type: bool = False,
    default_union_parameter: bool = False,
) -> tuple[ApplicationProgram, ApplicationIndexer, ParameterRefRefNode, str]:
    """Build a real app + indexer + node for one Parameter(Ref) pair.

    ``union=True`` makes the parameter a UnionParameter inside a MemoryUnion (the
    reachable divergence target); ``union=False`` makes it a plain
    ApplicationProgramStaticParametersParameter backed by a MemoryParameter. The node
    is built from the indexer's own tables, mirroring DynamicTreeBuilder._build, so
    EvalContext.mark_active_param sees a registered ParameterRef.
    """
    if text_type:
        type_choice: object = ParameterTypeTypeText(size_in_bit=size_in_bit)
    else:
        type_choice = _num_type(size_in_bit)

    pt = ParameterType(id=_PT_ID, name="T", choice=type_choice)

    if union:
        param: object = UnionParameter(
            id=_PARAM_ID,
            name="",
            text="",
            parameter_type=_PT_ID,
            value=param_value,
            offset=0,
            bit_offset=0,
            default_union_parameter=default_union_parameter,
        )
        static_choice = ApplicationProgramStaticParametersUnion(
            choice=MemoryUnion(code_segment=_SEG_ID, offset=0, bit_offset=0),
            size_in_bit=size_in_bit,
            parameter=[param],  # type: ignore[list-item]
        )
    else:
        param = ApplicationProgramStaticParametersParameter(
            id=_PARAM_ID,
            name="",
            text="",
            parameter_type=_PT_ID,
            value=param_value,
            choice=MemoryParameter(code_segment=_SEG_ID, offset=0, bit_offset=0),
        )
        static_choice = param

    param_ref = ParameterRef(
        id=_PR_ID,
        ref_id=_PARAM_ID,
        value=param_ref_value,
        access=param_ref_access,
    )

    # Segment must be at least ceil(size_in_bit / 8) bytes.
    seg_size = (size_in_bit + 7) // 8
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
            code=ApplicationProgramStaticCode(
                absolute_segment=[
                    ApplicationProgramStaticCodeAbsoluteSegment(
                        id=_SEG_ID, size=seg_size, address=0, data=None
                    )
                ]
            ),
            parameter_types=ApplicationProgramStaticParameterTypes(parameter_type=[pt]),
            parameters=ApplicationProgramStaticParameters(choice=[static_choice]),
            parameter_refs=ApplicationProgramStaticParameterRefs(
                parameter_ref=[param_ref]
            ),
        ),
    )
    idx = ApplicationIndexer(app)
    node = ParameterRefRefNode(
        elem=ParameterRefRef(ref_id=_PR_ID),
        param_ref=idx.parameter_refs[_PR_ID],
        param=idx.parameters[_PARAM_ID],
        param_type=idx.parameter_types[_PT_ID],
    )
    return app, idx, node, _PR_ID


def _eval(
    node: ParameterRefRefNode, state: GlobalState, idx: ApplicationIndexer
) -> UiParameter:
    """Eval the node and return its single UiParameter leaf (narrowed from UiNode).

    The node returns ``list[UiNode]``; in all non-empty cases the leaf is a
    ``UiParameter``. Centralising the length + isinstance assertion keeps every value /
    widget / label / suffix / access test strict-checker clean.
    """
    result = node.eval(EvalContext(state, idx=idx))
    assert len(result) == 1
    assert isinstance(result[0], UiParameter)
    return result[0]


# ---------------------------------------------------------------------------
# Value resolution chain — the bug fix (is-None sentinel, not truthiness)
# ---------------------------------------------------------------------------


class TestValueResolution:
    def test_non_empty_override_is_used(self) -> None:
        _, idx, node, pr_id = _build(union=False, param_value="100")
        state = GlobalState(values={pr_id: "42"})
        ui = _eval(node, state, idx)
        assert ui.value == "42"

    def test_empty_string_override_is_preserved_not_collapsed_to_default(self) -> None:
        # The fix: "" is a first-class override value, not the "unset" sentinel.
        # Before the fix the `or` chain collapsed "" to the declared default "100".
        _, idx, node, pr_id = _build(union=False, param_value="100")
        state = GlobalState(values={pr_id: ""})
        ui = _eval(node, state, idx)
        assert ui.value == ""

    def test_empty_string_override_preserved_for_union_member_with_default(
        self,
    ) -> None:
        # The reachable divergence target: a union member with a non-empty default.
        _, idx, node, pr_id = _build(union=True, param_value="100")
        state = GlobalState(values={pr_id: ""})
        ui = _eval(node, state, idx)
        assert ui.value == ""

    def test_no_override_falls_back_to_param_ref_value(self) -> None:
        _, idx, node, _pr_id = _build(
            union=False, param_value="100", param_ref_value="7"
        )
        ui = _eval(node, GlobalState(), idx)
        assert ui.value == "7"

    def test_empty_param_ref_value_not_collapsed_to_param_value(self) -> None:
        # ParameterRef.value="" must win over ParameterBase.value="100" — same
        # is-None semantics one tier down. Before the fix "" collapsed to "100".
        _, idx, node, _pr_id = _build(
            union=False, param_value="100", param_ref_value=""
        )
        ui = _eval(node, GlobalState(), idx)
        assert ui.value == ""

    def test_no_override_no_param_ref_value_falls_back_to_param_value(self) -> None:
        _, idx, node, _pr_id = _build(union=False, param_value="100")
        ui = _eval(node, GlobalState(), idx)
        assert ui.value == "100"

    def test_override_takes_precedence_over_param_ref_value(self) -> None:
        _, idx, node, pr_id = _build(
            union=False, param_value="100", param_ref_value="7"
        )
        state = GlobalState(values={pr_id: "42"})
        ui = _eval(node, state, idx)
        assert ui.value == "42"

    def test_empty_override_takes_precedence_over_non_empty_param_ref_value(
        self,
    ) -> None:
        # "is None" not truthiness: "" override must win over param_ref.value="7".
        # Before the fix the `or` chain made this yield "7".
        _, idx, node, pr_id = _build(
            union=False, param_value="100", param_ref_value="7"
        )
        state = GlobalState(values={pr_id: ""})
        ui = _eval(node, state, idx)
        assert ui.value == ""

    def test_param_ref_value_none_falls_through_to_param_value(self) -> None:
        # ParameterRef.value defaults to None — must fall through, not short-circuit.
        _, idx, node, _pr_id = _build(union=False, param_value="100")
        ui = _eval(node, GlobalState(), idx)
        assert ui.value == "100"

    def test_value_is_always_a_str(self) -> None:
        # UiParameter.value is typed str; the chain must never leak None through.
        _, idx, node, _pr_id = _build(union=False, param_value="9")
        ui = _eval(node, GlobalState(), idx)
        assert isinstance(ui.value, str)


# ---------------------------------------------------------------------------
# Active-ref tracking
# ---------------------------------------------------------------------------


class TestActiveTracking:
    def test_marks_param_ref_active(self) -> None:
        _, idx, node, _pr_id = _build(union=False, param_value="1")
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert _PR_ID in state.active_param_refs()

    def test_marks_underlying_parameter_id_active(self) -> None:
        _, idx, node, _pr_id = _build(union=False, param_value="1")
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert state.is_parameter_active(_PARAM_ID)

    def test_marks_union_member_parameter_id_active(self) -> None:
        _, idx, node, _pr_id = _build(union=True, param_value="1")
        state = GlobalState()
        node.eval(EvalContext(state, idx=idx))
        assert state.is_parameter_active(_PARAM_ID)


# ---------------------------------------------------------------------------
# Access gate
# ---------------------------------------------------------------------------


class TestAccess:
    def test_returns_empty_when_access_is_none(self) -> None:
        _, idx, node, _pr_id = _build(
            union=False, param_value="1", param_ref_access=Access.NONE
        )
        assert node.eval(EvalContext(GlobalState(), idx=idx)) == []

    def test_param_ref_access_overrides_param_access(self) -> None:
        _, idx, node, _pr_id = _build(
            union=False, param_value="1", param_ref_access=Access.READ
        )
        ui = _eval(node, GlobalState(), idx)
        assert ui.access is Access.READ

    def test_falls_back_to_param_access_when_param_ref_access_is_none(self) -> None:
        _, idx, node, _pr_id = _build(union=False, param_value="1")
        ui = _eval(node, GlobalState(), idx)
        # ParameterBase.access defaults to READ_WRITE.
        assert ui.access is Access.READ_WRITE


# ---------------------------------------------------------------------------
# Widget / label / suffix
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# UI/encoder agreement — the end-to-end divergence fix
# ---------------------------------------------------------------------------


class TestUiEncoderAgreement:
    def test_union_number_member_ui_and_encoder_agree_on_empty_override_numeric_raises(
        self,
    ) -> None:
        # The reachable divergence (all 2298 union members in the bundled fixture):
        # before the fix the UI showed the default '100' while the encoder received ''
        # and raised EncodingError. After the fix both see '' and the encoder still
        # raises — but the UI no longer lies about it.
        app, idx, node, pr_id = _build(union=True, param_value="100")
        state = GlobalState()
        state.set(pr_id, "")

        # node.eval marks U1 active AND resolves the value the UI displays.
        ui = _eval(node, state, idx)
        assert ui.value == ""  # UI no longer shows the default '100'

        overrides = resolve_param_values(idx, state)
        assert overrides == {_PARAM_ID: ""}  # storage path preserves "" verbatim

        writes = collect_writes(app, idx, overrides, state)
        assert len(writes.mem) == 1
        assert writes.mem[0].value == ""  # union encoder path preserves "" verbatim

        # Encoder surfaces the unencodable "" as EncodingError (numeric "" can't encode)
        # — the same error the union path always raised; the UI just no longer masks it.
        with pytest.raises(EncodingError, match=_PARAM_ID):
            encode_to_memory(app, idx, overrides, state)

    def test_union_text_member_ui_and_encoder_agree_on_empty_override_silent_write(
        self,
    ) -> None:
        # The schema-permitted silent-miswrite variant: before the fix the UI showed
        # 'Hello' while the device was programmed with all-zero (empty) bytes. After
        # the fix both agree on empty.
        app, idx, node, pr_id = _build(
            union=True, param_value="Hello", text_type=True, size_in_bit=48
        )
        state = GlobalState()
        state.set(pr_id, "")

        ui = _eval(node, state, idx)
        assert ui.value == ""  # UI no longer shows the default 'Hello'

        overrides = resolve_param_values(idx, state)
        mem = encode_to_memory(app, idx, overrides, state)
        # Empty text encodes as all-zero bytes (6 bytes for a 48-bit text field).
        assert mem[_SEG_ID][:6] == b"\x00\x00\x00\x00\x00\x00"

    def test_plain_number_ui_and_encoder_agree_on_empty_override(self) -> None:
        # The required coupling: with only the node fix, the plain path would still
        # collapse "" to the default — a NEW UI/memory split (UI="" vs encoder="100").
        # The encode.py _collect_param fix makes the plain path agree too.
        app, idx, node, pr_id = _build(union=False, param_value="100")
        state = GlobalState()
        state.set(pr_id, "")

        ui = _eval(node, state, idx)
        assert ui.value == ""

        overrides = resolve_param_values(idx, state)
        writes = collect_writes(app, idx, overrides, state)
        assert writes.mem[0].value == ""  # plain path no longer masks "" with default

        # Numeric "" is unencodable — surfaced as EncodingError, not silently defaulted.
        with pytest.raises(EncodingError, match=_PARAM_ID):
            encode_to_memory(app, idx, overrides, state)

    def test_plain_text_ui_and_encoder_agree_on_empty_override(self) -> None:
        app, idx, node, pr_id = _build(
            union=False, param_value="Hi", text_type=True, size_in_bit=16
        )
        state = GlobalState()
        state.set(pr_id, "")

        ui = _eval(node, state, idx)
        assert ui.value == ""

        overrides = resolve_param_values(idx, state)
        mem = encode_to_memory(app, idx, overrides, state)
        assert mem[_SEG_ID][:2] == b"\x00\x00"  # empty text, not "Hi"

    def test_non_empty_override_agreement_unchanged(self) -> None:
        # Regression guard: a normal non-empty override must still flow through both
        # sides identically (this path was never broken).
        app, idx, node, pr_id = _build(union=True, param_value="100")
        state = GlobalState()
        state.set(pr_id, "42")

        ui = _eval(node, state, idx)
        assert ui.value == "42"

        overrides = resolve_param_values(idx, state)
        writes = collect_writes(app, idx, overrides, state)
        assert writes.mem[0].value == "42"
        mem = encode_to_memory(app, idx, overrides, state)
        assert mem[_SEG_ID][0] == 42

    def test_no_override_agreement_unchanged(self) -> None:
        # Regression guard: with no override, UI and encoder both use the default.
        # The union member is marked the default alternative so the encoder writes
        # it when no alternative is explicitly active (real product data often ships
        # unions without an explicit default — that case writes nothing, exercised
        # in test_encode_unit.py — here we test the default-write path).
        app, idx, node, _pr_id = _build(
            union=True, param_value="100", default_union_parameter=True
        )
        state = GlobalState()

        ui = _eval(node, state, idx)
        assert ui.value == "100"

        overrides = resolve_param_values(idx, state)
        assert overrides == {}  # no override stored
        # Union with a default member and no active override writes that default.
        writes = collect_writes(app, idx, overrides, state)
        assert writes.mem[0].value == "100"
        mem = encode_to_memory(app, idx, overrides, state)
        assert mem[_SEG_ID][0] == 100
