from __future__ import annotations

from typing import TYPE_CHECKING

from xknxmono.models.intermediate import ModuleArg
from xknxmono.models.intermediate.com_object_instance_ref_t import ComObjectInstanceRef

if TYPE_CHECKING:
    from .application_indexer import ApplicationIndexer
    from .state import ParameterState


class EvalContext:
    """Scope handle: the active state node plus a pending repeat index for the next module_child call.

    Reads delegate to the active state, which walks its parent chain (submodule → module → global).
    Writes go to the active state only.
    """

    __slots__ = ("_idx", "_repeat_idx", "_scope")

    def __init__(
        self,
        scope: ParameterState,
        repeat_idx: int = 1,
        *,
        idx: ApplicationIndexer,
    ) -> None:
        self._scope = scope
        self._repeat_idx = repeat_idx
        self._idx = idx

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

    def get_param_ref_text(self, ref_id: str) -> str | None:
        """The Text of the Parameter/UnionParameter `ref_id` (a ParameterRef id) points to.

        Some manufacturers give a ParameterBlock/Channel a ParamRefId pointing at a
        label-only Parameter (typically a "Page" type) instead of setting Text/Name
        directly on the block itself - confirmed against a real product's dynamic
        XML, where every ParameterBlock relies on this instead of its own Text.
        """
        param_ref = self._idx.parameter_refs.get(ref_id)
        if param_ref is None:
            return None
        parameter = self._idx.parameters.get(param_ref.ref_id)
        return parameter.text if parameter is not None else None

    def mark_active_param(self, ref_id: str) -> None:
        parameter_id = self._idx.parameter_refs[ref_id].ref_id
        self._scope.mark_active_param(ref_id, parameter_id)

    def mark_active_com_object(self, ref_id: str) -> None:
        self._scope.mark_active_com_object(ref_id)

    def get_com_obj_instance_ref(self, ref_id: str) -> ComObjectInstanceRef | None:
        return self._scope.get_com_obj_instance_ref(ref_id)

    def allocate(
        self, def_ref_id: str, alloc_id: str, arg_ref_id: str, base: int = 0
    ) -> int:
        """Allocate an address from the running pool, advance the scope position, and return the address."""
        alloc = self._idx.allocators[def_ref_id][alloc_id]
        arg_alloc_entry = self._idx.arg_alloc[def_ref_id][arg_ref_id]
        allocates, alignment = arg_alloc_entry
        position = self._scope.alloc_position(alloc_id, alloc.start)
        address, next_position = alloc.resolve(position, allocates, alignment, base)
        self._scope.set_alloc_position(alloc_id, next_position)
        return address

    @property
    def repeat_idx(self) -> int:
        return self._repeat_idx

    def repeat_ctx(self, repeat_idx: int) -> EvalContext:
        return EvalContext(self._scope, repeat_idx, idx=self._idx)

    def get_arg_value(self, ref_id: str) -> int:
        arg = self._scope.get_arg(ref_id)
        return arg.value if arg is not None and arg.value is not None else 0

    def get_arg_defaults(self) -> dict[str, str]:
        return self._scope.get_arg_defaults()

    def seed_param_ref_defaults(self, param_ref_defaults: dict[str, str]) -> None:
        self._scope.set_param_ref_defaults(param_ref_defaults)

    def module_ctx(
        self,
        module_id: str,
        default_arguments: dict[str, ModuleArg] | None = None,
        param_ref_defaults: dict[str, str] | None = None,
        arg_defaults: dict[str, str] | None = None,
        ref_id: str | None = None,
    ) -> EvalContext:
        ms = self._scope.module_child(
            module_id,
            self._repeat_idx,
            default_arguments,
            param_ref_defaults=param_ref_defaults,
            arg_defaults=arg_defaults,
            ref_id=ref_id,
        )
        return EvalContext(ms, idx=self._idx)
