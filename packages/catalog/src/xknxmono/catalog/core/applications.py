"""Application-centric catalog queries.

The catalog schema is hardware-centric (an :class:`Application` is reached through the hardware
programs that reference it), but consumers such as a device-picker want a flat, app-first view.
These helpers provide that: list every application with the manufacturer that ships it, and resolve
the full parsed application detail straight from an application id.
"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from xknxmono.catalog.core.hardware import get_application_detail
from xknxmono.catalog.models import (
    Application,
    Hardware,
    HardwareProgram,
    Manufacturer,
)
from xknxmono.product import Application as ProductApplication


@dataclass(frozen=True)
class ApplicationSummary:
    """A flat, app-first catalog entry: an application plus the manufacturer that ships it."""

    application_id: str
    name: str
    manufacturer_id: str
    manufacturer_name: str | None


def list_applications(db: Session) -> list[ApplicationSummary]:
    """Every application with its manufacturer, resolved via the hardware programs that use it."""
    rows = db.execute(
        select(Application.id, Application.name, Manufacturer.id, Manufacturer.name)
        .join(HardwareProgram, HardwareProgram.application_id == Application.id)
        .join(Hardware, Hardware.id == HardwareProgram.hardware_id)
        .join(Manufacturer, Manufacturer.id == Hardware.manufacturer_id)
        .distinct()
    ).all()
    return [
        ApplicationSummary(
            application_id=app_id,
            name=name,
            manufacturer_id=mfr_id,
            manufacturer_name=mfr_name,
        )
        for app_id, name, mfr_id, mfr_name in rows
    ]


def get_application_detail_by_id(
    db: Session, application_id: str
) -> ProductApplication | None:
    """Parsed application detail for an application id, via any hardware program that references it.

    Returns the IR-backed product :class:`~xknxmono.product.Application`, or ``None`` if no program
    references the id (or its archive no longer holds the application).
    """
    program_id = db.scalars(
        select(HardwareProgram.id)
        .where(HardwareProgram.application_id == application_id)
        .limit(1)
    ).first()
    if program_id is None:
        return None
    return get_application_detail(db, program_id)
