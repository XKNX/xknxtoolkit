"""Hardware router: list and retrieve KNX hardware items and their application program details."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from xknxmono.catalog.core.hardware import (
    HardwareFilters,
    get_application_detail,
    get_application_xml,
    get_hardware,
    get_hardware_program,
    list_hardware,
)
from xknxmono.catalog.db import get_db
from xknxmono.catalog.http.schemas import ApplicationDetailResponse, HardwareResponse
from xknxmono.product.errors import ArchiveError

router = APIRouter(prefix="/hardware", tags=["Hardware"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[HardwareResponse])
def list_hardware_endpoint(
    filters: Annotated[HardwareFilters, Depends()],
    db: DbDep = None,  # type: ignore[assignment]
):
    """List hardware items with optional filters for manufacturer, medium type, flags, registration, and free-text search."""
    return list_hardware(db, filters)


@router.get("/{hardware_id}/programs/{program_id}/application")
def get_program_application(
    hardware_id: str,
    program_id: str,
    accept: Annotated[str, Header()] = "application/json",
    db: DbDep = None,  # type: ignore[assignment]
):
    """Return full application detail for a hardware program, parsed from the source .knxprod archive.

    Accepts ``application/xml`` to return the raw XML instead of the parsed JSON response.
    """
    # Validate ownership: the program must belong to this hardware item.
    program = get_hardware_program(db, hardware_id, program_id)
    if not program:
        raise HTTPException(404, "Hardware program not found")
    if not program.application_id:
        raise HTTPException(
            404, "No application program associated with this hardware program"
        )

    if "application/xml" in accept:
        try:
            result = get_application_xml(db, program_id)
        except ArchiveError as e:
            raise HTTPException(500, f"Cannot open archive: {e}") from e
        if result is None:
            raise HTTPException(404, "Application XML not found in archive")
        xml_bytes, _ = result
        return Response(content=xml_bytes, media_type="application/xml")

    try:
        app = get_application_detail(db, program_id)
    except ArchiveError as e:
        raise HTTPException(500, f"Cannot open archive: {e}") from e
    if app is None:
        raise HTTPException(404, "Application not found in archive")

    return ApplicationDetailResponse.model_validate(app)


@router.get("/{hardware_id}", response_model=HardwareResponse)
def get_hardware_endpoint(hardware_id: str, db: DbDep = None):  # type: ignore[assignment]
    """Return a single hardware item by its ID, including all associated programs."""
    hw = get_hardware(db, hardware_id)
    if not hw:
        raise HTTPException(404, "Hardware not found")
    return hw
