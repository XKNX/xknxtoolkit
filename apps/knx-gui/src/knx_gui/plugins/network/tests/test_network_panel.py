"""Regression tests for NetworkPanel selection / filter / copy logic.

These cover the coordinate-space bug introduced in commit 7855f42
(``feat(knx-gui): redesign telegrams panel with improved UX``):
``_render_table`` enumerated the *filtered* telegram list, so ``_selected``
stored filtered-list positions, but ``_copy_telegrams`` resolved those same
positions against the *unfiltered* list returned by ``get_telegrams``. Under
an active filter a single clicked row and a Shift-click range therefore
copied different rows than the ones the user selected.

The logic under test does not drive the Dear ImGui render loop, so no display
is required: importing ``imgui_bundle`` is headless-safe and only
``imgui.set_clipboard_text`` is patched to capture what the panel would place
on the clipboard.
"""

import pytest
from imgui_bundle import imgui
from xknx.dpt.payload import DPTBinary
from xknx.telegram.apci import GroupValueRead, GroupValueWrite

from knx_gui.plugins.network.records import TelegramRecord
from knx_gui.plugins.network.tests.conftest import make_telegram_record
from knx_gui.plugins.network.ui import CaptureState, NetworkPanel

HEADER = "Time\tVia\tSource\tDestination\tTPCI\tAPCI\tDPT\tValue"


def _build_panel(recs: list[TelegramRecord]) -> NetworkPanel:
    return NetworkPanel(
        get_telegrams=lambda: recs,
        get_cemi_records=lambda: [],
        get_capture_state=lambda: CaptureState.STOPPED,
        on_start=lambda: None,
        on_stop=lambda: None,
        on_clear=lambda: None,
        on_focus_source=lambda _s: None,
    )


def _filtered(panel: NetworkPanel) -> list[TelegramRecord]:
    return panel._filtered_telegrams()  # pyright: ignore[reportPrivateUsage]


def _set_filter(panel: NetworkPanel, text: str) -> None:
    panel._filter_text = text  # pyright: ignore[reportPrivateUsage]


def _set_selected(panel: NetworkPanel, indices: set[int]) -> None:
    panel._selected = set(indices)  # pyright: ignore[reportPrivateUsage]


def _selected(panel: NetworkPanel) -> set[int]:
    return set(panel._selected)  # pyright: ignore[reportPrivateUsage]


def _last_selected(panel: NetworkPanel) -> int:
    return panel._last_selected  # pyright: ignore[reportPrivateUsage]


def _select_single(panel: NetworkPanel, index: int, t: TelegramRecord) -> None:
    panel._select_single(index, t)  # pyright: ignore[reportPrivateUsage]


def _select_range(panel: NetworkPanel, start: int, end: int, *, additive: bool) -> None:
    panel._select_range(start, end, additive=additive)  # pyright: ignore[reportPrivateUsage]


def _set_filter_text(panel: NetworkPanel, text: str) -> None:
    panel._set_filter_text(text)  # pyright: ignore[reportPrivateUsage]


def _copy(panel: NetworkPanel, monkeypatch: pytest.MonkeyPatch) -> str:
    captured: dict[str, str] = {}

    def fake_set_clipboard_text(text: str) -> None:
        captured["v"] = text

    monkeypatch.setattr(imgui, "set_clipboard_text", fake_set_clipboard_text)
    panel._copy_telegrams()  # pyright: ignore[reportPrivateUsage]
    return captured.get("v", "")


def _sources(clipboard: str) -> list[str]:
    lines = clipboard.split("\n")
    return [ln.split("\t")[2] for ln in lines[1:] if ln.strip()]


def _distinct_recs() -> list[TelegramRecord]:
    return [
        make_telegram_record("1.1.10", "0/0/1", GroupValueWrite(DPTBinary(1)), 0),
        make_telegram_record("1.1.15", "0/0/2", GroupValueRead(), 1),
        make_telegram_record("1.1.20", "0/0/3", GroupValueWrite(DPTBinary(0)), 2),
    ]


def _shared_dest_recs() -> list[TelegramRecord]:
    return [
        make_telegram_record("1.1.10", "0/0/1", GroupValueWrite(DPTBinary(1)), 0),
        make_telegram_record("1.1.15", "0/0/2", GroupValueRead(), 1),
        make_telegram_record("1.1.20", "0/0/2", GroupValueWrite(DPTBinary(0)), 2),
    ]


# --- _filtered_telegrams -------------------------------------------------


def test_filtered_telegrams_no_filter_returns_all(
    mock_telegrams: list[TelegramRecord],
) -> None:
    panel = _build_panel(mock_telegrams)
    assert _filtered(panel) is mock_telegrams
    assert _filtered(panel) == mock_telegrams


def test_filtered_telegrams_matches_destination() -> None:
    panel = _build_panel(_distinct_recs())
    _set_filter(panel, "0/0/2")
    assert [t.source for t in _filtered(panel)] == ["1.1.15"]


def test_filtered_telegrams_no_match_returns_empty() -> None:
    panel = _build_panel(_distinct_recs())
    _set_filter(panel, "nonexistent")
    assert _filtered(panel) == []


# --- _copy_telegrams: the coordinate-space fix ----------------------------


def test_copy_single_filtered_index_returns_clicked_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _build_panel(_distinct_recs())
    _set_filter(panel, "0/0/2")
    assert [t.source for t in _filtered(panel)] == ["1.1.15"]
    _set_selected(panel, {0})

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == ["1.1.15"]
    assert "1.1.15" in clipboard
    assert "1.1.10" not in clipboard
    assert clipboard.startswith(HEADER)


def test_copy_shift_range_filtered_indices_returns_clicked_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _build_panel(_shared_dest_recs())
    _set_filter(panel, "0/0/2")
    assert [t.source for t in _filtered(panel)] == ["1.1.15", "1.1.20"]
    _set_selected(panel, {0, 1})

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == ["1.1.15", "1.1.20"]
    assert "1.1.10" not in clipboard
    assert "1.1.20" in clipboard


# --- _copy_telegrams: no-filter regression guards ------------------------


def test_copy_no_filter_with_selection_returns_selected_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _build_panel(_distinct_recs())
    assert panel._filter_text == ""  # pyright: ignore[reportPrivateUsage]
    _set_selected(panel, {1})

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == ["1.1.15"]


def test_copy_no_filter_no_selection_copies_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recs = _distinct_recs()
    panel = _build_panel(recs)
    _set_selected(panel, set())

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == [r.source for r in recs]


# --- _copy_telegrams: copy respects the active filter --------------------


def test_copy_with_filter_no_selection_copies_only_filtered_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _build_panel(_shared_dest_recs())
    _set_filter(panel, "0/0/2")
    _set_selected(panel, set())

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == ["1.1.15", "1.1.20"]
    assert "1.1.10" not in clipboard


# --- _set_filter_text: invalidate selection on filter change -------------


def test_set_filter_text_change_clears_selection_and_anchor() -> None:
    panel = _build_panel(_distinct_recs())
    _set_filter(panel, "old")
    _set_selected(panel, {0, 1, 2})
    panel._last_selected = 1  # pyright: ignore[reportPrivateUsage]

    _set_filter_text(panel, "new")

    assert panel._filter_text == "new"  # pyright: ignore[reportPrivateUsage]
    assert _selected(panel) == set()
    assert _last_selected(panel) == -1


def test_set_filter_text_unchanged_preserves_selection_and_anchor() -> None:
    panel = _build_panel(_distinct_recs())
    _set_filter(panel, "same")
    _set_selected(panel, {2})
    panel._last_selected = 2  # pyright: ignore[reportPrivateUsage]

    _set_filter_text(panel, "same")

    assert panel._filter_text == "same"  # pyright: ignore[reportPrivateUsage]
    assert _selected(panel) == {2}
    assert _last_selected(panel) == 2


def test_set_filter_text_then_copy_uses_new_filter_space(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    panel = _build_panel(_shared_dest_recs())
    _set_filter(panel, "1.1.10")
    _select_single(panel, 0, _filtered(panel)[0])
    assert _selected(panel) == {0}

    _set_filter_text(panel, "0/0/2")
    assert _selected(panel) == set()

    _select_single(panel, 0, _filtered(panel)[0])
    _select_range(panel, _last_selected(panel), 1, additive=False)

    clipboard = _copy(panel, monkeypatch)

    assert _sources(clipboard) == ["1.1.15", "1.1.20"]
    assert "1.1.10" not in clipboard
