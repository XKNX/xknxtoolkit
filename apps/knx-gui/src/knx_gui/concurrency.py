"""A tiny guard for service reads during a background import.

A long ``.knxproj`` import runs on a worker thread that mutates the catalog and project databases.
The GUI panels read those same services every frame on the UI thread. To keep the UI responsive
without racing the writer, the importer holds a shared *re-entrant* lock for the whole import, and
every per-frame service read is wrapped with :func:`io_guarded`: it acquires the lock without
blocking and, if the importer holds it, returns an empty placeholder instead of touching the
database. Because the lock is re-entrant, the importing thread itself (which already holds it) still
reads real data while building the project view.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any


def io_guarded[T](
    default_factory: Callable[[], T],
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Return the wrapped read's result, or ``default_factory()`` if a background import is running.

    The instance must expose a re-entrant ``self._io_lock`` (``threading.RLock``)."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
            if not self._io_lock.acquire(blocking=False):
                return default_factory()
            try:
                return fn(self, *args, **kwargs)
            finally:
                self._io_lock.release()

        return wrapper

    return decorator
