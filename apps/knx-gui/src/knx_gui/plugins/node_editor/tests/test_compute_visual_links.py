"""Headless unit tests for NodeEditorPanel link computation.

`_compute_visual_links` is pure Python over injected state (no imgui / GL /
editor context - verified by importing `NodeEditorPanel` and calling it
without `setup()`), so it can be exercised directly like the helpers in
``src/knx_gui/tests/test_device.py`` / ``test_dpt.py``.

The regression these tests lock down: a group address with a single sender
and multiple receivers must produce one *unique* visual link per
sender x receiver pair. Previously the GA-hidden branch reused ``ga.id`` as
the visual ``LinkId`` for every pair, so ``imgui_node_editor``'s ``ed.link``
collapsed all of them onto a single editor link record (only the
last-submitted pair survived). The fix makes the ``LinkId`` unique per pair
and threads the underlying ``ga_id`` back as the 4th tuple element so
``_handle_link_deletion`` can still remove the right GA.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import patch

from imgui_bundle import imgui_node_editor as ed
from knx_gui.plugins.node_editor.ui import NodeEditorPanel
from knx_gui.plugins.project.service import Assignment, GroupAddress

# Access panel internals directly - the panel is a unit of state and these
# tests assert on its private link/pin maps. Each private reach goes through a
# tiny wrapper carrying a single ``# pyright: ignore[reportPrivateUsage]`` so
# the strict type-checker stays quiet without littering every assertion line;
# the same private-access style is used in
# ``src/knx_gui/testing/tests/test_configure_panel.py``.


def _make_panel(
    *,
    group_addresses: list[GroupAddress],
    assignments_by_ga: dict[int, list[Assignment]],
) -> NodeEditorPanel:
    return NodeEditorPanel(
        get_devices=lambda: [],
        get_group_addresses=lambda: list(group_addresses),
        get_assignments_for_ga=lambda ga_id: list(assignments_by_ga.get(ga_id, [])),
        add_link=lambda a, b: 1,
        remove_link=lambda a: None,
        on_param_change=lambda d, p, v: None,
    )


def _seed_pin(
    panel: NodeEditorPanel, co_db_id: int, in_pin: int | None, out_pin: int | None
) -> None:
    pins: dict[str, int] = {}
    if in_pin is not None:
        pins["in"] = in_pin
    if out_pin is not None:
        pins["out"] = out_pin
    panel._co_db_id_to_pins[co_db_id] = pins  # pyright: ignore[reportPrivateUsage]


def _visual_links(panel: NodeEditorPanel) -> list[tuple[int, int, int, int]]:
    return panel._compute_visual_links()  # pyright: ignore[reportPrivateUsage]


def _link_exists(panel: NodeEditorPanel, pin_a: int, pin_b: int) -> bool:
    return panel._link_exists(pin_a, pin_b)  # pyright: ignore[reportPrivateUsage]


def _set_show_ga_nodes(panel: NodeEditorPanel, value: bool) -> None:
    panel._show_ga_nodes = value  # pyright: ignore[reportPrivateUsage]


def _set_ga_pins(panel: NodeEditorPanel, ga_id: int, pins: tuple[int, int]) -> None:
    panel._ga_pins[ga_id] = pins  # pyright: ignore[reportPrivateUsage]


def _set_link_map(panel: NodeEditorPanel, mapping: dict[int, int]) -> None:
    panel._visual_link_id_to_ga_id = mapping  # pyright: ignore[reportPrivateUsage]


def _set_remove_link(panel: NodeEditorPanel, fn: Callable[[int], None]) -> None:
    panel._remove_link = fn  # pyright: ignore[reportPrivateUsage]


def _handle_deletion(panel: NodeEditorPanel) -> None:
    panel._handle_link_deletion()  # pyright: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# GA-hidden mode (default, _show_ga_nodes = False)
# ---------------------------------------------------------------------------


def test_hidden_no_group_addresses_returns_empty() -> None:
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    assert _visual_links(panel) == []


def test_hidden_ga_with_no_assignments_is_skipped() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")], assignments_by_ga={7: []}
    )
    assert _visual_links(panel) == []


def test_hidden_ga_with_single_assignment_is_skipped() -> None:
    # GA-hidden mode requires at least two assignments on the GA, otherwise
    # there is no pair to draw a link between.
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={7: [Assignment(100, 500, 7, is_sending=True)]},
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    assert _visual_links(panel) == []


def test_hidden_assignment_with_unknown_co_db_id_is_skipped() -> None:
    # If the CO was never rendered (no pin), the assignment yields no pin and
    # must be dropped from the sender/receiver lists.
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 99999, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    # 99999 was never seeded -> only one valid pin -> < 2 assignments -> skipped
    assert _visual_links(panel) == []


def test_hidden_sending_assignment_without_out_pin_is_dropped() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),  # only "in" pin seeded
                Assignment(101, 501, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=100001, out_pin=None)
    _seed_pin(panel, 501, in_pin=100002, out_pin=None)
    assert _visual_links(panel) == []


def test_hidden_receiving_assignment_without_in_pin_is_dropped() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),  # only "out" pin seeded
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=None, out_pin=100002)
    assert _visual_links(panel) == []


def test_hidden_one_sender_one_receiver_produces_single_link() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    assert _visual_links(panel) == [(7 * 1_000_000 + 0 * 1000 + 0, 100000, 100001, 7)]


def test_hidden_multi_receiver_link_ids_are_unique_per_pair() -> None:
    # The bug report's headline scenario: 1 sender x 3 receivers.
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
                Assignment(102, 502, 7, is_sending=False),
                Assignment(103, 503, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    _seed_pin(panel, 502, in_pin=100002, out_pin=None)
    _seed_pin(panel, 503, in_pin=100003, out_pin=None)

    links = _visual_links(panel)

    assert len(links) == 3, f"expected 3 visual links, got {len(links)}: {links}"
    link_ids = [link_id for link_id, _, _, _ in links]
    assert len(set(link_ids)) == 3, (
        f"LinkIds must be unique per sender x receiver pair; got {link_ids}"
    )
    # All three curves emanate from the single sender output pin.
    assert all(start == 100000 for _, start, _, _ in links)
    # Each receiver pin is its own curve endpoint.
    assert sorted(end for _, _, end, _ in links) == [100001, 100002, 100003]
    # The underlying GA is threaded back for deletion on every link.
    assert all(ga_id == 7 for _, _, _, ga_id in links)
    # Pin pairs are preserved exactly (no reordering / dropping).
    assert sorted((start, end) for _, start, end, _ in links) == [
        (100000, 100001),
        (100000, 100002),
        (100000, 100003),
    ]


def test_hidden_multi_sender_multi_receiver_cartesian_product() -> None:
    # 2 senders x 3 receivers -> 6 distinct curves with 6 distinct LinkIds.
    panel = _make_panel(
        group_addresses=[GroupAddress(3, "1/3", "n")],
        assignments_by_ga={
            3: [
                Assignment(10, 100, 3, is_sending=True),
                Assignment(11, 101, 3, is_sending=True),
                Assignment(20, 200, 3, is_sending=False),
                Assignment(21, 201, 3, is_sending=False),
                Assignment(22, 202, 3, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 100, in_pin=None, out_pin=200000)
    _seed_pin(panel, 101, in_pin=None, out_pin=200001)
    _seed_pin(panel, 200, in_pin=200002, out_pin=None)
    _seed_pin(panel, 201, in_pin=200003, out_pin=None)
    _seed_pin(panel, 202, in_pin=200004, out_pin=None)

    links = _visual_links(panel)

    assert len(links) == 6, f"expected 6 visual links, got {len(links)}: {links}"
    link_ids = [link_id for link_id, _, _, _ in links]
    assert len(set(link_ids)) == 6, f"LinkIds must be unique; got {link_ids}"
    expected_pairs = {
        (200000, 200002),
        (200000, 200003),
        (200000, 200004),
        (200001, 200002),
        (200001, 200003),
        (200001, 200004),
    }
    assert {(start, end) for _, start, end, _ in links} == expected_pairs
    assert all(ga_id == 3 for _, _, _, ga_id in links)


def test_hidden_link_ids_differ_from_raw_ga_id() -> None:
    # Regression guard for the original bug shape: the LinkId must NOT be the
    # bare ga.id (that caused ed.link() to collapse pairs onto one record).
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
                Assignment(102, 502, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    _seed_pin(panel, 502, in_pin=100002, out_pin=None)
    for link_id, _, _, _ in _visual_links(panel):
        assert link_id != 7, "LinkId must not be the raw ga.id"
        assert link_id != link_id // 1_000_000 or link_id >= 1_000_000


def test_hidden_multiple_gas_get_disjoint_link_id_ranges() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(1, "1/1", "a"), GroupAddress(2, "1/2", "b")],
        assignments_by_ga={
            1: [
                Assignment(10, 100, 1, is_sending=True),
                Assignment(11, 101, 1, is_sending=False),
            ],
            2: [
                Assignment(20, 200, 2, is_sending=True),
                Assignment(21, 201, 2, is_sending=False),
                Assignment(22, 202, 2, is_sending=False),
            ],
        },
    )
    _seed_pin(panel, 100, in_pin=None, out_pin=100000)
    _seed_pin(panel, 101, in_pin=100001, out_pin=None)
    _seed_pin(panel, 200, in_pin=None, out_pin=200000)
    _seed_pin(panel, 201, in_pin=200001, out_pin=None)
    _seed_pin(panel, 202, in_pin=200002, out_pin=None)

    links = _visual_links(panel)
    link_ids = [link_id for link_id, _, _, _ in links]
    assert len(set(link_ids)) == len(link_ids)
    ga_ids = sorted({ga_id for _, _, _, ga_id in links})
    assert ga_ids == [1, 2]
    # No link_id of GA 1 may collide with any link_id of GA 2 (or vice versa).
    for link_id, _, _, ga_id in links:
        assert link_id // 1_000_000 == ga_id, (
            f"link_id {link_id} should encode ga_id {ga_id}"
        )


# ---------------------------------------------------------------------------
# GA-shown mode (_show_ga_nodes = True) - preserved behaviour + ga_id thread
# ---------------------------------------------------------------------------


def test_shown_ga_links_route_through_ga_node_pins() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    _set_ga_pins(panel, 7, (3000001, 3000002))
    _set_show_ga_nodes(panel, True)

    links = _visual_links(panel)
    assert links == [
        (7 * 10000 + 0, 100000, 3000001, 7),
        (7 * 10000 + 5000 + 0, 3000002, 100001, 7),
    ]


def test_shown_ga_multi_receiver_links_have_unique_ids() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
                Assignment(102, 502, 7, is_sending=False),
                Assignment(103, 503, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    _seed_pin(panel, 502, in_pin=100002, out_pin=None)
    _seed_pin(panel, 503, in_pin=100003, out_pin=None)
    _set_ga_pins(panel, 7, (3000001, 3000002))
    _set_show_ga_nodes(panel, True)

    links = _visual_links(panel)
    link_ids = [link_id for link_id, _, _, _ in links]
    assert len(set(link_ids)) == len(link_ids), f"unique: {link_ids}"
    assert all(ga_id == 7 for _, _, _, ga_id in links)
    # 1 in-link (sender -> GA) + 3 out-links (GA -> receivers) = 4 curves.
    assert len(links) == 4


# ---------------------------------------------------------------------------
# Derivative behaviours that consume _compute_visual_links
# ---------------------------------------------------------------------------


def test_link_exists_matches_on_either_pin_order() -> None:
    panel = _make_panel(
        group_addresses=[GroupAddress(7, "1/7", "n")],
        assignments_by_ga={
            7: [
                Assignment(100, 500, 7, is_sending=True),
                Assignment(101, 501, 7, is_sending=False),
            ]
        },
    )
    _seed_pin(panel, 500, in_pin=None, out_pin=100000)
    _seed_pin(panel, 501, in_pin=100001, out_pin=None)
    assert _link_exists(panel, 100000, 100001) is True
    assert _link_exists(panel, 100001, 100000) is True
    assert _link_exists(panel, 100000, 999999) is False


# ---------------------------------------------------------------------------
# _handle_link_deletion: visual LinkId -> ga_id reverse-map threading
#
# `_render_links` repopulates `_visual_link_id_to_ga_id` each frame and
# `_handle_link_deletion` must look the deleted visual LinkId up in it before
# calling `_remove_link`, so the underlying GA (not the composite visual id)
# is what gets removed. This wires the editor's composite LinkIds back to the
# GA-granular deletion API in plugin.py. The imgui_node_editor entry points
# are stubbed here so the deletion control flow runs headless; the real
# editor's no-collapse behaviour is covered by the e2e test under
# ``src/knx_gui/testing/tests/test_node_editor_links.py``.


class _FakeLinkId:
    """Mutable stand-in for ``imgui_node_editor.LinkId``.

    The real ``query_deleted_link(link_id)`` mutates the LinkId passed to it
    and returns True while there are more deleted links; ``_FakeLinkId`` lets
    the fake query callback set ``._value`` between iterations the same way.
    """

    def __init__(self, value: int = 0) -> None:
        self._value = value

    def id(self) -> int:
        return self._value


def _run_deletion(
    panel: NodeEditorPanel,
    deleted_link_ids: list[int],
    *,
    begin_delete: bool = True,
    accept: bool = True,
) -> list[int]:
    """Drive ``_handle_link_deletion`` with stubbed ed calls and record the
    ga_ids handed to ``_remove_link``."""
    removed: list[int] = []
    _set_remove_link(panel, removed.append)
    state: dict[str, int] = {"i": 0}

    def fake_begin_delete() -> bool:
        return begin_delete

    def fake_query(link_id: Any) -> bool:
        i = state["i"]
        state["i"] += 1
        if i < len(deleted_link_ids):
            link_id._value = deleted_link_ids[i]
            return True
        return False

    def fake_accept() -> bool:
        return accept

    with (
        patch.object(ed, "begin_delete", fake_begin_delete),
        patch.object(ed, "query_deleted_link", fake_query),
        patch.object(ed, "accept_deleted_item", fake_accept),
        patch.object(ed, "end_delete", lambda: None),
        patch.object(ed, "LinkId", _FakeLinkId),
    ):
        _handle_deletion(panel)
    return removed


def test_handle_link_deletion_translates_visual_link_id_to_ga_id() -> None:
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    _set_link_map(panel, {7000000: 7, 7000001: 7, 7000002: 7})
    removed = _run_deletion(panel, [7000000, 7000002])
    assert removed == [7, 7]


def test_handle_link_deletion_skips_visual_link_id_unknown_to_map() -> None:
    # A visual LinkId that isn't in the reverse map (e.g. stale editor link
    # after a model change) must be silently skipped, not crash or pass a
    # bogus ga_id down to _remove_link.
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    _set_link_map(panel, {7000000: 7})
    removed = _run_deletion(panel, [7000000, 9999999, 7000000])
    assert removed == [7, 7]


def test_handle_link_deletion_noop_when_begin_delete_is_false() -> None:
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    _set_link_map(panel, {7000000: 7})
    removed = _run_deletion(panel, [7000000], begin_delete=False)
    assert removed == []


def test_handle_link_deletion_skips_removal_when_accept_returns_false() -> None:
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    _set_link_map(panel, {7000000: 7})
    removed = _run_deletion(panel, [7000000, 7000001], accept=False)
    assert removed == []


def test_handle_link_deletion_uses_per_ga_reverse_map_entries() -> None:
    # Two GAs each with multiple visual links: deleting one visual link from
    # each GA must remove only that GA, by ga_id - not the composite link id.
    panel = _make_panel(group_addresses=[], assignments_by_ga={})
    _set_link_map(panel, {1_000_000: 1, 2_000_005: 2, 1_000_001: 1})
    removed = _run_deletion(panel, [1_000_001, 2_000_005, 1_000_000])
    assert removed == [1, 2, 1]
