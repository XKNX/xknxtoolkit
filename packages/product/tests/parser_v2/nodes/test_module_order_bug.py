"""Regression tests for the order-dependence defect in ``_resolve_arguments``.

Before the fix, ``_resolve_arguments`` performed a single forward pass over
``arguments.items()`` in iteration order and read each arg's ``base_value``
target from the in-progress ``out`` dict, so a dependent arg listed *before* its
``base_value`` target read the target's *unresolved* state and computed a wrong
base (it dropped the base for an allocator-only target whose pre-resolution
``value`` is ``None``, or used the *stale pre-allocation literal* when the
target also carried a co-occurring ``Value=`` alongside ``AllocatorRefId=``).

These tests pin down the resolver's behaviour as **order-independent** and the
new contract that cyclic / unsatisfiable ``base_value`` graphs raise
``ValueError`` instead of silently producing a wrong value.

``_indexer_with_allocator`` (shared with ``test_module.py``) builds an
``ApplicationIndexer`` whose single ``ModuleDef`` (def_id) has one
``Allocator`` (alloc_id, ``start=100, max_inclusive=199``) and a sequence of
args each ``allocates=1, alignment=1``.
"""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import ModuleArg
from xknxmono.models.intermediate.module_t_numeric_arg import ModuleNumericArg
from xknxmono.product.parser_v2.nodes import EvalContext, GlobalState
from xknxmono.product.parser_v2.nodes.module import (
    _resolve_arguments,  # pyright: ignore[reportPrivateUsage]
)

from .test_module import (
    _indexer_with_allocator,  # pyright: ignore[reportPrivateUsage]
)


def _numeric(args: dict[str, ModuleArg], ref_id: str) -> ModuleNumericArg:
    """Narrow the resolved-arg lookup to ``ModuleNumericArg`` for tests.

    Returns the resolved arg for ``ref_id`` (asserts type); tests then read
    ``.value`` without per-assertion pyright ignores.
    """
    arg = args[ref_id]
    assert isinstance(arg, ModuleNumericArg)
    return arg


def test_base_value_to_allocator_backed_arg_reverse_order() -> None:
    """A-2 (dependent) listed BEFORE its allocator-backed base A-1.

    Pre-fix, A-2 read A-1's pre-resolution ``value=None`` as base 0 and resolved
    to its literal 10 (= ``10 + 0``). After the fixpoint fix, A-1 is allocated
    first and A-2 reads its final value 100 to resolve to 110.
    """
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1", "A-2"])
    ctx = EvalContext(GlobalState(), idx=idx)
    # Reverse dependency order; runtime dict preserves insertion order.
    args: dict[str, ModuleArg] = {
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
        "A-1": ModuleNumericArg(ref_id="A-1", allocator_ref_id="L-1"),
    }
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert _numeric(resolved, "A-1").value == 100
    assert _numeric(resolved, "A-2").value == 110  # was 10 pre-fix


def test_base_value_to_allocator_backed_arg_reverse_order_carrying_literal() -> None:
    """A-1 also carries a stale ``Value=7`` alongside ``AllocatorRefId=L-1``.

    ``allocate()`` discards that literal, so A-1's final value is 100, not 7.
    Pre-fix, A-2 saw A-1's *stale pre-allocation literal* 7 and resolved to
    17 (= ``10 + 7``). After the fixpoint fix, A-2 defers until A-1 is
    allocated, then resolves to 110 (= ``10 + 100``).
    """
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1", "A-2"])
    ctx = EvalContext(GlobalState(), idx=idx)
    args: dict[str, ModuleArg] = {
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
        "A-1": ModuleNumericArg(ref_id="A-1", value=7, allocator_ref_id="L-1"),
    }
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert _numeric(resolved, "A-1").value == 100  # literal 7 discarded by allocate()
    assert _numeric(resolved, "A-2").value == 110  # was 17 pre-fix


def test_reverse_order_matches_forward_order_for_allocator_base_pair() -> None:
    """The forward- and reverse-order resolutions of the same logical args must
    produce identical output dicts — the order-independence contract."""
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1", "A-2"])
    fwd_args: dict[str, ModuleArg] = {
        "A-1": ModuleNumericArg(ref_id="A-1", allocator_ref_id="L-1"),
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
    }
    rev_args: dict[str, ModuleArg] = {
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
        "A-1": ModuleNumericArg(ref_id="A-1", allocator_ref_id="L-1"),
    }
    fwd = _resolve_arguments(EvalContext(GlobalState(), idx=idx), "MD1", fwd_args)
    rev = _resolve_arguments(EvalContext(GlobalState(), idx=idx), "MD1", rev_args)
    assert {k: _numeric(fwd, k).value for k in fwd} == {
        k: _numeric(rev, k).value for k in rev
    }


def test_allocator_backed_arg_is_allocated_exactly_once_even_if_deferred() -> None:
    """When an allocator-backed arg's ``base_value`` forces deferral, the arg
    must still allocate exactly once (the pool position advances by 1, not by
    N passes). Otherwise the deferred arg would silently consume more pool
    slots than its sibling allocator-backed args — a footgun specific to the
    fixpoint approach.

    A-1 and A-3 share pool L-1 (start=100); A-1 takes slot 100, A-3 takes the
    next slot 101 with base = A-1's final value 100 -> 201. If A-1 were
    re-allocated by the fixpoint loop, A-3 would land above 101.
    """
    idx = _indexer_with_allocator("MD1", "L-1", ["A-1", "A-3"])
    ctx = EvalContext(GlobalState(), idx=idx)
    args: dict[str, ModuleArg] = {
        "A-3": ModuleNumericArg(ref_id="A-3", allocator_ref_id="L-1", base_value="A-1"),
        "A-1": ModuleNumericArg(ref_id="A-1", allocator_ref_id="L-1", value=0),
    }
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert _numeric(resolved, "A-1").value == 100  # literal 0 discarded
    assert _numeric(resolved, "A-3").value == 201  # pool_pos 101 + base 100


def test_base_value_chain_of_three_in_reverse_dependency_order() -> None:
    """A four-arg chain A-4 -> A-3 -> A-2 -> A-1, iterated in *reverse dependency*
    order (A-4 first, A-1 last), requires three deferral-then-resolve passes —
    guards against the fixpoint loop regressing to a bounded-<N single pass.
    """
    ctx = EvalContext(GlobalState(), idx=_indexer_with_allocator("MD1", "L-1", []))
    args: dict[str, ModuleArg] = {
        "A-4": ModuleNumericArg(ref_id="A-4", value=30, base_value="A-3"),
        "A-3": ModuleNumericArg(ref_id="A-3", value=20, base_value="A-2"),
        "A-2": ModuleNumericArg(ref_id="A-2", value=10, base_value="A-1"),
        "A-1": ModuleNumericArg(ref_id="A-1", value=5),
    }
    resolved = _resolve_arguments(ctx, "MD1", args)
    assert _numeric(resolved, "A-1").value == 5  # plain literal, untouched
    assert _numeric(resolved, "A-2").value == 15  # 10 + 5
    assert _numeric(resolved, "A-3").value == 35  # 20 + 15
    assert _numeric(resolved, "A-4").value == 65  # 30 + 35


def test_self_cycle_raises() -> None:
    """A cyclic ``base_value`` graph (here, an arg pointing at itself) cannot
    converge and must raise rather than silently produce a wrong value."""
    ctx = EvalContext(GlobalState(), idx=_indexer_with_allocator("MD1", "L-1", ["A-1"]))
    args: dict[str, ModuleArg] = {
        "A-1": ModuleNumericArg(ref_id="A-1", value=10, base_value="A-1"),
    }
    with pytest.raises(ValueError, match="cyclic or unsatisfiable BaseValue"):
        _resolve_arguments(ctx, "MD1", args)


def test_dangling_base_value_raises() -> None:
    """A ``base_value`` referencing an absent arg (e.g. a typo in the RefId)
    is unsatisfiable and must raise rather than silently drop the base."""
    ctx = EvalContext(GlobalState(), idx=_indexer_with_allocator("MD1", "L-1", []))
    args: dict[str, ModuleArg] = {
        "A-1": ModuleNumericArg(ref_id="A-1", value=10, base_value="A-x"),
    }
    with pytest.raises(ValueError, match="cyclic or unsatisfiable BaseValue"):
        _resolve_arguments(ctx, "MD1", args)
