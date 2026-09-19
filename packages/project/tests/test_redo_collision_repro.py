"""Regression tests for ``EventStore.append`` truncating the redo branch at ``cursor == 0``.

Before the fix, ``append`` only deleted the redo branch when ``self._cursor > 0``. Undoing the
whole history left the reverted "orphan" events in the ``events`` table, so appending a new event
at ``cursor == 0`` did not truncate them. This had two consequences:

1. **Silent wrong state**: after ``undo-all -> append -> undo``, ``redo`` replayed an abandoned
   orphan instead of the just-undone event (no error, just the wrong row reappearing).
2. **IntegrityError**: for row-creating events that capture their autoincrement id on first
   ``apply``, replaying the new event after the orphans re-inserted the same captured id and
   raised ``UNIQUE constraint failed: <table>.id``, bricking the SQLAlchemy session.

The fix drops the ``if self._cursor > 0`` guard so the redo branch is truncated unconditionally,
matching the module docstring's already-stated invariant.
"""

from pathlib import Path

from xknxmono.project import ProjectService

PRODUCT = "M-0001_H-x-1_P-1"


def _new(tmp_path: Path, name: str = "p") -> tuple[ProjectService, str]:
    svc = ProjectService()
    pid = svc.create(tmp_path / f"{name}.xknx", "P-0001")
    return svc, pid


def _backbone_segment(svc: ProjectService, pid: str) -> int:
    """The default backbone segment (Area 0 / Line 0) the skeleton ships with."""
    return svc.topology(pid, 0).areas[0].lines[0].segments[0].id


def _undo_all(svc: ProjectService, pid: str) -> None:
    while svc.undo(pid):
        pass


def test_append_at_cursor_zero_deletes_reverted_events(tmp_path: Path) -> None:
    """Appending at ``cursor == 0`` truncates the reverted orphan events (the core invariant)."""
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="A")
    svc.add_device(pid, seg, PRODUCT, address=2, name="B")
    _undo_all(svc, pid)  # cursor 0; events 1 & 2 left reverted
    assert [(e.id, e.reverted) for e in svc.history(pid)] == [(2, True), (1, True)]

    svc.add_device(pid, seg, PRODUCT, address=1, name="C")  # append at cursor 0

    # the orphan redo branch is truncated; only the new event remains, nothing to redo
    entries = svc.history(pid)
    assert len(entries) == 1
    assert entries[0].reverted is False
    assert not svc.can_redo(pid)


def test_redo_after_undo_all_append_replays_just_undone_event(tmp_path: Path) -> None:
    """After ``undo-all -> append -> undo``, ``redo`` replays the just-undone event, not an orphan.

    This is the silent-wrong-state form of the bug: with the orphan branch left in place, the
    user saw the wrong row reappear with no error. With the fix, ``redo`` replays the event
    just undone and then returns ``False`` (no abandoned branch to walk into).
    """
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="A")
    svc.add_device(pid, seg, PRODUCT, address=2, name="B")
    _undo_all(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="C")  # append at cursor 0
    assert [d.name for d in svc.devices(pid)] == ["C"]
    assert svc.undo(pid)  # undo C -> cursor 0
    assert svc.cursor(pid) == 0

    assert svc.redo(pid)  # replays C, the just-undone event — not the orphan "A"
    assert [d.name for d in svc.devices(pid)] == ["C"]
    assert not svc.redo(pid)  # the abandoned redo branch is gone


def test_add_device_undo_all_append_redo_no_collision(tmp_path: Path) -> None:
    """The crash form: redoing forward after ``undo-all -> append -> undo`` raises no
    ``IntegrityError`` on the captured autoincrement id (the canonical single-row case)."""
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="A")
    svc.add_device(pid, seg, PRODUCT, address=2, name="B")
    _undo_all(svc, pid)
    svc.add_device(
        pid, seg, PRODUCT, address=1, name="C"
    )  # device_id clashes with orphan A
    assert svc.undo(pid)  # undo C -> cursor 0

    # replay forward to the end; with the bug the third redo re-inserted id=1 and raised
    # ``UNIQUE constraint failed: devices.id``. With the fix only C is replayed.
    while svc.redo(pid):
        pass
    assert [d.name for d in svc.devices(pid)] == ["C"]
    assert not svc.can_redo(pid)
