"""Tracks background work for the status bar - see apps/knx-gui/CLAUDE.md's
"Tasks plugin" section for the design."""

from __future__ import annotations

import itertools
from concurrent.futures import Future
from dataclasses import dataclass, replace
from typing import Any, Literal

TaskStatus = Literal["queued", "running", "error"]

_STATUS_ORDER: dict[TaskStatus, int] = {"running": 0, "queued": 1, "error": 2}


@dataclass(frozen=True)
class Task:
    id: int
    label: str
    status: TaskStatus
    detail: str = ""  # only ever meaningful for status == "error"


class TaskService:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._ids = itertools.count(1)

    def add(self, label: str, *, status: TaskStatus = "running") -> int:
        """Returns an id for later `update`/`remove` calls. Prefer `track` for
        `Future`-backed work."""
        task_id = next(self._ids)
        self._tasks[task_id] = Task(id=task_id, label=label, status=status)
        return task_id

    def update(
        self,
        task_id: int,
        *,
        label: str | None = None,
        status: TaskStatus | None = None,
        detail: str | None = None,
    ) -> None:
        """No-op if `task_id` is unknown."""
        task = self._tasks.get(task_id)
        if task is None:
            return
        self._tasks[task_id] = replace(
            task,
            label=task.label if label is None else label,
            status=task.status if status is None else status,
            detail=task.detail if detail is None else detail,
        )

    def remove(self, task_id: int) -> None:
        self._tasks.pop(task_id, None)

    def tasks(self) -> list[Task]:
        """Running first, then queued, then errors."""
        return sorted(
            self._tasks.values(), key=lambda t: (_STATUS_ORDER[t.status], t.id)
        )

    def track(self, label: str, future: Future[Any]) -> int:
        """Removed on success/cancellation, turned into an `error` on failure."""
        task_id = self.add(label, status="running")
        future.add_done_callback(lambda f: self._resolve(task_id, f))
        return task_id

    def _resolve(self, task_id: int, future: Future[Any]) -> None:
        if future.cancelled():
            self.remove(task_id)
            return
        exc = future.exception()
        if exc is None:
            self.remove(task_id)
        else:
            self.update(task_id, status="error", detail=str(exc))
