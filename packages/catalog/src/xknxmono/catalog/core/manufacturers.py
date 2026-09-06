"""Query functions for KNX manufacturers stored in the catalog database."""

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from xknxmono.catalog.models import Manufacturer


@dataclass(frozen=True)
class ManufacturerInfo:
    """A manufacturer's data, detached from the database session that read it.

    ``Manufacturer`` itself only carries ``id``/``name`` as columns - this
    mirrors them exactly. Snapshotting into a plain dataclass (rather than
    returning the ORM row) avoids ``DetachedInstanceError`` if a caller
    reaches for something after the session that read it has closed, and
    keeps this a stable return type if the table ever grows more columns.

    A manufacturer's hardware is deliberately not carried here - it can be
    a large, unbounded list, and this type is built on every per-device
    lookup. Use :func:`~xknxmono.catalog.core.hardware.list_hardware` with
    ``HardwareFilters(manufacturer_id=[id])`` for that, on demand.
    """

    id: str
    name: str | None


def list_manufacturers(db: Session) -> Sequence[Manufacturer]:
    """Return all manufacturers in the catalog, ordered by their M-XXXX ID.

    Args:
      db: An active SQLAlchemy session.

    Returns:
      A sequence of :class:`~xknxmono.catalog.models.Manufacturer` ORM objects,
      sorted ascending by ``id``.
    """
    return db.scalars(select(Manufacturer).order_by(Manufacturer.id)).all()


def get_manufacturer(db: Session, manufacturer_id: str) -> ManufacturerInfo | None:
    """Return a single manufacturer by its M-XXXX ID, or ``None`` if not found.

    Args:
      db: An active SQLAlchemy session.
      manufacturer_id: The manufacturer's primary-key identifier (e.g. ``"M-0001"``).

    Returns:
      A :class:`ManufacturerInfo` snapshot, or ``None`` if no manufacturer with
      that ID exists in the database.
    """
    manufacturer = db.get(Manufacturer, manufacturer_id)
    if manufacturer is None:
        return None
    return ManufacturerInfo(id=manufacturer.id, name=manufacturer.name)
