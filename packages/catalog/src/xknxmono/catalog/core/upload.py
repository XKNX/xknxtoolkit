"""Core ingestion logic for .knxprod files — populates the catalog DB from a product Registry."""

from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from xknxmono.catalog.models import (
    Application,
    CatalogSection,
    CatalogSectionProduct,
    Hardware,
    HardwareProgram,
    HardwareProgramMediumType,
    Manufacturer,
)
from xknxmono.product import DeviceProgram, Registry, load


def _ingest_manufacturers(session: Session, reg: Registry) -> None:
    names = reg.master.manufacturers
    mids = set(reg.manufacturer_to_hardware) | set(reg.manufacturer_to_section)
    for mid in mids:
        session.merge(Manufacturer(id=mid, name=names.get(mid)))


def _ingest_applications(session: Session, reg: Registry) -> None:
    for app in reg.applications.values():
        program = app.program
        session.merge(
            Application(
                id=app.id,
                name=app.name,
                application_number=program.application_number,
                application_version=program.application_version,
                mask_version=program.mask_version,
                is_secure_enabled=bool(program.is_secure_enabled),
            )
        )


def _ingest_hardware(session: Session, reg: Registry, knxprod_path: str) -> None:
    for mfr_id, hardware_ids in reg.manufacturer_to_hardware.items():
        for hardware_id in hardware_ids:
            hw = reg.hardware[hardware_id]
            raw = hw.raw
            products = list(reg.products_for_hardware(hardware_id).values())
            product = products[0] if products else None
            session.merge(
                Hardware(
                    id=hw.id,
                    manufacturer_id=mfr_id,
                    name=product.name if product else hw.name,
                    order_number=product.order_number if product else None,
                    is_rail_mounted=product.rail_mounted if product else None,
                    width_mm=product.width_mm if product else None,
                    description=product.raw.visible_description if product else None,
                    default_language=product.raw.default_language if product else None,
                    serial_number=raw.serial_number,
                    version_number=raw.version_number,
                    bus_current=raw.bus_current,
                    has_application_program=raw.has_application_program,
                    is_coupler=raw.is_coupler,
                    is_power_supply=raw.is_power_supply,
                    is_ip_enabled=raw.is_ipenabled,
                    no_download_without_plugin=raw.no_download_without_plugin,
                )
            )
            for program in reg.programs_for_hardware(hardware_id).values():
                _ingest_program(session, hw.id, program, knxprod_path)


def _ingest_program(
    session: Session, hardware_id: str, program: DeviceProgram, knxprod_path: str
) -> None:
    app_id = program.application_ref_ids[0] if program.application_ref_ids else None

    reg_status = reg_number = reg_date = None
    info = program.raw.registration_info
    if info is not None:
        reg_status = info.registration_status.value
        reg_number = info.registration_number
        reg_date = info.registration_date.to_date() if info.registration_date else None

    session.merge(
        HardwareProgram(
            id=program.id,
            hardware_id=hardware_id,
            application_id=app_id,
            knxprod_path=knxprod_path,
            registration_status=reg_status,
            registration_number=reg_number,
            registration_date=reg_date,
        )
    )
    for medium_type in program.raw.medium_types or []:
        session.merge(
            HardwareProgramMediumType(
                hardware_program_id=program.id, medium_type=medium_type
            )
        )


def _ingest_catalog(session: Session, reg: Registry) -> None:
    for mfr_id, section_ids in reg.manufacturer_to_section.items():
        for section_id in section_ids:
            section = reg.catalog_sections[section_id]
            session.merge(
                CatalogSection(
                    id=section.id,
                    manufacturer_id=mfr_id,
                    parent_id=section.parent_id,
                    name=section.name or section.id,
                    number=section.number,
                )
            )
            for item in reg.items_for_section(section_id).values():
                if item.hardware2_program_ref_id:
                    session.merge(
                        CatalogSectionProduct(
                            id=item.id,
                            section_id=section.id,
                            hardware_program_id=item.hardware2_program_ref_id,
                            product_ref_id=item.product_ref_id,
                            name=item.name,
                        )
                    )


def upload_knxprod(content: bytes, dest_dir: Path, engine: Engine) -> Path:
    """Ingest .knxprod bytes into the database behind ``engine``. Returns the path where the file was saved.

    Skips silently if the same content (by SHA3-256) was already ingested.
    File is written to disk only after a successful DB commit.
    """
    path = dest_dir / f"{hashlib.sha3_256(content).hexdigest()}.knxprod"
    if path.exists():
        return path

    registry = load(content)
    with Session(engine) as session:
        _ingest_manufacturers(session, registry)
        _ingest_applications(session, registry)
        _ingest_hardware(session, registry, str(path))
        _ingest_catalog(session, registry)
        session.commit()

    path.write_bytes(content)
    return path
