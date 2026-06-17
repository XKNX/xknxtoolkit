from __future__ import annotations

from xknxmono.models.intermediate import (
    ModuleArg,
    ModuleInstance,
    ModuleTextArg,
    ParameterInstanceRef,
)

from .application_indexer import ApplicationIndexer


def compute_arg_defaults(mod_def_arguments: object, instance_args: list[ModuleArg]) -> dict[str, str]:
    """Return {arg_name: value} for all text args in a module instance."""
    result: dict[str, str] = {}
    if mod_def_arguments is None:
        return result
    arg_def_by_id = {a.id: a for a in getattr(mod_def_arguments, "argument", [])}
    for arg in instance_args:
        if isinstance(arg, ModuleTextArg):
            arg_def = arg_def_by_id.get(arg.ref_id)
            if arg_def is not None:
                result[arg_def.name] = arg.value
    return result


def compute_param_ref_defaults(refs_container: object, idx: ApplicationIndexer) -> dict[str, str]:
    """Return {pr.id: effective_value} for all ParameterRefs in a static section.

    Tries pr.value first; falls back to the base Parameter's value via idx.
    """
    result: dict[str, str] = {}
    refs = getattr(refs_container, "parameter_ref", None) if refs_container is not None else None
    if not refs:
        return result
    for pr in refs:
        value = pr.value
        if value is None:
            base = idx.parameters.get(pr.ref_id)
            if base is not None:
                value = base.value
        if value is not None:
            result[pr.id] = value
    return result


class _ParameterState:
    """Shared base for GlobalState and ModuleState.

    Forms a tree: root → module children → submodule children.
    Reads walk the parent chain; writes go to the node itself only.
    Text overrides (from Rename nodes) are scope-local only — no parent walk.

    Active ref sets persist after trim_to_active() and are cleared by reset_active()
    at the start of each traversal, so callers can read active_param_refs() /
    active_com_object_refs() after ui() or evaluate() returns.
    """

    __slots__ = (
        "_active_com_object_refs",
        "_active_param_refs",
        "_children",
        "_param_ref_defaults",
        "_parent",
        "_text",
        "param_ref_id_to_value",
    )

    def __init__(self, values: dict[str, str] | None = None, parent: _ParameterState | None = None, param_ref_defaults: dict[str, str] | None = None) -> None:
        self.param_ref_id_to_value: dict[str, str] = dict(values or {})
        self._parent: _ParameterState | None = parent
        self._children: dict[str, ModuleState] = {}
        self._text: dict[str, str] = {}
        self._active_param_refs: set[str] = set()
        self._active_com_object_refs: set[str] = set()
        self._param_ref_defaults: dict[str, str] = param_ref_defaults or {}

    def get(self, ref_id: str) -> str | None:
        val = self.param_ref_id_to_value.get(ref_id)
        if val is not None:
            return val
        if self._parent is not None:
            parent_val = self._parent.get(ref_id)
            if parent_val is not None:
                return parent_val
        return self._param_ref_defaults.get(ref_id)

    def set_param_ref_defaults(self, param_ref_defaults: dict[str, str]) -> None:
        self._param_ref_defaults = param_ref_defaults

    def get_arg_defaults(self) -> dict[str, str]:
        return {}

    def set(self, ref_id: str, value: str) -> None:
        self.param_ref_id_to_value[ref_id] = value

    def set_text(self, ref_id: str, text: str) -> None:
        self._text[ref_id] = text

    def get_text(self, ref_id: str) -> str | None:
        return self._text.get(ref_id)

    def mark_active_param(self, ref_id: str) -> None:
        self._active_param_refs.add(ref_id)

    def mark_active_com_object(self, ref_id: str) -> None:
        self._active_com_object_refs.add(ref_id)

    def reset_active(self) -> None:
        """Clear active ref sets before a new traversal."""
        self._active_param_refs.clear()
        self._active_com_object_refs.clear()
        for child in self._children.values():
            child.reset_active()

    def trim_to_active(self) -> None:
        """Remove values for param refs not marked active, then recurse into module children.

        Active ref sets are NOT cleared here — they persist so callers can read
        active_param_refs() / active_com_object_refs() after the traversal.
        """
        inactive = self.param_ref_id_to_value.keys() - self._active_param_refs
        for key in inactive:
            del self.param_ref_id_to_value[key]
        self._text.clear()
        for child in self._children.values():
            child.trim_to_active()

    def active_param_refs(self) -> set[str]:
        result = set(self._active_param_refs)
        for child in self._children.values():
            result.update(child.active_param_refs())
        return result

    def active_com_object_refs(self) -> set[str]:
        result = set(self._active_com_object_refs)
        for child in self._children.values():
            result.update(child.active_com_object_refs())
        return result

    def qualify(self, ref_id: str) -> str:
        return ref_id

    def find_scope_for_qualified(self, ref_id: str) -> tuple[_ParameterState, str] | None:
        for child in self._children.values():
            result = child.find_scope_for_qualified(ref_id)
            if result is not None:
                return result
        return None

    def set_instance_ref(self, ref_id: str, value: str) -> None:
        found = self.find_scope_for_qualified(ref_id)
        if found is not None:
            scope, local = found
            scope.set(local, value)
        else:
            self.set(ref_id, value)

    def module_child(self, module_id: str, repeat_idx: int = 1, arguments: dict[str, ModuleArg] | None = None, param_ref_defaults: dict[str, str] | None = None, arg_defaults: dict[str, str] | None = None) -> ModuleState:
        """Returns (creating if needed) the module instance state and wires it into the tree."""
        key = f"{module_id}_MI-{repeat_idx}"
        if key not in self._children:
            child = ModuleState(key, arguments, param_ref_defaults=param_ref_defaults, arg_defaults=arg_defaults)
            child._parent = self
            self._children[key] = child
        else:
            child = self._children[key]
            child._parent = self
            if param_ref_defaults is not None:
                child.set_param_ref_defaults(param_ref_defaults)
            if arg_defaults is not None:
                child.set_arg_defaults(arg_defaults)
        return self._children[key]

    def parameter_instance_refs(self) -> dict[str, str]:
        result = dict(self.param_ref_id_to_value)
        for child in self._children.values():
            result.update(child.parameter_instance_refs())
        return result

    def module_instances(self) -> list[tuple[str, str, dict[str, ModuleArg]]]:
        result: list[tuple[str, str, dict[str, ModuleArg]]] = []
        for child in self._children.values():
            result.extend(child.module_instances())
        return result


class GlobalState(_ParameterState):
    """Global (root) parameter state; top of the tree from which module children hang."""

    @classmethod
    def from_project(
        cls,
        parameter_instance_refs: list[ParameterInstanceRef] | None = None,
        module_instances: list[ModuleInstance] | None = None,
    ) -> GlobalState:
        """Reconstruct a GlobalState tree from saved project data (parameter refs + module instance list)."""
        root = cls()
        mid_to_mdid: dict[str, str] = {}
        for mi in module_instances or []:
            if mi.id is None or mi.ref_id is None:
                continue
            ms = ModuleState(mi.id)
            ms._parent = root
            root._children[mi.id] = ms
            mid_to_mdid[mi.id] = mi.ref_id

        for pir in parameter_instance_refs or []:
            if pir.value is None:
                continue
            ref_id, value = pir.ref_id, pir.value
            for mid, ms in root._children.items():
                p = f"_{ref_id}_".find(f"_{mid}_")
                if p != -1:
                    app_prefix = ref_id[:p]
                    suffix = ref_id[p + len(mid):]
                    ms.module_instance_id = app_prefix + mid
                    ms.param_ref_id_to_value[app_prefix + mid_to_mdid[mid] + suffix] = value
                    break
            else:
                root.param_ref_id_to_value[ref_id] = value

        return root


class ModuleState(_ParameterState):
    """Parameter state for one module instance; stores local (def-relative) ref IDs.

    parameter_instance_refs() qualifies each key by splicing module_instance_id in place of the
    shared prefix with the local ref ID — no def_ref_id needed at eval time.
    e.g. M-..._MD-1_P-5_R-5  →  M-..._MD-1_M-100_MI-2_P-5_R-5
    """

    __slots__ = ("_arg_defaults", "arguments", "module_instance_id")

    def __init__(self, module_instance_id: str, arguments: dict[str, ModuleArg] | None = None, param_ref_defaults: dict[str, str] | None = None, arg_defaults: dict[str, str] | None = None) -> None:
        super().__init__(param_ref_defaults=param_ref_defaults)
        self.module_instance_id = module_instance_id
        self.arguments: dict[str, ModuleArg] = arguments or {}
        self._arg_defaults: dict[str, str] = arg_defaults or {}

    def get_arg_defaults(self) -> dict[str, str]:
        return self._arg_defaults

    def set_arg_defaults(self, arg_defaults: dict[str, str]) -> None:
        self._arg_defaults = arg_defaults

    def get_arg(self, ref_id: str) -> ModuleArg | None:
        return self.arguments.get(ref_id)

    def as_module_instance(self) -> tuple[str, str, dict[str, ModuleArg]]:
        instance_id = self.module_instance_id
        ref_id = instance_id.rsplit("_MI-", 1)[0]
        args = {k[k.find("_MD-") + 1:]: v for k, v in self.arguments.items()}
        return instance_id, ref_id, args

    def qualify(self, ref_id: str) -> str:
        return self._qualify(ref_id)

    def find_scope_for_qualified(self, ref_id: str) -> tuple[_ParameterState, str] | None:
        mid = self.module_instance_id
        if not ref_id.startswith(mid + "_"):
            return None
        for child in self._children.values():
            result = child.find_scope_for_qualified(ref_id)
            if result is not None:
                return result
        suffix = ref_id[len(mid):]
        common_prefix = mid.rsplit("_MI-", 1)[0].rsplit("_", 1)[0]
        return (self, common_prefix + suffix)

    def _qualify(self, ref_id: str) -> str:
        i, n = 0, min(len(self.module_instance_id), len(ref_id))
        while i < n and self.module_instance_id[i] == ref_id[i]:
            i += 1
        return self.module_instance_id + ref_id[i - 1:]

    def active_param_refs(self) -> set[str]:
        result = {self.qualify(ref) for ref in self._active_param_refs}
        for child in self._children.values():
            result.update(child.active_param_refs())
        return result

    def active_com_object_refs(self) -> set[str]:
        result = {self.qualify(ref) for ref in self._active_com_object_refs}
        for child in self._children.values():
            result.update(child.active_com_object_refs())
        return result

    def parameter_instance_refs(self) -> dict[str, str]:
        result = {self._qualify(k): v for k, v in self.param_ref_id_to_value.items()}
        for child in self._children.values():
            result.update(child.parameter_instance_refs())
        return result

    def module_instances(self) -> list[tuple[str, str, dict[str, ModuleArg]]]:
        result: list[tuple[str, str, dict[str, ModuleArg]]] = [self.as_module_instance()]
        for child in self._children.values():
            result.extend(child.module_instances())
        return result


class EvalContext:
    """Scope handle: the active state node plus a pending repeat index for the next module_child call.

    Reads delegate to the active state, which walks its parent chain (submodule → module → global).
    Writes go to the active state only.
    """

    __slots__ = ("_repeat_idx", "_scope")

    def __init__(self, scope: _ParameterState, repeat_idx: int = 1) -> None:
        self._scope = scope
        self._repeat_idx = repeat_idx

    def get(self, ref_id: str) -> str | None:
        return self._scope.get(ref_id)

    def qualify(self, ref_id: str) -> str:
        return self._scope.qualify(ref_id)

    def set(self, ref_id: str, value: str) -> None:
        self._scope.set(ref_id, value)

    def set_text(self, ref_id: str, text: str) -> None:
        self._scope.set_text(ref_id, text)

    def get_text(self, ref_id: str) -> str | None:
        return self._scope.get_text(ref_id)

    def mark_active_param(self, ref_id: str) -> None:
        self._scope.mark_active_param(ref_id)

    def mark_active_com_object(self, ref_id: str) -> None:
        self._scope.mark_active_com_object(ref_id)

    def repeat_ctx(self, repeat_idx: int) -> EvalContext:
        return EvalContext(self._scope, repeat_idx)

    def get_arg_defaults(self) -> dict[str, str]:
        return self._scope.get_arg_defaults()

    def seed_param_ref_defaults(self, param_ref_defaults: dict[str, str]) -> None:
        self._scope.set_param_ref_defaults(param_ref_defaults)

    def module_ctx(self, module_id: str, default_arguments: dict[str, ModuleArg] | None = None, param_ref_defaults: dict[str, str] | None = None, arg_defaults: dict[str, str] | None = None) -> EvalContext:
        # Enters a module instance scope; wires the current scope as the new state's parent.
        ms = self._scope.module_child(module_id, self._repeat_idx, default_arguments, param_ref_defaults=param_ref_defaults, arg_defaults=arg_defaults)
        return EvalContext(ms)
