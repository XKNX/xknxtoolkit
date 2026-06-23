"""Hardware router: list and retrieve KNX hardware items and their application program details."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import Response

from xknxmono.catalog.core.hardware import HardwareFilters
from xknxmono.catalog.core.service import CatalogService
from xknxmono.catalog.http.deps import get_service
from xknxmono.catalog.http.schemas import ApplicationDetailResponse, HardwareResponse
from xknxmono.product.errors import ArchiveError

router = APIRouter(prefix="/hardware", tags=["Hardware"])

ServiceDep = Annotated[CatalogService, Depends(get_service)]


@router.get("", response_model=list[HardwareResponse])
def list_hardware_endpoint(
    filters: Annotated[HardwareFilters, Query()],
    service: ServiceDep,
):
    """List hardware items with optional filters for manufacturer, medium type, flags, registration, and free-text search."""
    return service.list_hardware(filters)


@router.get("/{hardware_id}/programs/{program_id}/application")
def get_program_application(
    hardware_id: str,
    program_id: str,
    service: ServiceDep,
    accept: Annotated[str, Header()] = "application/json",
):
    """Return full application detail for a hardware program, parsed from the source .knxprod archive.

    Accepts ``application/xml`` to return the raw XML instead of the parsed JSON response.
    """
    # Validate ownership: the program must belong to this hardware item.
    program = service.get_hardware_program(hardware_id, program_id)
    if not program:
        raise HTTPException(404, "Hardware program not found")
    if not program.application_id:
        raise HTTPException(
            404, "No application program associated with this hardware program"
        )

    if "application/xml" in accept:
        try:
            result = service.get_application_xml(program_id)
        except ArchiveError as e:
            raise HTTPException(500, f"Cannot open archive: {e}") from e
        if result is None:
            raise HTTPException(404, "Application XML not found in archive")
        xml_bytes, _ = result
        return Response(content=xml_bytes, media_type="application/xml")

    try:
        app = service.get_application_detail(program_id)
    except ArchiveError as e:
        raise HTTPException(500, f"Cannot open archive: {e}") from e
    if app is None:
        raise HTTPException(404, "Application not found in archive")

    from xknxmono.models.intermediate.enable_t import Enable

    com_objects: list[ApplicationDetailResponse.ComObject] = []
    tbl = app.program.static.com_object_table
    if tbl is not None:
        for co in tbl.com_object:
            com_objects.append(
                ApplicationDetailResponse.ComObject(
                    id=co.id,
                    name=co.name,
                    number=co.number,
                    dpt_codes=co.datapoint_type,
                    flags=ApplicationDetailResponse.ComObjectFlags(
                        communication=co.communication_flag == Enable.ENABLED,
                        read=co.read_flag == Enable.ENABLED,
                        write=co.write_flag == Enable.ENABLED,
                        transmit=co.transmit_flag == Enable.ENABLED,
                        update=co.update_flag == Enable.ENABLED,
                        read_on_init=co.read_on_init_flag == Enable.ENABLED,
                    ),
                )
            )
    return ApplicationDetailResponse(
        application_id=app.id,
        name=app.name,
        manufacturer_id=app.manufacturer_id,
        com_objects=com_objects,
        parameters=[],
        code=ApplicationDetailResponse.Code.model_validate(app.code) if app.code else None,
    )


@router.get("/{hardware_id}", response_model=HardwareResponse)
def get_hardware_endpoint(hardware_id: str, service: ServiceDep):
    """Return a single hardware item by its ID, including all associated programs."""
    hw = service.get_hardware(hardware_id)
    if not hw:
        raise HTTPException(404, "Hardware not found")
    return hw
