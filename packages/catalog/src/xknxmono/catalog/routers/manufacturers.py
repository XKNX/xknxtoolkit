"""Manufacturers router: list and retrieve KNX manufacturers from the catalog."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from xknxmono.catalog.db import get_db
from xknxmono.catalog.models import Manufacturer
from xknxmono.catalog.schemas import ManufacturerOut

router = APIRouter(prefix="/manufacturers", tags=["Manufacturers"])


@router.get("", response_model=list[ManufacturerOut])
def list_manufacturers(db: Session = Depends(get_db)):
    """Return all manufacturers in the catalog, ordered by ID."""
    return db.scalars(select(Manufacturer).order_by(Manufacturer.id)).all()


@router.get("/{manufacturer_id}", response_model=ManufacturerOut)
def get_manufacturer(manufacturer_id: str, db: Session = Depends(get_db)):
    """Return a single manufacturer by its M-XXXX ID."""
    mfr = db.get(Manufacturer, manufacturer_id)
    if not mfr:
        raise HTTPException(404, "Manufacturer not found")
    return mfr
