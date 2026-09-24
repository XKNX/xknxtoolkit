"""Unit tests for Registry's ergonomic resolver methods. Registry itself is a plain
dict-of-dicts index - these methods never touch the stored objects' internals, only
look them up by id, so cheap opaque placeholders (cast to the expected type) stand in
for real Product/DeviceProgram/CatalogItem values."""

from __future__ import annotations

from typing import cast

from xknxmono.product.catalog import CatalogItem
from xknxmono.product.hardware import DeviceProgram, Product
from xknxmono.product.master import MasterData
from xknxmono.product.registry import Registry


def _registry() -> Registry:
    return Registry(master=MasterData(raw=None))


def test_products_for_hardware() -> None:
    reg = _registry()
    product = cast(Product, "product-1")
    reg.products = {"P1": product}
    reg.hardware_to_product = {"H1": ["P1"]}
    assert reg.products_for_hardware("H1") == {"P1": product}
    assert reg.products_for_hardware("H-unknown") == {}


def test_programs_for_hardware() -> None:
    reg = _registry()
    program = cast(DeviceProgram, "program-1")
    reg.programs = {"PR1": program}
    reg.hardware_to_program = {"H1": ["PR1"]}
    assert reg.programs_for_hardware("H1") == {"PR1": program}
    assert reg.programs_for_hardware("H-unknown") == {}


def test_items_for_section() -> None:
    reg = _registry()
    item = CatalogItem(
        id="I1",
        name=None,
        number=None,
        product_ref_id=None,
        hardware2_program_ref_id=None,
    )
    reg.catalog_items = {"I1": item}
    reg.section_to_item = {"S1": ["I1"]}
    assert reg.items_for_section("S1") == {"I1": item}
    assert reg.items_for_section("S-unknown") == {}
