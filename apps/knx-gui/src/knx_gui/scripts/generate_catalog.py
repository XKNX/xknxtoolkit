"""Generate or update the catalog database from knxprod files."""

import sys
from datetime import UTC, datetime
from pathlib import Path

from knx_gui.catalog.database import CatalogDatabase
from knx_gui.catalog.loader import load_knxprod_to_catalog
from knx_gui.catalog.models import ApplicationModel

DEMO_TEMPLATES = [
    {
        "application_id": "demo:switch_actuator",
        "manufacturer_id": "ABB",
        "name": "Switch Actuator",
    },
    {
        "application_id": "demo:dimmer_actuator",
        "manufacturer_id": "ABB",
        "name": "Dimmer Actuator",
    },
    {
        "application_id": "demo:temperature_sensor",
        "manufacturer_id": "Siemens",
        "name": "Temperature Sensor",
    },
    {
        "application_id": "demo:push_button",
        "manufacturer_id": "Gira",
        "name": "Push Button",
    },
    {
        "application_id": "demo:blinds_actuator",
        "manufacturer_id": "MDT",
        "name": "Blinds Actuator",
    },
    {
        "application_id": "demo:shutter_button",
        "manufacturer_id": "Gira",
        "name": "Shutter Button",
    },
    {
        "application_id": "demo:rgb_controller",
        "manufacturer_id": "MDT",
        "name": "RGB Controller",
    },
    {
        "application_id": "demo:logic_gate",
        "manufacturer_id": "MDT",
        "name": "Logic Gate",
    },
    {
        "application_id": "demo:thermostat",
        "manufacturer_id": "Theben",
        "name": "Thermostat",
    },
]


def make_fake_xml(app_id: str, name: str) -> bytes:
    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/21">
  <ManufacturerData>
    <Manufacturer>
      <ApplicationPrograms>
        <ApplicationProgram Id="{app_id}" Name="{name}">
          <Static>
            <ComObjectTable />
            <Parameters />
          </Static>
        </ApplicationProgram>
      </ApplicationPrograms>
    </Manufacturer>
  </ManufacturerData>
</KNX>"""
    return xml.encode("utf-8")


def add_demo_templates(db: CatalogDatabase) -> int:
    added = 0
    for tmpl in DEMO_TEMPLATES:
        existing = (
            db.session.query(ApplicationModel)
            .filter_by(application_id=tmpl["application_id"])
            .first()
        )
        if existing:
            continue

        app = ApplicationModel(
            manufacturer_id=tmpl["manufacturer_id"],
            application_id=tmpl["application_id"],
            name=tmpl["name"],
            xml_data=make_fake_xml(tmpl["application_id"], tmpl["name"]),
            created_at=datetime.now(UTC),
        )
        db.session.add(app)
        added += 1
        print(f"    Added demo: {tmpl['name']}")

    if added:
        db.session.commit()
    return added


def generate_catalog(catalog_path: Path, knxprod_paths: list[Path]) -> None:
    if catalog_path.exists():
        print(f"Opening existing catalog: {catalog_path}")
        db = CatalogDatabase(catalog_path)
        db.open()
    else:
        print(f"Creating new catalog: {catalog_path}")
        db = CatalogDatabase(catalog_path)
        db.create()

    total_added = 0

    print("Adding demo templates...")
    total_added += add_demo_templates(db)

    for knxprod_path in knxprod_paths:
        if not knxprod_path.exists():
            print(f"  Skipping (not found): {knxprod_path}")
            continue

        print(f"  Loading: {knxprod_path}")
        try:
            added = load_knxprod_to_catalog(db, knxprod_path)
            if added:
                print(f"    Added {len(added)} application(s)")
                for app_id in added:
                    print(f"      - {app_id}")
                total_added += len(added)
            else:
                print("    No new applications (already in catalog)")
        except Exception as e:
            print(f"    Error: {e}")

    db.close()
    print(f"\nCatalog updated: {total_added} application(s) added")
    print(f"Saved to: {catalog_path}")


def main() -> None:
    catalog_path = Path(__file__).parent.parent.parent.parent / "demo.xknxcatalog"

    knxprod_paths: list[Path] = []
    if len(sys.argv) > 1:
        knxprod_paths = [Path(p) for p in sys.argv[1:]]

    generate_catalog(catalog_path, knxprod_paths)


if __name__ == "__main__":
    main()
