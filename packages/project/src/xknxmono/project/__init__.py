"""xknx-project: an editable KNX project stored as a relational SQLite document.

A project is one on-disk SQLite database; edits go through a command-based
:class:`~xknxmono.project.core.service.ProjectService` that records each command in an ``events``
history for undo/redo. The package defines its own topology/group-address models
(:mod:`xknxmono.project.models`) — a subset of the KNX IR, not the IR itself. See
:mod:`xknxmono.project.core`.
"""

__version__ = "0.1.0"

from xknxmono.project.core import ProjectService

__all__ = ["ProjectService"]
