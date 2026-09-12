"""Unit test for xknxmono.product's PEP 562 lazy __getattr__: an unknown attribute name
must raise AttributeError rather than silently returning None."""

import pytest

import xknxmono.product


def test_unknown_attribute_raises() -> None:
    with pytest.raises(AttributeError, match="has no attribute 'NoSuchThing'"):
        getattr(xknxmono.product, "NoSuchThing")  # noqa: B009
