"""End-to-end regression test for the `<Assign>` -> active-ref-trimming bug.

`AssignNode.eval` writes its override via `ctx.set(target, value)` but historically did
NOT call `ctx.mark_active_param(target)` first. The `DynamicUI.ui()` pipeline runs

    1. eval(ctx)         -> Assign writes to param_ref_id_to_value
    2. trim_to_active()  -> evicts entries whose ref-id is not in _active_param_refs
    3. encode_to_memory()-> resolve_param_values + _collect_param read the survivors

so the Assign's write was always evicted at step 2 and the parameter was dropped at
step 3 (because `_is_parameter_active` returned False for it). The fix adds the
missing `mark_active_param` call so the target survives both gates.

These tests build minimal synthetic `ApplicationProgram`s (no .knxprod fixture) whose
dynamic tree is `ChannelIndependentBlock -> ComObjectParameterBlock -> <Assign>`
with a memory-mapped target Parameter and NO co-resident `<ParameterRefRef>` for
that target (the bug-bites case), then run the real `DynamicUI.encode_to_memory()`.
"""

from __future__ import annotations

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramDynamic,
    Assign,
    ChannelIndependentBlock,
    ParameterRefRef,
)
from xknxmono.models.intermediate.application_program_channel_t import (
    ComObjectParameterBlock,
)
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
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.memory_parameter_t import MemoryParameter
from xknxmono.models.intermediate.parameter_ref_t import ParameterRef
from xknxmono.models.intermediate.parameter_type_t import ParameterType
from xknxmono.models.intermediate.parameter_type_t_type_number import (
    ParameterTypeTypeNumber,
)
from xknxmono.models.intermediate.parameter_type_t_type_number_type import (
    ParameterTypeTypeNumberType,
)
from xknxmono.product.parser_v2.dynamic import DynamicUI

_BASE = "M-0008_A-7072-21-5CC3-O000A"
_SEG_ID = f"{_BASE}_RS-04-00000"
_PT_ID = "PT1"

_PARAM_TARGET = f"{_BASE}_P-2"
_REF_TARGET = f"{_BASE}_P-2_R-2"
_PARAM_SOURCE = f"{_BASE}_P-3"
_REF_SOURCE = f"{_BASE}_P-3_R-3"


def _num_type(size_in_bit: int = 8) -> ParameterTypeTypeNumber:
    return ParameterTypeTypeNumber(
        size_in_bit=size_in_bit,
        type_value=ParameterTypeTypeNumberType.UNSIGNED_INT,
        min_inclusive=0,
        max_inclusive=(1 << size_in_bit) - 1,
    )


def _param_type() -> ParameterType:
    return ParameterType(id=_PT_ID, name="T", choice=_num_type(8))


def _segment(size: int = 2) -> ApplicationProgramStaticCodeAbsoluteSegment:
    return ApplicationProgramStaticCodeAbsoluteSegment(
        id=_SEG_ID, size=size, address=0, data=None
    )


def _mem_param(
    param_id: str, value: str, offset: int
) -> ApplicationProgramStaticParametersParameter:
    return ApplicationProgramStaticParametersParameter(
        id=param_id,
        name="",
        text="",
        parameter_type=_PT_ID,
        value=value,
        choice=MemoryParameter(code_segment=_SEG_ID, offset=offset, bit_offset=0),
    )


def _app_value_arm() -> ApplicationProgram:
    """A dynamic tree containing a single `<Assign value="42">` against a memory-mapped
    target (default 7). The target ParameterRef exists in the static section (so the
    parameter is in idx.referenced_parameter_ids and activity-gating applies), but no
    `<ParameterRefRef>` for the target exists anywhere in the dynamic tree."""
    return ApplicationProgram(
        id=_BASE,
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
            code=ApplicationProgramStaticCode(absolute_segment=[_segment()]),
            parameter_types=ApplicationProgramStaticParameterTypes(
                parameter_type=[_param_type()]
            ),
            parameters=ApplicationProgramStaticParameters(
                choice=[_mem_param(_PARAM_TARGET, value="7", offset=0)]
            ),
            parameter_refs=ApplicationProgramStaticParameterRefs(
                parameter_ref=[ParameterRef(id=_REF_TARGET, ref_id=_PARAM_TARGET)]
            ),
        ),
        dynamic=ApplicationProgramDynamic(
            choice=[
                ChannelIndependentBlock(
                    choice=[
                        ComObjectParameterBlock(
                            id=f"{_BASE}_PB-1",
                            choice=[
                                Assign(
                                    target_param_ref_ref=_REF_TARGET,
                                    value="42",
                                )
                            ],
                        )
                    ]
                )
            ]
        ),
    )


def _app_source_arm() -> ApplicationProgram:
    """Same as _app_value_arm() but the dynamic tree contains a `<ParameterRefRef>`
    for the SOURCE parameter (the UI widget shows the source; the PRR marks the source
    active) and the `<Assign>` copies the source's value to the target.

    The source ParameterRef ships with value="42" (seeded into param_ref_defaults in
    DynamicTreeBuilder and read by `ctx.get(R-SRC)` during eval), so the source-arm
    of AssignNode.eval copies "42" into the target ref. The source itself is encoded
    at offset 1 -- that byte is the *source's* memory write and demonstrates the
    source's PRR is the one marking the source active; it is NOT evidence that the
    Assign's write survived. The bug-bites byte is offset 0 (the target with no
    co-resident PRR) -- before the fix it stays 0x00; after the fix it becomes 0x2A.
    """
    source_param = _mem_param(_PARAM_SOURCE, value="42", offset=1)
    source_param_ref = ParameterRef(id=_REF_SOURCE, ref_id=_PARAM_SOURCE, value="42")
    return ApplicationProgram(
        id=_BASE,
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
            code=ApplicationProgramStaticCode(absolute_segment=[_segment()]),
            parameter_types=ApplicationProgramStaticParameterTypes(
                parameter_type=[_param_type()]
            ),
            parameters=ApplicationProgramStaticParameters(
                choice=[
                    _mem_param(_PARAM_TARGET, value="7", offset=0),
                    source_param,
                ]
            ),
            parameter_refs=ApplicationProgramStaticParameterRefs(
                parameter_ref=[
                    ParameterRef(id=_REF_TARGET, ref_id=_PARAM_TARGET),
                    source_param_ref,
                ]
            ),
        ),
        dynamic=ApplicationProgramDynamic(
            choice=[
                ChannelIndependentBlock(
                    choice=[
                        ComObjectParameterBlock(
                            id=f"{_BASE}_PB-1",
                            choice=[
                                ParameterRefRef(ref_id=_REF_SOURCE),
                                Assign(
                                    target_param_ref_ref=_REF_TARGET,
                                    source_param_ref_ref=_REF_SOURCE,
                                ),
                            ],
                        )
                    ]
                )
            ]
        ),
    )


def test_assign_value_appears_in_encoded_image() -> None:
    """The value-arm `<Assign>` should land 0x2A (42) at byte 0 of the encoded image.

    Before the fix: trim_to_active() evicts the override AND _is_parameter_active
    returns False, so the parameter is dropped entirely and the byte stays 0x00.
    """
    dui = DynamicUI(_app_value_arm())
    mem = dui.encode_to_memory()
    assert _SEG_ID in mem
    assert mem[_SEG_ID][0] == 42, (
        f"expected assigned value 42 at offset 0, got {mem[_SEG_ID][0]}; "
        f"full segment: {mem[_SEG_ID]!r}"
    )


def test_assign_source_arm_appears_in_encoded_image() -> None:
    """The source-arm `<Assign>` should also land the copied value at byte 0.

    Byte 1 is the source's own memory write (its PRR marks it active). Before the
    fix: byte 0 (the target with no co-resident PRR) stays 0x00; byte 1 already
    shows the source value (0x2A). With the fix: byte 0 also shows 0x2A.
    """
    dui = DynamicUI(_app_source_arm())
    mem = dui.encode_to_memory()
    assert _SEG_ID in mem
    assert mem[_SEG_ID][0] == 42, (
        f"expected source-arm assigned value 42 at offset 0, got {mem[_SEG_ID][0]}; "
        f"full segment: {mem[_SEG_ID]!r}"
    )
    assert mem[_SEG_ID][1] == 42, (
        f"expected source value 42 at offset 1, got {mem[_SEG_ID][1]}; "
        f"full segment: {mem[_SEG_ID]!r}"
    )
