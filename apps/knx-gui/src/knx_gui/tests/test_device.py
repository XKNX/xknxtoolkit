"""Covers device.py's standalone pure functions directly, and Device's own
methods via the "no dynamic UI" degenerate-but-valid construction path
(app.program.dynamic=None) - real Device instances, without needing a real
Application/ApplicationProgram (an xsdata-generated dataclass with its own
required fields, not worth constructing just for this).

The fixture-backed section at the bottom uses the real Gira push-button
interface 2-gang comfort knxprod (shared with packages/product) to exercise the
dynamic-UI path: a parameter edit that switches a <choose> branch must
regenerate the com_objects snapshot so the newly-revealed com objects appear in
the Com Flags table and the node editor.
"""

from __future__ import annotations

from pathlib import Path
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
from xknxmono.product import Application, load
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


# --- Device: dynamic-UI path backed by the real Gira 2-gang fixture -----------
#
# The Gira push-button interface 2-gang comfort (M-0008_A-7072-21-5CC3-O000A)
# ships a <choose> branch switch driven by P-106_R-153 (an L->R calc source):
# the default branch emits 4 com objects (MD-1_M-100 / MD-1_M-200), toggling it
# to "1" wholesale-swaps to a single revealed com object (MD-2_M-250). Before the
# fix in set_param_value, the branch switch left Device.com_objects holding the
# stale default-branch snapshot, so get_visible_com_objects() returned [] and
# device.rows was 0 — the Com Flags table rendered "Com Flags (0)" and the node
# editor rendered no pin rows.

_GIRA_FIXTURE = "gira_2gang_button_interface.knxprod"
_GIRA_APP_ID = "M-0008_A-7072-21-5CC3-O000A"
# P-106_R-153 drives an L->R calc whose dependent parameter switches a <choose>
# branch, wholesale-swapping the emitted com-object set.
_TOPO_PARAM = "M-0008_A-7072-21-5CC3-O000A_P-106_R-153"
# P-105_R-116 is an app-root param whose value does not switch any <choose>
# branch — editing it keeps the com-object ref-id set identical (the common
# non-topology case), which is what the db_id-preservation merge must cover.
_NON_TOPO_PARAM = "M-0008_A-7072-21-5CC3-O000A_P-105_R-116"


def _gira_fixture_path() -> Path:
    """Resolve the shared Gira fixture across the workspace (apps/ -> packages/)."""
    for parent in Path(__file__).resolve().parents:
        candidate = (
            parent / "packages" / "product" / "tests" / "fixtures" / _GIRA_FIXTURE
        )
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"fixture {_GIRA_FIXTURE!r} not found under workspace")


def _gira_app() -> Application:
    return load(_gira_fixture_path().read_bytes()).applications[_GIRA_APP_ID]


def _gira_device() -> Device:
    return Device(node_id=0, name="gira", app=_gira_app(), individual_address="")


def _ui_ref_ids(dev: Device) -> list[str]:
    return [co.ref_id for co in _collect_ui_com_objects(dev.get_ui())]


def test_dynamic_device_default_branch_has_four_default_branch_com_objects() -> None:
    device = _gira_device()
    assert len(device.com_objects) == 4
    assert {co.id for co in device.com_objects} == set(_ui_ref_ids(device))
    # get_visible_com_objects mirrors the snapshot (same ref-ids) at construction.
    assert [co.id for co in device.get_visible_com_objects()] == _ui_ref_ids(device)
    assert len(device.rows) == 4


def test_set_param_value_topology_switch_reveals_new_com_objects() -> None:
    """The central bug: a branch-switching param edit must surface the revealed
    com objects in com_objects, get_visible_com_objects() and rows."""
    device = _gira_device()
    default_ids = {co.id for co in device.com_objects}
    assert all("MD-1" in co.id for co in device.com_objects)

    device.set_param_value(_TOPO_PARAM, "1")

    # The live ui() flipped to the alternate branch (one revealed com object).
    revealed = _ui_ref_ids(device)
    assert len(revealed) == 1
    revealed_id = revealed[0]
    assert "MD-2_M-250" in revealed_id
    assert revealed_id not in default_ids

    # FIX: com_objects is regenerated, so the revealed com object is now present
    # (was [] before the fix — stale snapshot filtered out by get_visible_com_objects).
    assert [co.id for co in device.com_objects] == [revealed_id]
    assert [co.id for co in device.get_visible_com_objects()] == [revealed_id]
    assert len(device.rows) == 1
    revealed_co = device.com_objects[0]
    # The revealed com object is the one shown in the node editor's single pin row.
    row = device.rows[0]
    assert row.left is revealed_co or row.right is revealed_co


def test_set_param_value_topology_switch_drops_old_branch_com_objects() -> None:
    """Com objects no longer emitted by ui() are dropped from the snapshot."""
    device = _gira_device()
    default_ids = {co.id for co in device.com_objects}

    device.set_param_value(_TOPO_PARAM, "1")

    new_ids = {co.id for co in device.com_objects}
    assert new_ids.isdisjoint(default_ids)
    for dropped_id in default_ids:
        assert device.find_com_object(dropped_id) is None


def test_set_param_value_revealed_com_object_has_db_id_none() -> None:
    """A com object revealed by a branch switch is minted fresh with db_id=None,
    matching the constructor's behaviour (the project layer only seeds store rows
    at add_device time from the initial default-branch snapshot). Seeding revealed
    com objects into the store is a separate project-layer concern, intentionally
    out of scope here."""
    device = _gira_device()
    device.set_param_value(_TOPO_PARAM, "1")
    assert len(device.com_objects) == 1
    assert device.com_objects[0].db_id is None


def test_set_param_value_topology_back_restores_default_branch() -> None:
    """Toggling the topology param back reverts the branch and re-mints the default
    com objects (the prior default instances were dropped during the wholesale swap,
    so the merge has nothing to recover — db_id is None until the project layer
    re-seeds)."""
    device = _gira_device()
    default_ids = [co.id for co in device.com_objects]

    device.set_param_value(_TOPO_PARAM, "1")
    assert [co.id for co in device.com_objects] != default_ids

    device.set_param_value(_TOPO_PARAM, "0")

    assert [co.id for co in device.com_objects] == default_ids
    assert [co.id for co in device.get_visible_com_objects()] == default_ids
    assert len(device.rows) == 4


def test_set_param_value_non_topology_edit_preserves_db_id_and_instance_identity() -> (
    None
):
    """Regression guard against a bare regeneration: a non-topology edit keeps the
    same com-object ref-ids, so the merge-by-ref-id must reuse the existing
    ComObject instances and preserve db_id (which set_param deliberately does not
    rebuild via _bump). A bare `com_objects = _create_com_objects_from_app()` would
    mint fresh instances with db_id=None, silently no-op'ing subsequent flag edits
    (service.set_flag guards on `co.db_id is None`)."""
    device = _gira_device()
    # Simulate _build_device's post-construction db_id patching (service.py:280-283).
    for i, co in enumerate(device.com_objects):
        co.db_id = 100 + i
    ids_before = [co.id for co in device.com_objects]
    instances_before = {co.id: id(co) for co in device.com_objects}
    db_ids_before = {co.id: co.db_id for co in device.com_objects}

    device.set_param_value(_NON_TOPO_PARAM, "1")

    # Ref-ids unchanged (the non-topology edit doesn't switch a <choose> branch).
    assert [co.id for co in device.com_objects] == ids_before
    # FIX: the same ComObject instances are reused (id() preserved), with db_id intact.
    assert {co.id: id(co) for co in device.com_objects} == instances_before
    assert {co.id: co.db_id for co in device.com_objects} == db_ids_before
    assert all(co.db_id is not None for co in device.com_objects)
    # find_com_object still returns the same instance, so set_flag/link keep working.
    for co in device.com_objects:
        assert device.find_com_object(co.id) is co


def test_set_param_value_non_topology_edit_preserves_db_id_after_topology_roundtrip() -> (
    None
):
    """The db_id-preservation merge keeps working across repeated non-topology edits
    after a topology toggle-back (the re-minted default com objects can be re-seeded
    with db_id and a subsequent non-topology edit must preserve them again)."""
    device = _gira_device()
    device.set_param_value(_TOPO_PARAM, "1")
    device.set_param_value(_TOPO_PARAM, "0")
    # Re-seed db_id on the re-minted default com objects (simulating a rebuild).
    for i, co in enumerate(device.com_objects):
        co.db_id = 200 + i
    db_ids_before = {co.id: co.db_id for co in device.com_objects}

    device.set_param_value(_NON_TOPO_PARAM, "0")

    assert {co.id: co.db_id for co in device.com_objects} == db_ids_before


def test_set_param_value_non_topology_edit_re_syncs_display_fields_from_ui() -> None:
    """Even when ref-ids persist, the merge re-syncs display fields (name/number/flags)
    from the freshly-evaluated UiComObject — so e.g. a param-driven channel rename that
    shows up in the UiComObject name is reflected on the reused ComObject instance."""
    device = _gira_device()
    original_name = device.com_objects[0].name

    device.set_param_value(_NON_TOPO_PARAM, "1")

    # Same instance, but display fields are re-synced from ui() (name is stable for a
    # non-topology edit, so the assertion is that the instance survives with a name
    # matching the freshly-evaluated UiComObject).
    same_co = device.com_objects[0]
    ui_cos = {co.ref_id: co for co in _collect_ui_com_objects(device.get_ui())}
    assert same_co.name == ui_cos[same_co.id].name
    assert same_co.number == ui_cos[same_co.id].number
    assert same_co.name == original_name  # non-topology edit doesn't change the name


def test_set_param_value_invalidates_visible_cos_and_rows_caches() -> None:
    """A parameter edit must invalidate the visibility/rows caches so the next read
    reflects the regenerated snapshot, not a stale cached list."""
    device = _gira_device()
    _ = device.get_visible_com_objects()  # warm cache
    _ = device.rows
    assert device._cached_visible_cos is not None  # pyright: ignore[reportPrivateUsage]
    assert device._cached_rows is not None  # pyright: ignore[reportPrivateUsage]

    device.set_param_value(_TOPO_PARAM, "1")

    assert device._cached_visible_cos is None  # pyright: ignore[reportPrivateUsage]
    assert device._cached_rows is None  # pyright: ignore[reportPrivateUsage]
    # The next read repopulates from the regenerated snapshot.
    assert len(device.get_visible_com_objects()) == 1
    assert len(device.rows) == 1
    assert device._cached_visible_cos is not None  # pyright: ignore[reportPrivateUsage]
    assert device._cached_rows is not None  # pyright: ignore[reportPrivateUsage]


def test_set_param_value_without_dynamic_ui_is_a_no_op_regression() -> None:
    """The no-dynamic-UI path is unchanged by the fix: set_param_value stays a no-op
    (the refresh returns a copy of com_objects, never reached because the guarded
    branch is skipped), and com_objects/visible_cos/rows are unaffected."""
    co = _co("a", write=True)
    device = _make_device([co])
    assert device.com_objects == [co]

    device.set_param_value("x", "1")

    assert device.com_objects == [co]
    assert device.get_visible_com_objects() == [co]
    assert device.rows == [PinRow(left=co)]
