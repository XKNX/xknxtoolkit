"""Regression guard for the ``limit``/``offset`` input-validation cap on ``HardwareFilters``.

``HardwareFilters`` is the live FastAPI query model (``Annotated[HardwareFilters, Query()]``),
so a ``Field(le=...)`` on it is an HTTP-layer cap: out-of-range values are rejected at the
Pydantic boundary (HTTP 422) before reaching SQLAlchemy. These tests pin that cap so it
cannot silently regress to the uncapped form that let ``?limit=-1`` mean "no limit" on SQLite.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from xknxmono.catalog.core.hardware import HardwareFilters


def test_defaults_match_documented_values() -> None:
    assert HardwareFilters().limit == 50
    assert HardwareFilters().offset == 0


def test_limit_accepts_zero_and_cap() -> None:
    assert HardwareFilters(limit=0).limit == 0
    assert HardwareFilters(limit=200).limit == 200


def test_limit_rejects_negative() -> None:
    """``limit=-1`` is the demonstrated exploit (SQLite ``LIMIT -1`` = unlimited)."""
    with pytest.raises(ValidationError):
        HardwareFilters(limit=-1)


def test_limit_rejects_above_cap() -> None:
    with pytest.raises(ValidationError):
        HardwareFilters(limit=201)


def test_offset_rejects_negative() -> None:
    with pytest.raises(ValidationError):
        HardwareFilters(offset=-1)


def test_other_filters_remain_unaffected() -> None:
    """Bounding ``limit``/``offset`` must not perturb the other filter fields."""
    f = HardwareFilters(
        manufacturer_id=["M-0001", "M-0002"], medium_type=["TP"], is_rail_mounted=True
    )
    assert f.manufacturer_id == ["M-0001", "M-0002"]
    assert f.medium_type == ["TP"]
    assert f.is_rail_mounted is True
