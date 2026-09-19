"""Tests for ``upload_knxprod`` / ``_ingest_hardware``.

These tests were the first in ``packages/catalog``; they exercise the ingestion seam
where the catalog DB meets a multi-SKU ``<Hardware>`` — the seam that previously
collapsed to ``products[0]`` and silently dropped every other SKU's payload.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from conftest import (  # type: ignore[import-not-found]
    CatalogItemSpec,
    ProductSpec,
    build_knxprod_bytes,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from xknxmono.catalog.core.upload import upload_knxprod
from xknxmono.catalog.models import Hardware, HardwareProduct

# Two SKUs of one hardware, with every per-<Product> field varied to make the
# surfaces that read each one observable.
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


def _ingest(
    content: bytes,
    engine: object,
    knxprod_dir: Path,
) -> None:
    """Run upload_knxprod against a fresh engine, surfacing warnings via caplog."""
    upload_knxprod(content, knxprod_dir, engine)  # pyright: ignore[reportArgumentType]


def test_single_sku_hardware_ingests_one_hardware_product_row(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    content = build_knxprod_bytes(products=[ALPHA])
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        skus = db.scalars(select(HardwareProduct)).all()
        assert [s.id for s in skus] == ["M-0008_H-1_P-1"]
        sku = skus[0]
        assert sku.hardware_id == "M-0008_H-1"
        assert sku.name == "SKU Alpha"
        assert sku.order_number == "ORD-ALPHA"
        assert sku.is_rail_mounted is True
        assert sku.width_mm == 36.0
        assert sku.description == "Alpha variant"
        assert sku.default_language == "en-US"


def test_multi_sku_hardware_ingests_every_sku(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The regression: every <Product> SKU is persisted, not just products[0]."""
    content = build_knxprod_bytes(products=[ALPHA, BETA])
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        skus = {s.id: s for s in db.scalars(select(HardwareProduct)).all()}
        assert set(skus) == {"M-0008_H-1_P-1", "M-0008_H-1_P-2"}

        alpha = skus["M-0008_H-1_P-1"]
        assert alpha.hardware_id == "M-0008_H-1"
        assert alpha.order_number == "ORD-ALPHA"
        assert alpha.width_mm == 36.0
        assert alpha.is_rail_mounted is True
        assert alpha.name == "SKU Alpha"
        assert alpha.description == "Alpha variant"
        assert alpha.default_language == "en-US"

        beta = skus["M-0008_H-1_P-2"]
        # The pre-fix behavior dropped every one of these fields for the non-first SKU.
        assert beta.hardware_id == "M-0008_H-1"
        assert beta.order_number == "ORD-BETA"
        assert beta.width_mm == 72.0
        assert beta.is_rail_mounted is True
        assert beta.name == "SKU Beta"
        assert beta.description == "Beta variant"
        assert beta.default_language == "de-DE"


def test_multi_sku_hardware_row_keeps_first_sku_display_fields(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The Hardware row's per-SKU columns still carry the first SKU (backwards compat for the
    HTTP HardwareResponse and consumers not yet migrated to SKU-resolution)."""
    content = build_knxprod_bytes(products=[ALPHA, BETA])
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        hw = db.scalars(select(Hardware)).one()
        # Hardware row carries the first SKU's display fields (well-defined suppression of
        # ambiguity — documented in the warning emitted at ingest time).
        assert hw.order_number == "ORD-ALPHA"
        assert hw.width_mm == 36.0
        assert hw.is_rail_mounted is True
        assert hw.name == "SKU Alpha"
        assert hw.description == "Alpha variant"
        assert hw.default_language == "en-US"


def test_multi_sku_hardware_warns_at_ingest_time(
    catalog_engine: object, knxprod_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """The silent data-loss is surfaced — matches the codebase pattern (#54/#56) of warning
    when data cannot be fully represented by a row's columns."""
    content = build_knxprod_bytes(products=[ALPHA, BETA])
    with caplog.at_level(
        logging.WARNING,
        logger="xknxmono.catalog.core.upload",
    ):
        _ingest(content, catalog_engine, knxprod_dir)

    assert any(
        "M-0008_H-1" in record.getMessage() and "2" in record.getMessage()
        for record in caplog.records
        if record.name == "xknxmono.catalog.core.upload"
    )
    # The warning explicitly names the dropped SKUs so an operator can audit.
    msg = next(
        record.getMessage()
        for record in caplog.records
        if record.name == "xknxmono.catalog.core.upload"
    )
    assert "M-0008_H-1_P-1" in msg
    assert "M-0008_H-1_P-2" in msg


def test_single_sku_hardware_emits_no_warning(
    catalog_engine: object, knxprod_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    content = build_knxprod_bytes(products=[ALPHA])
    with caplog.at_level(
        logging.WARNING,
        logger="xknxmono.catalog.core.upload",
    ):
        _ingest(content, catalog_engine, knxprod_dir)

    assert not [
        record
        for record in caplog.records
        if record.name == "xknxmono.catalog.core.upload"
    ]


def test_productless_hardware_ingests_no_sku_rows(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """A <Hardware> with no <Products> ingests the row but no hardware_products rows."""
    content = build_knxprod_bytes(products=[])
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        assert db.scalars(select(Hardware)).one().id == "M-0008_H-1"
        assert db.scalars(select(HardwareProduct)).all() == []


def test_reingest_is_idempotent_for_skus(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """Ingesting the same content twice (deduped by content hash) doesn't duplicate SKU rows."""
    content = build_knxprod_bytes(products=[ALPHA, BETA])
    _ingest(content, catalog_engine, knxprod_dir)
    _ingest(content, catalog_engine, knxprod_dir)

    with Session(catalog_engine) as db:  # pyright: ignore[reportArgumentType]
        ids = sorted(s.id for s in db.scalars(select(HardwareProduct)).all())
        assert ids == ["M-0008_H-1_P-1", "M-0008_H-1_P-2"]


def test_catalog_item_persists_product_ref_id_for_nonfirst_sku(
    catalog_engine: object, knxprod_dir: Path
) -> None:
    """The product_ref_id pointing at a non-first SKU survives ingestion (it's the join key
    the SKU-resolution in list_products / get_hardware_by_program looks up)."""
    from xknxmono.catalog.models import CatalogSectionProduct

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
        item = db.scalars(select(CatalogSectionProduct)).one()
        assert item.product_ref_id == BETA.id
        assert item.hardware_program_id == "M-0008_H-1_HP-1"
