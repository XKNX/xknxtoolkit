from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepeatScope:
    instance_idx: int


@dataclass(frozen=True)
class ModuleScope:
    module_id: str
    def_ref_id: str


class EvalContext:
    """Carries parameter state and the current module/repeat scope during tree evaluation."""

    __slots__ = ("_parent", "_scope", "_state")

    def __init__(
        self,
        state: dict[str, str],
        parent: EvalContext | None = None,
        scope: RepeatScope | ModuleScope | None = None,
    ) -> None:
        self._state = state
        self._parent = parent
        self._scope = scope

    def _instance_idx(self) -> int:
        if isinstance(self._scope, RepeatScope):
            return self._scope.instance_idx
        if self._parent is not None:
            return self._parent._instance_idx()
        return 1

    def qualify(self, ref_id: str) -> str:
        """Translate a module-def-relative ref ID to its instance-qualified form."""
        if isinstance(self._scope, ModuleScope) and ref_id.startswith(
            self._scope.def_ref_id
        ):
            idx = self._parent._instance_idx() if self._parent is not None else 1
            return (
                self._scope.module_id
                + f"_MI-{idx}"
                + ref_id[len(self._scope.def_ref_id) :]
            )
        if self._parent is not None:
            return self._parent.qualify(ref_id)
        return ref_id

    def get(self, ref_id: str, default: str = "") -> str:
        return self._state.get(self.qualify(ref_id), default)

    def set(self, ref_id: str, value: str) -> None:
        self._state[self.qualify(ref_id)] = value

    def repeat_ctx(self, instance_idx: int) -> EvalContext:
        """Return a context for a specific repeat iteration index."""
        return EvalContext(self._state, self, RepeatScope(instance_idx))

    def module_ctx(self, module_id: str, def_ref_id: str) -> EvalContext:
        """Return a context for evaluating inside a module instance."""
        return EvalContext(self._state, self, ModuleScope(module_id, def_ref_id))
