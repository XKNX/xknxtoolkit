"""Manufacturers router: list and retrieve KNX manufacturers from the catalog."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from xknxmono.catalog.core.manufacturers import get_manufacturer, list_manufacturers
from xknxmono.catalog.http.deps import get_db
from xknxmono.catalog.http.schemas import ManufacturerResponse

router = APIRouter(prefix="/manufacturers", tags=["Manufacturers"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ManufacturerResponse])
def list_manufacturers_endpoint(db: DbDep):
    """Return all manufacturers in the catalog, ordered by ID."""
    return list_manufacturers(db)


@router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
def get_manufacturer_endpoint(manufacturer_id: str, db: DbDep):
    """Return a single manufacturer by its M-XXXX ID."""
    mfr = get_manufacturer(db, manufacturer_id)
    if not mfr:
        raise HTTPException(404, "Manufacturer not found")
    return mfr
