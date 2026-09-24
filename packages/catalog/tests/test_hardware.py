"""Tests for ``get_hardware_by_program`` — the project Configure panel's hardware source.

The Configure panel resolves the catalog ``Hardware`` row from a device's
``hardware2program_ref_id`` and renders ``order_number`` / ``width_mm`` /
``is_rail_mounted`` unconditionally from it. The pre-fix ``get_hardware_by_program``
returned the hardware row's first-SKU display fields for *every* SKU the operator
could have added — so adding a device from a non-first catalog item rendered the
wrong order number / width. The fix keeps the same surface (``HardwareInfo``) but
accepts the device's ``product_ref_id`` so per-SKU fields can be sourced from the
matching ``hardware_products`` row.
"""

from __future__ import annotations

from pathlib import Path

from conftest import (  # type: ignore[import-not-found]
    ProductSpec,
    build_knxprod_bytes,
)
from sqlalchemy.orm import Session

from xknxmono.catalog.core.hardware import HardwareInfo, get_hardware_by_program
from xknxmono.catalog.core.upload import upload_knxprod

ALPHA = ProductSpec(
    id="M-0008_H-1_P-1",
    name="SKU Alpha",
    order_number="ORD-ALPHA",
    is_rail_mounted=True,
    width_mm=36.0,
    visible_description="Alpha variant",
    default_language="en-US",
)
BETA = ProductSpec(
    id="M-0008_H-1_P-2",
    name="SKU Beta",
    order_number="ORD-BETA",
    is_rail_mounted=True,
    width_mm=72.0,
    visible_description="Beta variant",
    default_language="de-DE",
)

_PROGRAM = "M-0008_H-1_HP-1"
_HARDWARE = "M-0008_H-1"


def _ingest(content: bytes, engine: object, knxprod_dir: Path) -> None:
    upload_knxprod(content, knxprod_dir, engine)  # pyright: ignore[reportArgumentType]


def _without_sku(engine: object, program_ref: str) -> HardwareInfo | None:
    with Session(engine) as db:  # pyright: ignore[reportArgumentType]
        return get_hardware_by_program(db, program_ref)


def _with_sku(
    engine: object, program_ref: str, product_ref_id: str | None
) -> HardwareInfo | None:
    with Session(engine) as db:  # pyright: ignore[reportArgumentType]
        return get_hardware_by_program(db, program_ref, product_ref_id)


def test_without_product_ref_id_returns_hardware_row_display_fields(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """Backwards compatibility: callers that don't supply a ``product_ref_id`` (e.g. the HTTP
    API rendering a hardware by program alone) get the same Hardware-row fields as before."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA, BETA]),
        catalog_engine,
        knxprod_dir,
    )

    info = _without_sku(catalog_engine, _PROGRAM)
    assert info is not None
    assert info.id == _HARDWARE
    # First-SKU (products[0]) display fields, as before the fix.
    assert info.name == "SKU Alpha"
    assert info.order_number == "ORD-ALPHA"
    assert info.is_rail_mounted is True
    assert info.width_mm == 36.0


def test_with_nonfirst_product_ref_id_returns_that_skus_display_fields(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The regression: passing the device's product_ref_id for the non-first SKU returns
    that SKU's order_number / width_mm / is_rail_mounted / name (the operator's selected
    SKU), not the Hardware row's first-SKU defaults."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA, BETA]),
        catalog_engine,
        knxprod_dir,
    )

    info = _with_sku(catalog_engine, _PROGRAM, BETA.id)
    assert info is not None
    assert (
        info.id == _HARDWARE
    )  # Same hardware — only the per-SKU display fields change.
    assert info.order_number == "ORD-BETA"
    assert info.width_mm == 72.0
    assert info.is_rail_mounted is True
    assert info.name == "SKU Beta"


def test_with_first_product_ref_id_matches_hardware_row(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """A ``product_ref_id`` pointing at the first SKU returns identical fields to the no-arg
    call — both consumers see the first-SKU values, no regression either way."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA, BETA]),
        catalog_engine,
        knxprod_dir,
    )

    with_sku = _with_sku(catalog_engine, _PROGRAM, ALPHA.id)
    without_sku = _without_sku(catalog_engine, _PROGRAM)
    assert with_sku is not None
    assert without_sku is not None
    assert with_sku == without_sku


def test_with_unknown_product_ref_id_falls_back_to_hardware_row(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """A ``product_ref_id`` with no matching SKU row falls back to the Hardware row's display
    fields (the no-arg behaviour) — defensive for older databases without per-SKU rows."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA]),
        catalog_engine,
        knxprod_dir,
    )

    info = _with_sku(catalog_engine, _PROGRAM, "M-0008_H-1_P-DOES-NOT-EXIST")
    assert info is not None
    assert info.order_number == "ORD-ALPHA"
    assert info.width_mm == 36.0


def test_unknown_program_ref_returns_none(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    _ingest(
        build_knxprod_bytes(products=[ALPHA]),
        catalog_engine,
        knxprod_dir,
    )
    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        assert (
            get_hardware_by_program(db, "M-0008_H-1_HP-DOES-NOT-EXIST", ALPHA.id)
            is None
        )


def test_hardware_level_fields_come_from_hardware_row_regardless_of_sku(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """Hardware-level fields (coupler/power-supply/IP flags, serial number, version number)
    are NOT per-SKU, so they come from the Hardware row even when a ``product_ref_id`` is
    given. This guards against the inverse mistake of pulling everything from the SKU row."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA, BETA]),
        catalog_engine,
        knxprod_dir,
    )

    info_beta = _with_sku(catalog_engine, _PROGRAM, BETA.id)
    info_alpha = _with_sku(catalog_engine, _PROGRAM, ALPHA.id)
    assert info_alpha is not None
    assert info_beta is not None
    # Hardware-level fields are equal for both SKUs of the same hardware:
    assert info_beta.serial_number == info_alpha.serial_number
    assert info_beta.version_number == info_alpha.version_number
    assert info_beta.is_coupler == info_alpha.is_coupler
    assert info_beta.is_power_supply == info_alpha.is_power_supply
    assert info_beta.is_ip_enabled == info_alpha.is_ip_enabled


def test_single_sku_hardware_get_with_product_ref_id_returns_hardware_values(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """For the common 1-SKU case (the only one in any in-repo fixture), passing the
    single SKU's id returns the hardware row's values — no regression to 1-SKU devices."""
    _ingest(
        build_knxprod_bytes(products=[ALPHA]),
        catalog_engine,
        knxprod_dir,
    )

    info = _with_sku(catalog_engine, _PROGRAM, ALPHA.id)
    assert info is not None
    assert info.order_number == "ORD-ALPHA"
    assert info.width_mm == 36.0
    assert info.is_rail_mounted is True
    assert info.name == "SKU Alpha"
