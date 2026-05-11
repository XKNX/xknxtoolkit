from datetime import UTC, datetime
from pathlib import Path

from knx_gui.catalog.database import CatalogDatabase
from knx_gui.catalog.models import ApplicationModel
from xknx.product.archive import ProductArchive


def load_knxprod_to_catalog(catalog: CatalogDatabase, knxprod_path: Path) -> list[str]:
    added: list[str] = []

    with ProductArchive(knxprod_path) as archive:
        for manufacturer_id in archive.manufacturer_ids:
            app_xmls = archive.get_application_xmls(manufacturer_id)

            for app_id, xml_data in app_xmls.items():
                existing = (
                    catalog.session.query(ApplicationModel)
                    .filter_by(application_id=app_id)
                    .first()
                )
                if existing:
                    continue

                app = ApplicationModel(
                    manufacturer_id=manufacturer_id,
                    application_id=app_id,
                    name=app_id,
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
