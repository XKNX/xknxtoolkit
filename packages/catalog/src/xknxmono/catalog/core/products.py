"""Product-centric catalog browse entries.

A *product* is an orderable catalog item bound to a specific hardware program; selecting one yields
the ``product_ref_id`` + ``hardware2program_ref_id`` a project device needs (the application is
resolved from the program). This is the product-first counterpart to the app-first
:mod:`xknxmono.catalog.core.applications` view.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from xknxmono.catalog.models import (
    CatalogSectionProduct,
    Hardware,
    HardwareProduct,
    HardwareProgram,
    Manufacturer,
)


@dataclass
class ProductSummary:
    """An orderable product: the refs a device needs, plus display fields and its manufacturer."""

    product_ref_id: str
    hardware2program_ref_id: str
    name: str | None
    order_number: str | None
    application_id: str | None
    manufacturer_id: str
    manufacturer_name: str | None


def list_products(db: Session) -> list[ProductSummary]:
    """Every catalog item that carries a ``ProductRefId``, with its program, application and maker.

    ``order_number`` is sourced from the SKU the catalog item actually references — i.e. the
    :class:`HardwareProduct` row whose ``id`` equals ``CatalogSectionProduct.product_ref_id`` —
    rather than from the hardware's first-SKU defaults on the :class:`Hardware` row, so a
    catalog item pointing at a non-first SKU returns that SKU's order number. The ``Hardware``
    row's order number is only used as a fallback when a referenced SKU has no row of its own
    (e.g. older databases ingested before the per-SKU table existed).
    """
    rows = db.execute(
        select(
            CatalogSectionProduct.product_ref_id,
            CatalogSectionProduct.hardware_program_id,
            CatalogSectionProduct.name,
            HardwareProduct.order_number,
            Hardware.order_number,
            HardwareProgram.application_id,
            Manufacturer.id,
            Manufacturer.name,
        )
        .join(
            HardwareProgram,
            HardwareProgram.id == CatalogSectionProduct.hardware_program_id,
        )
        .join(Hardware, Hardware.id == HardwareProgram.hardware_id)
        .join(
            HardwareProduct,
            HardwareProduct.id == CatalogSectionProduct.product_ref_id,
            isouter=True,
        )
        .join(Manufacturer, Manufacturer.id == Hardware.manufacturer_id)
        .where(CatalogSectionProduct.product_ref_id.is_not(None))
        .distinct()
    ).all()
    return [
        ProductSummary(
            product_ref_id=product_ref_id,
            hardware2program_ref_id=hardware_program_id,
            name=name,
            order_number=sku_order_number
            if sku_order_number is not None
            else hardware_order_number,
            application_id=application_id,
            manufacturer_id=manufacturer_id,
            manufacturer_name=manufacturer_name,
        )
        for (
            product_ref_id,
            hardware_program_id,
            name,
            sku_order_number,
            hardware_order_number,
            application_id,
            manufacturer_id,
            manufacturer_name,
        ) in rows
        if product_ref_id is not None
    ]
