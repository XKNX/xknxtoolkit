"""Core ingestion logic for .knxprod files."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session
from xknxmono.product.archive import ProductArchive
from xknxmono.product.data import load_archive

from xknxmono.catalog.db import get_engine
from xknxmono.catalog.models import (
    Application,
    CatalogSection,
    CatalogSectionProduct,
    Hardware,
    HardwareProgram,
    HardwareProgramMediumType,
    Manufacturer,
)


def _walk_manufacturer_data(knx: Any):
    """Yield each manufacturer entry from a parsed KNX XML root object."""
    md = getattr(knx, "manufacturer_data", None)
    yield from getattr(md, "manufacturer", []) or []


def _ingest_applications(session: Session, data_applications: list[Any]) -> None:
    """Upsert all application programs from the parsed application XML objects into the database."""
    for app_knx in data_applications:
        for mfr in _walk_manufacturer_data(app_knx):
            app_programs = getattr(mfr, "application_programs", None)
            for ap in getattr(app_programs, "application_program", []) or []:
                session.merge(Application(
                    id=ap.id,
                    name=getattr(ap, "name", None) or ap.id,
                    application_number=getattr(ap, "application_number", None),
                    application_version=getattr(ap, "application_version", None),
                    mask_version=getattr(ap, "mask_version", None),
                    is_secure_enabled=getattr(ap, "is_secure_enabled", False),
                ))


def _ingest_hardware(
    session: Session, hw_knx: Any, mfr_id: str, knxprod_path: str
) -> None:
    """Upsert hardware items and their hardware programs from the parsed Hardware.xml object."""
    if not session.get(Manufacturer, mfr_id):
        session.add(Manufacturer(id=mfr_id, name=None))

    for mfr in _walk_manufacturer_data(hw_knx):
        hw_container = getattr(mfr, "hardware", None)
        for hw in getattr(hw_container, "hardware", []) or []:
            products_container = getattr(hw, "products", None)
            products = getattr(products_container, "product", []) or []
            prod = products[0] if products else None

            session.merge(Hardware(
                id=hw.id,
                manufacturer_id=mfr_id,
                name=prod.text if prod else None,
                order_number=prod.order_number if prod else None,
                is_rail_mounted=getattr(prod, "is_rail_mounted", None) if prod else None,
                width_mm=getattr(prod, "width_in_millimeter", None) if prod else None,
                description=getattr(prod, "visible_description", None) if prod else None,
                default_language=getattr(prod, "default_language", None) if prod else None,
                serial_number=getattr(hw, "serial_number", None),
                version_number=getattr(hw, "version_number", None),
                bus_current=getattr(hw, "bus_current", None),
                has_application_program=getattr(hw, "has_application_program", None),
                is_coupler=getattr(hw, "is_coupler", None),
                is_power_supply=getattr(hw, "is_power_supply", None),
                is_ip_enabled=getattr(hw, "is_ipenabled", None),
                no_download_without_plugin=getattr(hw, "no_download_without_plugin", None),
            ))

            h2ps_container = getattr(hw, "hardware2_programs", None)
            for h2p in getattr(h2ps_container, "hardware2_program", []) or []:
                app_refs = getattr(h2p, "application_program_ref", []) or []
                app_id = app_refs[0].ref_id if app_refs else None

                reg = getattr(h2p, "registration_info", None)
                reg_status = None
                reg_number = None
                reg_date = None
                if reg is not None:
                    status = getattr(reg, "registration_status", None)
                    reg_status = status.value if status is not None else None
                    reg_number = getattr(reg, "registration_number", None)
                    xml_date = getattr(reg, "registration_date", None)
                    reg_date = xml_date.to_date() if xml_date is not None else None

                session.merge(HardwareProgram(
                    id=h2p.id,
                    hardware_id=hw.id,
                    application_id=app_id,
                    knxprod_path=knxprod_path,
                    registration_status=reg_status,
                    registration_number=reg_number,
                    registration_date=reg_date,
                ))

                for mt in getattr(h2p, "medium_types", []) or []:
                    session.merge(HardwareProgramMediumType(hardware_program_id=h2p.id, medium_type=mt))


def _ingest_section(
    session: Session, section: Any, mfr_id: str, parent_id: str | None
) -> None:
    """Recursively upsert a catalog section and its children and product references."""
    session.merge(CatalogSection(
        id=section.id,
        manufacturer_id=mfr_id,
        parent_id=parent_id,
        name=section.name,
        number=getattr(section, "number", None),
    ))
    for item in getattr(section, "catalog_item", []) or []:
        prod_ref = getattr(item, "hardware2_program_ref_id", None)
        if prod_ref:
            session.merge(CatalogSectionProduct(section_id=section.id, hardware_program_id=prod_ref))
    for child in getattr(section, "catalog_section", []) or []:
        _ingest_section(session, child, mfr_id, section.id)


def _ingest_catalog(session: Session, cat_knx: Any, mfr_id: str) -> None:
    """Upsert all top-level catalog sections for a manufacturer from the parsed Catalog.xml object."""
    for mfr in _walk_manufacturer_data(cat_knx):
        cat_container = getattr(mfr, "catalog", None)
        for section in getattr(cat_container, "catalog_section", []) or []:
            _ingest_section(session, section, mfr_id, None)


def ingest_file(content: bytes, dest_dir: Path) -> Path:
    """Ingest .knxprod bytes. Returns the path where the file was saved.

    Skips silently if the same content (by SHA3-256) was already ingested.
    File is written to disk only after a successful DB commit.
    """
    path = dest_dir / f"{hashlib.sha3_256(content).hexdigest()}.knxprod"
    if path.exists():
        return path

    with ProductArchive(content) as archive:
        with Session(get_engine()) as session:
            for mfr_id in archive.manufacturer_ids:
                data = load_archive(archive, mfr_id)
                _ingest_applications(session, data.applications)
                _ingest_hardware(session, data.hardware, mfr_id, str(path))
                _ingest_catalog(session, data.catalog, mfr_id)
            session.commit()

    path.write_bytes(content)
    return path
