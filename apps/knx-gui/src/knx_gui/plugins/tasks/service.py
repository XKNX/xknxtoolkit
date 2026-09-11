"""Tracks background work - loading a knxprod, programming a device, exporting
group addresses - so the status bar can show it without knowing what any of
those plugins actually do. Plugins report in through this service; nothing
here knows what a knxprod is.

No progress percentage: a task is either `queued` (waiting its turn), `running`
(shown with a spinner - that's the only feedback while it's in flight) or
`error` (something needs the user's attention, so it stays until dismissed).
There is deliberately no `done` status - a task that finishes cleanly is
removed outright (see `track`), rather than lingering as a badge nobody needs
to read once it's over.

Rendering is immediate-mode, like the rest of this app (see `ConnectionService`
`_state`, or any of the `get_x: Callable[[], ...]` panel constructors) - there
is no subscribe/notify here. A consumer just calls `tasks()` every frame;
nothing pushes.
"""

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
        """Start tracking one unit of work, returning its id for later `update`/
        `remove` calls. If the work is already backed by a `Future` (most
        connection.service calls are), use `track` instead - it resolves the
        task automatically instead of needing a matching `update`/`remove`."""
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
        """No-op if `task_id` is unknown (already removed, or never existed) -
        callers don't need to guard every update against a task having finished
        out from under them."""
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
        """Running first, then queued, then errors - each group in the order
        it was added. Matches how the status bar groups tasks for display."""
        return sorted(
            self._tasks.values(), key=lambda t: (_STATUS_ORDER[t.status], t.id)
        )

    def track(self, label: str, future: Future[Any]) -> int:
        """Add a running task that resolves itself from `future`: removed
        outright on success or cancellation, turned into an `error` (with the
        exception text as `detail`) on failure. `future.add_done_callback` fires
        on whichever thread the future completes on (see
        `ConnectionService.run_async`) - same no-lock, plain-mutation pattern
        already used for restart/program results in the Configure panel.
        """
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
