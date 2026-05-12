from datetime import UTC, datetime
from pathlib import Path

from xknxmono.models import load_xml
from xknxmono.product.archive import ProductArchive

from knx_gui.knxprod import parse_application_xml
from knx_gui.plugins.catalog.db.database import CatalogDatabase
from knx_gui.plugins.catalog.db.models import ApplicationModel


def _parse_manufacturer_names(master_xml: bytes) -> dict[str, str]:
    knx = load_xml(master_xml)
    result: dict[str, str] = {}
    if knx.master_data and knx.master_data.manufacturers:
        for mfr in knx.master_data.manufacturers.manufacturer:
            result[mfr.id] = mfr.name
    return result


def load_knxprod_to_catalog(catalog: CatalogDatabase, knxprod_path: Path) -> list[str]:
    added: list[str] = []

    with ProductArchive(knxprod_path) as archive:
        manufacturer_names = _parse_manufacturer_names(archive.get_master_xml())

        for manufacturer_id in archive.manufacturer_ids:
            manufacturer_name = manufacturer_names.get(manufacturer_id)
            if not manufacturer_name:
                raise ValueError(f"Manufacturer name not found for {manufacturer_id}")
            app_xmls = archive.get_application_xmls(manufacturer_id)

            for app_id, xml_data in app_xmls.items():
                existing = (
                    catalog.session.query(ApplicationModel)
                    .filter_by(application_id=app_id)
                    .first()
                )
                if existing:
                    continue

                device_apps = parse_application_xml(xml_data, manufacturer_id)
                app_name = device_apps[0].name if device_apps else app_id

                app = ApplicationModel(
                    manufacturer_id=manufacturer_id,
                    manufacturer_name=manufacturer_name,
                    application_id=app_id,
                    name=app_name,
                    xml_data=xml_data,
                    created_at=datetime.now(UTC),
                )
                catalog.session.add(app)
                added.append(app_id)

            catalog.session.commit()

    return added


def get_application_xml(catalog: CatalogDatabase, application_id: str) -> bytes | None:
    app = (
        catalog.session.query(ApplicationModel)
        .filter_by(application_id=application_id)
        .first()
    )
    if app:
        return app.xml_data
    return None
