"""Tests for ``list_products`` — the product-centric browse view's SKU resolution.

The pre-fix ``list_products`` joined ``Hardware.order_number`` to the catalog item
without reconciling it against ``CatalogSectionProduct.product_ref_id``, so a row
whose ``product_ref_id`` pointed at a non-first SKU returned that SKU's id paired
with the *first* SKU's order number. After the fix the order number comes from the
SKU the catalog item references, via the new ``hardware_products`` table.
"""

from __future__ import annotations

from pathlib import Path

from conftest import (  # type: ignore[import-not-found]
    CatalogItemSpec,
    ProductSpec,
    build_knxprod_bytes,
)
from sqlalchemy.orm import Session

from xknxmono.catalog.core.products import ProductSummary, list_products
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
GAMMA = ProductSpec(
    id="M-0008_H-2_P-3",
    name="SKU Gamma",
    order_number="ORD-GAMMA",
    is_rail_mounted=False,
    width_mm=12.0,
)


def _ingest(content: bytes, engine: object, knxprod_dir: Path) -> None:
    upload_knxprod(content, knxprod_dir, engine)  # pyright: ignore[reportArgumentType]


def _products(db: Session) -> dict[str, ProductSummary]:
    return {p.product_ref_id: p for p in list_products(db)}


def test_catalog_item_referencing_nonfirst_sku_returns_that_skus_order_number(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The regression: CI referencing P-2 inherits P-2's order number, not P-1's."""
    content = build_knxprod_bytes(
        products=[ALPHA, BETA],
        catalog_items=[
            CatalogItemSpec(
                id="M-0008_CI-1",
                name="Dual-SKU Device (Beta)",
                number=1,
                product_ref_id=BETA.id,
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            )
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        rows = _products(db)
        assert set(rows) == {BETA.id}
        beta = rows[BETA.id]
        assert beta.product_ref_id == BETA.id
        assert beta.hardware2program_ref_id == "M-0008_H-1_HP-1"
        # Before the fix this was "ORD-ALPHA" (products[0]) — mixing two SKUs.
        assert beta.order_number == "ORD-BETA"


def test_catalog_item_referencing_first_sku_returns_first_skus_order_number(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """A catalog item referencing the first SKU is unaffected by the bug — confirm no
    regression. ``order_number`` is the same whether sourced from the SKU or the Hardware row."""
    content = build_knxprod_bytes(
        products=[ALPHA, BETA],
        catalog_items=[
            CatalogItemSpec(
                id="M-0008_CI-1",
                name="Dual-SKU Device (Alpha)",
                number=1,
                product_ref_id=ALPHA.id,
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            )
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        rows = _products(db)
        alpha = rows[ALPHA.id]
        assert alpha.order_number == "ORD-ALPHA"


def test_two_catalog_items_referencing_different_skus_of_same_hardware(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """Two catalog items pointing at two SKUs of the same hardware return distinct order
    numbers even though they share the same hardware_program_id."""
    content = build_knxprod_bytes(
        products=[ALPHA, BETA],
        catalog_items=[
            CatalogItemSpec(
                id="M-0008_CI-1",
                name="Alpha pack",
                number=1,
                product_ref_id=ALPHA.id,
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            ),
            CatalogItemSpec(
                id="M-0008_CI-2",
                name="Beta pack",
                number=2,
                product_ref_id=BETA.id,
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            ),
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        rows = _products(db)
        assert rows[ALPHA.id].order_number == "ORD-ALPHA"
        assert rows[BETA.id].order_number == "ORD-BETA"
        # Same program reference for both — only the SKU differentiates them.
        assert rows[ALPHA.id].hardware2program_ref_id == "M-0008_H-1_HP-1"
        assert rows[BETA.id].hardware2program_ref_id == "M-0008_H-1_HP-1"


def test_single_sku_hardware_catalog_item_returns_that_skus_order_number(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The common (and the only in-repo fixture) case: a 1-SKU hardware. ``order_number``
    sourced from the SKU matches the Hardware row's pre-fix value — no regression."""
    content = build_knxprod_bytes(
        products=[GAMMA],
        catalog_items=[
            CatalogItemSpec(
                id="M-0008_CI-1",
                name="Gamma device",
                number=1,
                product_ref_id=GAMMA.id,
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            )
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        rows = _products(db)
        assert rows[GAMMA.id].order_number == "ORD-GAMMA"


def test_catalog_items_without_hardware2program_ref_are_not_persisted_to_section_products(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """A catalog item with no ``Hardware2ProgramRefId`` is not a product/SKU at all —
    ``_ingest_catalog`` skips persisting a ``CatalogSectionProduct`` row for it. With no
    row to join, ``list_products`` returns nothing — preserves the prior gate."""
    content = build_knxprod_bytes(
        products=[ALPHA],
        catalog_items=[
            # A "section-only" catalog item (no program ref): _ingest_catalog won't persist a
            # CatalogSectionProduct row for it at all.
            CatalogItemSpec(
                id="M-0008_CI-SECTION-ONLY",
                name="Section-only entry",
                number=1,
                product_ref_id=ALPHA.id,
                hardware2_program_ref_id=None,
            )
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        assert _products(db) == {}


def test_unresolvable_sku_falls_back_to_hardware_order_number(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """Defensively: when a catalog item's product_ref_id has no row in hardware_products
    (e.g. an older DB migrated without re-ingesting), the outer join leaves the SKU's
    order_number NULL and the query falls back to the Hardware row's value — same
    behaviour as the pre-fix code, so this code path never regresses."""
    content = build_knxprod_bytes(
        products=[ALPHA],
        catalog_items=[
            CatalogItemSpec(
                id="M-0008_CI-1",
                name="Unknown SKU reference",
                number=1,
                # References a SKU that isn't attached to any ingested hardware.
                product_ref_id="M-0008_H-1_P-DOES-NOT-EXIST",
                hardware2_program_ref_id="M-0008_H-1_HP-1",
            )
        ],
    )
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        rows = _products(db)
        # Falls back to the hardware row's first-SKU order number rather than dropping the row.
        only = rows["M-0008_H-1_P-DOES-NOT-EXIST"]
        assert only.order_number == "ORD-ALPHA"
