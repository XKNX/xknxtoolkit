"""Generate the demo.xknx project file using devices from the catalog."""

from dataclasses import dataclass
from pathlib import Path

from knx_gui.knxprod import parse_application_xml
from knx_gui.plugins.catalog.db import (
    ApplicationModel,
    CatalogDatabase,
    get_application_xml,
)
from knx_gui.plugins.project.db import DeviceAdded, ProjectDatabase


@dataclass
class DemoDevice:
    template_id: str
    name: str
    individual_address: str


DEMO_DEVICES = [
    DemoDevice("M-0083_A-0009-21-FB5C", "Switch Actuator 4x", "1.1.1"),
    DemoDevice("M-0083_A-013F-31-1DDA", "Dimming Actuator 2x", "1.1.2"),
    DemoDevice("M-0083_A-0020-15-7F81", "Push Button 2-fold", "1.1.3"),
    DemoDevice("M-0083_A-004D-13-2B44", "Weather Station", "1.1.4"),
    DemoDevice("M-0083_A-0112-10-2897", "Energy Meter", "1.1.5"),
]


def generate_demo(output_path: Path, catalog_path: Path) -> None:
    if output_path.exists():
        output_path.unlink()

    catalog = CatalogDatabase(catalog_path)
    if not catalog_path.exists():
        print(f"Error: catalog not found at {catalog_path}")
        print("Run 'uv run generate-catalog' first")
        return
    catalog.open()

    db = ProjectDatabase(output_path)
    db.create()

    for demo_device in DEMO_DEVICES:
        xml_data = get_application_xml(catalog, demo_device.template_id)
        if not xml_data:
            print(f"Warning: {demo_device.template_id} not in catalog, skipping")
            continue

        app_model = (
            catalog.session.query(ApplicationModel)
            .filter_by(application_id=demo_device.template_id)
            .first()
        )
        if not app_model:
            continue

        apps = parse_application_xml(xml_data, app_model.manufacturer_id)
        if not apps:
            print(f"Warning: failed to parse {demo_device.template_id}, skipping")
            continue

        app = apps[0]
        params = [(p.id, p.value) for p in app.parameters]
        com_objs = []
        for co in app.com_objects:
            dpt_major, dpt_minor = 0, 0
            if co.dpt_codes:
                parts = co.dpt_codes[0].split(".")
                dpt_major = int(parts[0]) if len(parts) > 0 else 0
                dpt_minor = int(parts[1]) if len(parts) > 1 else 0
            com_objs.append(
                {
                    "co_id": co.id,
                    "dpt_major": dpt_major,
                    "dpt_minor": dpt_minor,
                    "flag_communication": co.flags.communication,
                    "flag_read": co.flags.read,
                    "flag_write": co.flags.write,
                    "flag_transmit": co.flags.transmit,
                    "flag_update": co.flags.update,
                }
            )

        event = DeviceAdded(
            device_id=0,
            individual_address=demo_device.individual_address,
            template_id=demo_device.template_id,
            name=demo_device.name,
            parameters=params,
            com_objects=com_objs,
        )
        db.event_store.append(event)
        print(
            f"Added: {demo_device.name} ({len(app.com_objects)} total, {len(app.visible_com_objects())} visible)"
        )

    catalog.close()
    db.close()
    print(f"\nDemo project saved to: {output_path}")


def main() -> None:
    base_path = Path(__file__).parent.parent.parent.parent
    output_path = base_path / "demo.xknx"
    catalog_path = base_path / "demo.xknxcatalog"
    generate_demo(output_path, catalog_path)


if __name__ == "__main__":
    main()
