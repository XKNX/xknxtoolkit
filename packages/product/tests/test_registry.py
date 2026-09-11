"""Unit tests for Registry's ergonomic resolver methods. Registry itself is a plain
dict-of-dicts index - these methods never touch the stored objects' internals, only
look them up by id, so cheap opaque placeholders (cast to the expected type) stand in
for real Hardware/Product/DeviceProgram/Application/CatalogItem/CatalogSection values."""

from __future__ import annotations

from typing import cast

from xknxmono.product.application import Application
from xknxmono.product.catalog import CatalogItem, CatalogSection
from xknxmono.product.hardware import DeviceProgram, Hardware, Product
from xknxmono.product.master import MasterData
from xknxmono.product.registry import Registry


def _registry() -> Registry:
    return Registry(master=MasterData(raw=None))


def test_update_master_replaces_master() -> None:
    reg = _registry()
    new_master = MasterData(raw=None)
    reg.update_master(new_master)
    assert reg.master is new_master


def test_hardware_for_manufacturer() -> None:
    reg = _registry()
    hw = cast(Hardware, "hw-1")
    reg.hardware = {"H1": hw}
    reg.manufacturer_to_hardware = {"M-1": ["H1"]}
    assert reg.hardware_for_manufacturer("M-1") == {"H1": hw}
    assert reg.hardware_for_manufacturer("M-unknown") == {}


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


def test_applications_for_program() -> None:
    reg = _registry()
    app = cast(Application, "app-1")
    reg.applications = {"A1": app}
    reg.program_to_application = {"PR1": ["A1"]}
    assert reg.applications_for_program("PR1") == {"A1": app}
    assert reg.applications_for_program("PR-unknown") == {}


def test_applications_for_program_skips_dangling_ids() -> None:
    reg = _registry()
    reg.applications = {}  # "A1" never actually registered
    reg.program_to_application = {"PR1": ["A1"]}
    assert reg.applications_for_program("PR1") == {}


def test_applications_for_hardware_aggregates_across_programs() -> None:
    reg = _registry()
    app1 = cast(Application, "app-1")
    app2 = cast(Application, "app-2")
    reg.applications = {"A1": app1, "A2": app2}
    reg.hardware_to_program = {"H1": ["PR1", "PR2"]}
    reg.program_to_application = {"PR1": ["A1"], "PR2": ["A2"]}
    assert reg.applications_for_hardware("H1") == {"A1": app1, "A2": app2}
    assert reg.applications_for_hardware("H-unknown") == {}


def test_product_for_item() -> None:
    reg = _registry()
    product = cast(Product, "product-1")
    reg.products = {"P1": product}
    item = CatalogItem(
        id="I1",
        name=None,
        number=None,
        product_ref_id="P1",
        hardware2_program_ref_id=None,
    )
    assert reg.product_for_item(item) is product


def test_product_for_item_none_ref_id() -> None:
    reg = _registry()
    item = CatalogItem(
        id="I1",
        name=None,
        number=None,
        product_ref_id=None,
        hardware2_program_ref_id=None,
    )
    assert reg.product_for_item(item) is None


def test_program_for_item() -> None:
    reg = _registry()
    program = cast(DeviceProgram, "program-1")
    reg.programs = {"PR1": program}
    item = CatalogItem(
        id="I1",
        name=None,
        number=None,
        product_ref_id=None,
        hardware2_program_ref_id="PR1",
    )
    assert reg.program_for_item(item) is program


def test_program_for_item_none_ref_id() -> None:
    reg = _registry()
    item = CatalogItem(
        id="I1",
        name=None,
        number=None,
        product_ref_id=None,
        hardware2_program_ref_id=None,
    )
    assert reg.program_for_item(item) is None


def test_sections_for_manufacturer() -> None:
    reg = _registry()
    section = CatalogSection(id="S1", name="Switching", number="1", parent_id=None)
    reg.catalog_sections = {"S1": section}
    reg.manufacturer_to_section = {"M-1": ["S1"]}
    assert reg.sections_for_manufacturer("M-1") == {"S1": section}
    assert reg.sections_for_manufacturer("M-unknown") == {}


def test_subsections() -> None:
    reg = _registry()
    sub = CatalogSection(id="S2", name="Sub", number="1.1", parent_id="S1")
    reg.catalog_sections = {"S2": sub}
    reg.section_to_subsection = {"S1": ["S2"]}
    assert reg.subsections("S1") == {"S2": sub}
    assert reg.subsections("S-unknown") == {}


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
