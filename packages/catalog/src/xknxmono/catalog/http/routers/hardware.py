"""Hardware router: list and retrieve KNX hardware items and their application program details."""
import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
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
from xknxmono.catalog.http.schemas import (
  AbsoluteSegmentOut,
  ApplicationDetailOut,
  ApplicationOut,
  CodeOut,
  ComObjectFlagsOut,
  ComObjectOut,
  EnumOptionOut,
  HardwareOut,
  HardwareProgramOut,
  ParameterOut,
  ParamTypeOut,
  RelativeSegmentOut,
)
from xknxmono.catalog.models import Hardware, HardwareProgram
from xknxmono.product.errors import ArchiveError

router = APIRouter(prefix="/hardware", tags=["Hardware"])

DbDep = Annotated[Session, Depends(get_db)]


def _program_out(p: HardwareProgram) -> HardwareProgramOut:
  """Convert a HardwareProgram ORM object to its API response schema."""
  return HardwareProgramOut(
    id=p.id,
    hardware_id=p.hardware_id,
    medium_types=[mt.medium_type for mt in p.medium_types],
    registration_status=p.registration_status,
    registration_number=p.registration_number,
    registration_date=p.registration_date,
    application=ApplicationOut.model_validate(p.application) if p.application else None,
  )


def _hardware_out(h: Hardware) -> HardwareOut:
  """Convert a Hardware ORM object to its API response schema."""
  return HardwareOut(
    id=h.id,
    manufacturer_id=h.manufacturer_id,
    name=h.name,
    order_number=h.order_number,
    description=h.description,
    is_rail_mounted=h.is_rail_mounted,
    width_mm=h.width_mm,
    serial_number=h.serial_number,
    version_number=h.version_number,
    bus_current=h.bus_current,
    has_application_program=h.has_application_program,
    is_coupler=h.is_coupler,
    is_power_supply=h.is_power_supply,
    is_ip_enabled=h.is_ip_enabled,
    no_download_without_plugin=h.no_download_without_plugin,
    default_language=h.default_language,
    programs=[_program_out(p) for p in h.programs],
  )


@router.get("", response_model=list[HardwareOut])
def list_hardware_endpoint(
  manufacturer_id: Annotated[list[str] | None, Query(description="Filter by manufacturer (repeatable)")] = None,
  medium_type: Annotated[list[str] | None, Query(description="Filter by medium type (repeatable)")] = None,
  section_id: str | None = None,
  is_secure_enabled: bool | None = None,
  is_rail_mounted: bool | None = None,
  is_coupler: bool | None = None,
  is_power_supply: bool | None = None,
  is_ip_enabled: bool | None = None,
  has_application_program: bool | None = None,
  no_download_without_plugin: bool | None = None,
  registration_status: str | None = None,
  registration_number: str | None = None,
  registration_date_from: datetime.date | None = None,
  registration_date_to: datetime.date | None = None,
  mask_version: str | None = None,
  search: str | None = Query(None, description="Search hardware name or order number"),
  limit: int = Query(50, le=200),
  offset: int = 0,
  db: DbDep = None,  # type: ignore[assignment]
):
  """List hardware items with optional filters for manufacturer, medium type, flags, registration, and free-text search."""
  filters = HardwareFilters(
    manufacturer_ids=manufacturer_id or [],
    medium_types=medium_type or [],
    section_id=section_id,
    is_secure_enabled=is_secure_enabled,
    is_rail_mounted=is_rail_mounted,
    is_coupler=is_coupler,
    is_power_supply=is_power_supply,
    is_ip_enabled=is_ip_enabled,
    has_application_program=has_application_program,
    no_download_without_plugin=no_download_without_plugin,
    registration_status=registration_status,
    registration_number=registration_number,
    registration_date_from=registration_date_from,
    registration_date_to=registration_date_to,
    mask_version=mask_version,
    search=search,
    limit=limit,
    offset=offset,
  )
  return [_hardware_out(h) for h in list_hardware(db, filters)]


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
    raise HTTPException(404, "No application program associated with this hardware program")

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

  code = None
  if app.code:
    code = CodeOut(
      absolute_segments=[
        AbsoluteSegmentOut.model_validate(s) for s in app.code.absolute_segments
      ],
      relative_segments=[
        RelativeSegmentOut.model_validate(s) for s in app.code.relative_segments
      ],
    )

  return ApplicationDetailOut(
    application_id=app.application_id,
    name=app.name,
    manufacturer_id=app.manufacturer_id,
    com_objects=[
      ComObjectOut(
        id=co.id,
        name=co.name,
        number=co.number,
        dpt_codes=co.dpt_codes,
        flags=ComObjectFlagsOut(
          communication=co.flags.communication,
          read=co.flags.read,
          write=co.flags.write,
          transmit=co.flags.transmit,
          update=co.flags.update,
          read_on_init=co.flags.read_on_init,
        ),
      )
      for co in app.com_objects
    ],
    parameters=[
      ParameterOut(
        id=p.id,
        ref_id=p.ref_id,
        name=p.name,
        text=p.text,
        value=p.value,
        param_type=ParamTypeOut(
          kind=p.param_type.kind.value,
          options=[EnumOptionOut(value=o.value, text=o.text) for o in p.param_type.options],
          min_value=p.param_type.min_value,
          max_value=p.param_type.max_value,
          size_bits=p.param_type.size_bits,
        ) if p.param_type else None,
      )
      for p in app.parameters
    ],
    code=code,
  )


@router.get("/{hardware_id}", response_model=HardwareOut)
def get_hardware_endpoint(hardware_id: str, db: DbDep = None):  # type: ignore[assignment]
  """Return a single hardware item by its ID, including all associated programs."""
  hw = get_hardware(db, hardware_id)
  if not hw:
    raise HTTPException(404, "Hardware not found")
  return _hardware_out(hw)
