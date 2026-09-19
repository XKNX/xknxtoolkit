from __future__ import annotations

from xknxmono.models.intermediate import ModuleArg
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg

from ..context import EvalContext
from ..ui import UiNode
from .base import DynamicNode


def _resolved_base(ref_id: str, args: dict[str, ModuleArg]) -> int:
    """Final, already-resolved integer value of ``ref_id`` in ``args``, else 0.

    Returns 0 if the ref is absent, is not a :class:`ModuleNumericArg`, or carries
    a ``None`` value. ``_resolve_arguments`` only calls this once a target's
    value has been determined *final* (post-allocation / post-base-add), so it
    can never observe a pre-resolution stale literal here.
    """
    ref = args.get(ref_id)
    return (
        ref.value if isinstance(ref, ModuleNumericArg) and ref.value is not None else 0
    )


def _resolve_arguments(
    ctx: EvalContext, ref_id: str, arguments: dict[str, ModuleArg]
) -> dict[str, ModuleArg]:
    """Resolve a module instance's :class:`ModuleNumericArg` arguments to concrete ints.

    Semantics, per :class:`ModuleNumericArg`'s independent optional attributes:

    * allocator-backed args (``AllocatorRefId=``) get their ``value`` from
      :meth:`EvalContext.allocate`; any co-occurring ``Value=`` literal is
      discarded.
    * base-value-only args (``BaseValue=`` but no ``AllocatorRefId=``) become
      ``(arg.value or 0) + resolved_base``.
    * plain-literal args (``Value=`` only) are already final and untouched.

    Resolution is **order-independent**: a ``base_value`` may reference an arg
    that is iterated *after* its referencer (XML document order of the instance
    ``<NumericArg>`` children). We converge to a fixpoint, deferring an arg
    until its ``base_value`` target's value is final. Allocating twice would
    advance the pool position, so each arg is allocated exactly once: the
    ``out[r_id] is not arg`` identity check distinguishes "already resolved by
    us" from "still the unresolved input literal".

    Cyclic or unsatisfiable ``base_value`` graphs (self-cycle, 2-/N-cycle,
    dangling reference) cannot converge and surface as a :class:`ValueError`
    rather than a silently-wrong value. A finite ``len(pending) + 1`` bound on
    passes guards against pathological inputs, and the ``not changed and
    deferred`` check raises on the first stalled pass (rather than spinning to
    the bound).
    """
    out = dict(arguments)
    # Only allocator-backed and base-value args need active resolution; plain
    # literals are already final. This bounds fixpoint passes by the number of
    # resolvable args (a chain of N may take up to N passes + 1 quiescence).
    pending: list[tuple[str, ModuleNumericArg]] = [
        (r_id, arg)
        for r_id, arg in arguments.items()
        if isinstance(arg, ModuleNumericArg)
        and (arg.allocator_ref_id is not None or arg.base_value is not None)
    ]

    def _base_if_final(base_id: str) -> int | None:
        """Resolved value of ``base_id`` if final, else ``None`` to defer.

        A target's ``.value`` is only trustworthy for use as a base once any
        allocator- or base-backed resolution has run on it; before that, the
        value may be a stale input ``Value=`` literal that ``allocate()`` would
        discard on the target itself. Plain literals and already-replaced args
        are final from the start / from the pass that replaced them.
        """
        target = out.get(base_id)
        if not isinstance(target, ModuleNumericArg):
            return None
        original = arguments.get(base_id)
        if (
            isinstance(original, ModuleNumericArg)
            and (
                original.allocator_ref_id is not None or original.base_value is not None
            )
            and target is original
        ):
            return None  # target's value not yet final; defer
        return _resolved_base(base_id, out)

    max_passes = len(pending) + 1
    for _ in range(max_passes):
        changed = False
        deferred = False
        for r_id, arg in pending:
            if out[r_id] is not arg:
                continue  # already resolved by us in an earlier pass
            if arg.base_value is not None:
                base = _base_if_final(arg.base_value)
                if base is None:
                    deferred = True
                    continue
            else:
                base = 0
            if arg.allocator_ref_id is not None:
                out[r_id] = ModuleNumericArg(
                    ref_id=r_id,
                    value=ctx.allocate(ref_id, arg.allocator_ref_id, r_id, base),
                )
            else:
                out[r_id] = ModuleNumericArg(ref_id=r_id, value=(arg.value or 0) + base)
            changed = True
        if not changed:
            if deferred:
                raise ValueError(
                    f"cyclic or unsatisfiable BaseValue dependency graph "
                    f"for module {ref_id!r}"
                )
            return out
    raise ValueError(
        f"cyclic or unsatisfiable BaseValue dependency graph for module {ref_id!r}"
    )


class ModuleNode(DynamicNode):
    """Container: inlines a module definition's subtree under its own instance scope."""

    def __init__(
        self,
        module_id: str,
        subtree: DynamicNode,
        ref_id: str,
        arguments: dict[str, ModuleArg] | None = None,
        param_ref_defaults: dict[str, str] | None = None,
        arg_defaults: dict[str, str] | None = None,
    ) -> None:
        self._module_id = module_id
        self._ref_id = ref_id
        self._subtree = subtree
        self._arguments: dict[str, ModuleArg] = arguments or {}
        self._param_ref_defaults: dict[str, str] = param_ref_defaults or {}
        self._arg_defaults: dict[str, str] = arg_defaults or {}

    def eval(self, ctx: EvalContext) -> list[UiNode]:
        args = _resolve_arguments(ctx, self._ref_id, self._arguments)
        mctx = ctx.module_ctx(
            self._module_id,
            args,
            param_ref_defaults=self._param_ref_defaults or None,
            arg_defaults=self._arg_defaults or None,
            ref_id=self._ref_id,
        )
        return self._subtree.eval(mctx)
