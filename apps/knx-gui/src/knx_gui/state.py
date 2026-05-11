from dataclasses import dataclass, field

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

    def add_device_with_id(
        self, template: DeviceTemplate, node_id: int, address: str = ""
    ) -> Device:
        device = Device(
            node_id=node_id,
            name=template.name,
            template=template,
            address=address,
        )
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


def create_empty_state() -> AppState:
    return AppState()
