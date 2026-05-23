import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from xknxmono.product.archive import ProductArchive
from xknxmono.product.errors import ArchiveError
from xknxmono.product.parser import parse_application_xml

from xknxmono.catalog.db import get_db
from xknxmono.catalog.models import Application, CatalogSection, CatalogSectionProduct, Hardware, HardwareProgram, HardwareProgramMediumType
from xknxmono.catalog.routers.catalog_sections import collect_section_ids
from xknxmono.catalog.schemas import (
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

router = APIRouter(prefix="/hardware", tags=["Hardware"])


def _program_out(p: HardwareProgram) -> HardwareProgramOut:
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


def _base_query():
    return select(Hardware).options(
        selectinload(Hardware.programs).selectinload(HardwareProgram.medium_types),
        selectinload(Hardware.programs).selectinload(HardwareProgram.application),
    )


@router.get("", response_model=list[HardwareOut])
def list_hardware(
    manufacturer_id: Annotated[list[str], Query(description="Filter by manufacturer (repeatable)")] = [],
    medium_type: Annotated[list[str], Query(description="Filter by medium type (repeatable)")] = [],
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
    db: Session = Depends(get_db),
):
    q = _base_query()

    needs_program_join = bool(
        medium_type or is_secure_enabled is not None or mask_version is not None
        or registration_status is not None or registration_number is not None
        or registration_date_from is not None or registration_date_to is not None
        or section_id is not None
    )
    if needs_program_join:
        q = q.join(Hardware.programs)

    if manufacturer_id:
        q = q.where(Hardware.manufacturer_id.in_(manufacturer_id))
    if is_rail_mounted is not None:
        q = q.where(Hardware.is_rail_mounted == is_rail_mounted)
    if is_coupler is not None:
        q = q.where(Hardware.is_coupler == is_coupler)
    if is_power_supply is not None:
        q = q.where(Hardware.is_power_supply == is_power_supply)
    if is_ip_enabled is not None:
        q = q.where(Hardware.is_ip_enabled == is_ip_enabled)
    if has_application_program is not None:
        q = q.where(Hardware.has_application_program == has_application_program)
    if no_download_without_plugin is not None:
        q = q.where(Hardware.no_download_without_plugin == no_download_without_plugin)
    if search:
        term = f"%{search}%"
        q = q.where(Hardware.name.ilike(term) | Hardware.order_number.ilike(term))
    if medium_type:
        q = q.join(HardwareProgram.medium_types).where(HardwareProgramMediumType.medium_type.in_(medium_type))
    if is_secure_enabled is not None or mask_version is not None:
        q = q.join(HardwareProgram.application, isouter=True)
        if is_secure_enabled is not None:
            q = q.where(Application.is_secure_enabled == is_secure_enabled)
        if mask_version is not None:
            q = q.where(Application.mask_version == mask_version)
    if registration_status is not None:
        q = q.where(HardwareProgram.registration_status == registration_status)
    if registration_number is not None:
        q = q.where(HardwareProgram.registration_number == registration_number)
    if registration_date_from is not None:
        q = q.where(HardwareProgram.registration_date >= registration_date_from)
    if registration_date_to is not None:
        q = q.where(HardwareProgram.registration_date <= registration_date_to)
    if section_id is not None:
        ids = collect_section_ids(db, section_id)
        q = (
            q.join(CatalogSectionProduct, CatalogSectionProduct.hardware_program_id == HardwareProgram.id)
            .join(CatalogSection, CatalogSection.id == CatalogSectionProduct.section_id)
            .where(CatalogSection.id.in_(ids))
        )

    q = q.distinct().offset(offset).limit(limit)
    return [_hardware_out(h) for h in db.scalars(q).unique().all()]


@router.get("/{hardware_id}/programs/{program_id}/application")
def get_program_application(
    hardware_id: str,
    program_id: str,
    accept: Annotated[str, Header()] = "application/json",
    db: Session = Depends(get_db),
):
    program = db.scalars(
        select(HardwareProgram)
        .options(selectinload(HardwareProgram.hardware))
        .where(HardwareProgram.id == program_id, HardwareProgram.hardware_id == hardware_id)
    ).first()
    if not program:
        raise HTTPException(404, "Hardware program not found")
    if not program.application_id:
        raise HTTPException(404, "No application program associated with this hardware program")

    manufacturer_id = program.hardware.manufacturer_id

    try:
        archive = ProductArchive(program.knxprod_path)
    except ArchiveError as e:
        raise HTTPException(500, f"Cannot open archive: {e}")

    with archive:
        app_xmls = archive.get_application_xmls(manufacturer_id)
        xml_bytes = app_xmls.get(program.application_id)
        if xml_bytes is None:
            raise HTTPException(404, "Application XML not found in archive")

        if "application/xml" in accept:
            return Response(content=xml_bytes, media_type="application/xml")

        apps = parse_application_xml(xml_bytes, manufacturer_id)
        app = next((a for a in apps if a.application_id == program.application_id), None)
        if app is None:
            raise HTTPException(404, "Application not found in archive")

        code = None
        if app.code:
            code = CodeOut(
                absolute_segments=[
                    AbsoluteSegmentOut.model_validate(s)
                    for s in app.code.absolute_segments
                ],
                relative_segments=[
                    RelativeSegmentOut.model_validate(s)
                    for s in app.code.relative_segments
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
def get_hardware(hardware_id: str, db: Session = Depends(get_db)):
    hw = db.scalars(
        _base_query().where(Hardware.id == hardware_id)
    ).first()
    if not hw:
        raise HTTPException(404, "Hardware not found")
    return _hardware_out(hw)
