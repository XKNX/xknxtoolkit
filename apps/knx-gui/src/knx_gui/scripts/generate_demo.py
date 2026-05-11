"""Generate the demo.xknx project file."""

from dataclasses import dataclass
from pathlib import Path

from knx_gui.project.database import ProjectDatabase
from knx_gui.project.events import DeviceAdded, LinkCreated


@dataclass
class DemoDevice:
    device_id: int
    template_id: str
    name: str
    address: str


@dataclass
class DemoLink:
    link_id: int
    start_pin: int
    end_pin: int


DEMO_DEVICES = [
    DemoDevice(1, "switch_actuator", "Living Room Light", "1.1.1"),
    DemoDevice(2, "dimmer_actuator", "Kitchen Dimmer", "1.1.2"),
    DemoDevice(3, "temperature_sensor", "Bedroom Temp", "1.1.3"),
    DemoDevice(4, "push_button", "Entry Button", "1.2.1"),
    DemoDevice(5, "thermostat", "Living Room Thermo", "1.2.2"),
    DemoDevice(6, "rgb_controller", "RGB Strip", "2.1.1"),
    DemoDevice(7, "blinds_actuator", "Bedroom Blinds", "1.2.3"),
    DemoDevice(8, "shutter_button", "Shutter Button", "1.2.4"),
    DemoDevice(9, "logic_gate", "Logic AND", "1.3.1"),
]

DEMO_LINKS = [
    DemoLink(1, 100001, 100002),
    DemoLink(2, 100003, 100004),
]


def generate_demo(output_path: Path) -> None:
    from knx_gui.templates import DEVICE_TEMPLATES

    if output_path.exists():
        output_path.unlink()

    db = ProjectDatabase(output_path)
    db.create()

    for device in DEMO_DEVICES:
        template = DEVICE_TEMPLATES.get(device.template_id)
        if not template:
            print(f"Warning: template {device.template_id} not found, skipping")
            continue

        params = [(p.id, p.value) for p in template.parameters]
        com_objs = [
            {
                "co_id": co.id,
                "dpt_major": co.dpt.major,
                "dpt_minor": co.dpt.minor,
                "flag_communication": co.flags.communication,
                "flag_read": co.flags.read,
                "flag_write": co.flags.write,
                "flag_transmit": co.flags.transmit,
                "flag_update": co.flags.update,
            }
            for co in template.com_objects
        ]

        event = DeviceAdded(
            device_id=device.device_id,
            address=device.address,
            template_id=device.template_id,
            name=device.name,
            parameters=params,
            com_objects=com_objs,
        )
        db.event_store.append(event)
        print(f"Added device: {device.name} ({device.template_id})")

    for link in DEMO_LINKS:
        event = LinkCreated(
            link_id=link.link_id,
            start_pin=link.start_pin,
            end_pin=link.end_pin,
        )
        db.event_store.append(event)
        print(f"Added link: {link.link_id}")

    db.close()
    print(f"\nDemo project saved to: {output_path}")


def main() -> None:
    output_path = Path(__file__).parent.parent.parent.parent / "demo.xknx"
    generate_demo(output_path)


if __name__ == "__main__":
    main()
