"""Covers device.py's standalone pure functions directly, and Device's own
methods via the "no dynamic UI" degenerate-but-valid construction path
(app.program.dynamic=None) - real Device instances, without needing a real
Application/ApplicationProgram (an xsdata-generated dataclass with its own
required fields, not worth constructing just for this)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from knx_gui.device import (
    ComObject,
    ComObjectFlags,
    Device,
    PinDir,
    PinRow,
    _collect_ui_com_objects,  # pyright: ignore[reportPrivateUsage]
    com_object_has_input,
    com_object_has_output,
    default_flags_for,
    flag_diff_letters,
    generate_rows,
)
from knx_gui.dpt import DPT_UNKNOWN

from xknxmono.product import Application
from xknxmono.product.parser_v2.ui import UiComObject, UiNode, UiParameterBlock, UiTab


def _co(
    id_: str,
    *,
    read: bool = False,
    write: bool = False,
    transmit: bool = False,
    update: bool = False,
) -> ComObject:
    return ComObject(
        id=id_,
        name=id_,
        dpt=DPT_UNKNOWN,
        flags=ComObjectFlags(read=read, write=write, transmit=transmit, update=update),
    )


def _ui_co(ref_id: str) -> UiComObject:
    return UiComObject(
        ref_id=ref_id,
        name=ref_id,
        number=0,
        dpt_codes=(),
        communication=True,
        read=False,
        write=False,
        transmit=False,
        update=False,
        read_on_init=False,
        read_locked=False,
        write_locked=False,
        transmit_locked=False,
        update_locked=False,
        read_on_init_locked=False,
    )


def _make_device(com_objects: list[ComObject] | None = None) -> Device:
    fake_app = SimpleNamespace(program=SimpleNamespace(dynamic=None))
    return Device(
        node_id=1,
        name="Test Device",
        app=cast(Application, fake_app),
        individual_address="1.1.1",
        com_objects=com_objects or [],
    )


# --- default_flags_for / ComObjectFlags -----------------------------------


def test_default_flags_for_input() -> None:
    flags = default_flags_for(PinDir.INPUT)
    assert flags == ComObjectFlags(communication=True, write=True)


def test_default_flags_for_output() -> None:
    flags = default_flags_for(PinDir.OUTPUT)
    assert flags == ComObjectFlags(communication=True, read=True, transmit=True)


# --- flag_diff_letters -----------------------------------------------------


def test_flag_diff_letters_no_diff_from_default() -> None:
    assert flag_diff_letters(default_flags_for(PinDir.INPUT), PinDir.INPUT) == []


def test_flag_diff_letters_reports_only_the_differing_flags() -> None:
    flags = default_flags_for(PinDir.INPUT)
    flags.read = True  # extra flag not in the INPUT default
    flags.write = False  # turned off a flag the INPUT default has on
    diffs = flag_diff_letters(flags, PinDir.INPUT)
    assert set(diffs) == {("R", True), ("W", False)}


# --- com_object_has_input / com_object_has_output --------------------------


def test_com_object_has_input_true_for_write() -> None:
    assert com_object_has_input(_co("a", write=True)) is True


def test_com_object_has_input_true_for_update() -> None:
    assert com_object_has_input(_co("a", update=True)) is True


def test_com_object_has_input_false_otherwise() -> None:
    assert com_object_has_input(_co("a", read=True, transmit=True)) is False


def test_com_object_has_output_true_for_read_or_transmit() -> None:
    assert com_object_has_output(_co("a", read=True)) is True
    assert com_object_has_output(_co("a", transmit=True)) is True


def test_com_object_has_output_false_otherwise() -> None:
    assert com_object_has_output(_co("a", write=True, update=True)) is False


# --- generate_rows -----------------------------------------------------------


def test_generate_rows_trailing_input_only_is_flushed_alone() -> None:
    rows = generate_rows([_co("in", write=True)])
    assert rows == [PinRow(left=_co("in", write=True))]


def test_generate_rows_output_only_with_no_pending_input() -> None:
    rows = generate_rows([_co("out", read=True)])
    assert rows == [PinRow(right=_co("out", read=True))]


def test_generate_rows_both_input_and_output_pairs_with_itself() -> None:
    co = _co("io", write=True, read=True)
    assert generate_rows([co]) == [PinRow(left=co, right=co)]


def test_generate_rows_pairs_pending_input_with_next_output() -> None:
    in_co = _co("in", write=True)
    out_co = _co("out", read=True)
    assert generate_rows([in_co, out_co]) == [PinRow(left=in_co, right=out_co)]


def test_generate_rows_two_inputs_in_a_row_get_separate_rows() -> None:
    a = _co("a", write=True)
    b = _co("b", write=True)
    assert generate_rows([a, b]) == [PinRow(left=a), PinRow(left=b)]


def test_generate_rows_flushes_pending_input_before_a_both_com_object() -> None:
    pending = _co("pending", write=True)
    both = _co("both", write=True, read=True)
    assert generate_rows([pending, both]) == [
        PinRow(left=pending),
        PinRow(left=both, right=both),
    ]


def test_generate_rows_skips_com_objects_with_neither_input_nor_output() -> None:
    neither = _co("neither")  # communication-only: no read/write/transmit/update
    assert generate_rows([neither]) == []


# --- _collect_ui_com_objects -------------------------------------------------


def test_collect_ui_com_objects_flat() -> None:
    nodes = (_ui_co("a"), _ui_co("b"))
    result = _collect_ui_com_objects(nodes)
    assert [n.ref_id for n in result] == ["a", "b"]


def test_collect_ui_com_objects_recurses_into_tabs_and_parameter_blocks() -> None:
    nodes: list[UiNode] = [
        UiTab(children=(_ui_co("in-tab"),), id="t1"),
        UiParameterBlock(id="pb1", children=(_ui_co("in-block"),)),
        _ui_co("top-level"),
    ]
    result = _collect_ui_com_objects(nodes)
    assert {n.ref_id for n in result} == {"in-tab", "in-block", "top-level"}


# --- Device: no-dynamic-ui degenerate path -----------------------------------


def test_device_get_ui_without_dynamic_ui_is_empty() -> None:
    assert _make_device().get_ui() == []


def test_device_get_segment_base_addrs_without_dynamic_ui_is_empty() -> None:
    assert _make_device().get_segment_base_addrs() == {}


def test_device_encode_to_memory_without_dynamic_ui_is_empty() -> None:
    assert _make_device().encode_to_memory() == {}


def test_device_get_memory_param_map_without_dynamic_ui_is_empty() -> None:
    assert _make_device().get_memory_param_map() == {}


def test_device_get_module_instances_without_dynamic_ui_is_empty() -> None:
    assert _make_device().get_module_instances() == []


def test_device_set_com_obj_instance_ref_without_dynamic_ui_is_a_no_op() -> None:
    device = _make_device()
    device.set_com_obj_instance_ref("x", cast("object", None))  # type: ignore[arg-type]


def test_device_set_param_value_without_dynamic_ui_is_a_no_op() -> None:
    device = _make_device()
    device.set_param_value("x", "1")


def test_device_get_visible_com_objects_without_dynamic_ui() -> None:
    co = _co("a", write=True)
    device = _make_device([co])
    assert device.get_visible_com_objects() == [co]


def test_device_rows_property_uses_generate_rows() -> None:
    co = _co("a", write=True, read=True)
    device = _make_device([co])
    assert device.rows == [PinRow(left=co, right=co)]


def test_device_find_com_object_hit() -> None:
    co = _co("a")
    device = _make_device([co])
    assert device.find_com_object("a") is co


def test_device_find_com_object_miss() -> None:
    device = _make_device([_co("a")])
    assert device.find_com_object("missing") is None
