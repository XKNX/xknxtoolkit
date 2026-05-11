from dataclasses import dataclass, field

from knx_gui.templates import DEVICE_TEMPLATES
from knx_gui.types import ComObject, Device, DeviceTemplate, Telegram


@dataclass
class AppState:
    devices: list[Device] = field(default_factory=list)
    links: list[tuple[int, int, int]] = field(default_factory=list)
    telegrams: list[Telegram] = field(default_factory=list)
    connected: bool = False
    controller_ip: str = "192.168.1.1"
    selected_device: Device | None = None
    _next_link_id: int = 1000
    _next_device_id: int = 10

    def add_link(self, start_pin: int, end_pin: int) -> int:
        link_id = self._next_link_id
        self._next_link_id += 1
        self.links.append((link_id, start_pin, end_pin))
        return link_id

    def remove_link(self, link_id: int) -> None:
        self.links = [link for link in self.links if link[0] != link_id]

    def add_device(self, template: DeviceTemplate, address: str = "") -> Device:
        device = Device(
            node_id=self._next_device_id,
            name=template.name,
            template=template,
            address=address,
        )
        self._next_device_id += 1
        self.devices.append(device)
        return device

    def find_device_by_address(self, address: str) -> Device | None:
        for device in self.devices:
            if device.address == address:
                return device
        return None

    def find_device_by_node_id(self, node_id: int) -> Device | None:
        for device in self.devices:
            if device.node_id == node_id:
                return device
        return None

    def check_param_change_hides_com_objects(
        self, device: Device, param_id: str, value: str
    ) -> list[ComObject]:
        return device.would_hide_com_objects(param_id, value)


def create_sample_state() -> AppState:
    state = AppState()
    state.devices = [
        Device(1, "Living Room Light", DEVICE_TEMPLATES["switch_actuator"], "1.1.1"),
        Device(2, "Kitchen Dimmer", DEVICE_TEMPLATES["dimmer_actuator"], "1.1.2"),
        Device(3, "Bedroom Temp", DEVICE_TEMPLATES["temperature_sensor"], "1.1.3"),
        Device(4, "Entry Button", DEVICE_TEMPLATES["push_button"], "1.2.1"),
        Device(5, "Living Room Thermo", DEVICE_TEMPLATES["thermostat"], "1.2.2"),
        Device(6, "RGB Strip", DEVICE_TEMPLATES["rgb_controller"], "2.1.1"),
        Device(7, "Bedroom Blinds", DEVICE_TEMPLATES["blinds_actuator"], "1.2.3"),
        Device(8, "Shutter Button", DEVICE_TEMPLATES["shutter_button"], "1.2.4"),
        Device(9, "Logic AND", DEVICE_TEMPLATES["logic_gate"], "1.3.1"),
    ]
    state._next_device_id = 10
    state.telegrams = [
        Telegram("12:34:01.123", "1.1.1", "1/0/1", "GroupValueWrite", "1.001", "On"),
        Telegram(
            "12:34:01.456", "1.1.1", "1/0/2", "GroupValueResponse", "1.001", "Off"
        ),
        Telegram("12:34:02.001", "1.2.1", "2/0/1", "GroupValueWrite", "5.001", "75%"),
        Telegram(
            "12:34:02.345", "1.1.3", "3/0/1", "GroupValueWrite", "9.001", "21.5°C"
        ),
        Telegram("12:34:03.012", "1.2.2", "4/0/1", "GroupValueRead", "1.001", ""),
        Telegram("12:34:03.234", "1.2.2", "4/0/1", "GroupValueResponse", "1.001", "On"),
        Telegram(
            "12:34:04.567", "2.1.1", "5/0/1", "GroupValueWrite", "232.600", "#FF8800"
        ),
        Telegram("12:34:05.123", "1.1.2", "1/1/1", "GroupValueWrite", "3.007", "Up"),
    ]
    return state
