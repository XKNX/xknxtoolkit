from collections import defaultdict
from collections.abc import Callable
from typing import Any

from knx_gui.knxprod import DeviceApplication
from knx_gui.types import ComObject, Device


class AppState:
    def __init__(self) -> None:
        self.devices: list[Device] = []
        self.links: list[tuple[int, int, int]] = []
        self._selected_device: Device | None = None
        self._next_link_id: int = 1000
        self._next_device_id: int = 10
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable[..., Any]) -> Callable[[], None]:
        self._listeners[event].append(callback)
        return lambda: self._listeners[event].remove(callback)

    def _emit(self, event: str, *args: Any) -> None:
        for callback in self._listeners[event]:
            callback(*args)

    @property
    def selected_device(self) -> Device | None:
        return self._selected_device

    @selected_device.setter
    def selected_device(self, device: Device | None) -> None:
        if self._selected_device != device:
            self._selected_device = device
            self._emit("device_selected", device)

    def set_flag(self, device: Device, co_id: str, flag_name: str, new_value: bool) -> None:
        com_object = device.find_com_object(co_id)
        if not com_object:
            return
        old_value = getattr(com_object.flags, flag_name)
        if old_value != new_value:
            setattr(com_object.flags, flag_name, new_value)
            self._emit("flag_changed", device, co_id, flag_name, old_value, new_value)

    def request_reload(self) -> None:
        self._emit("reload_requested")

    def set_param(self, device: Device, param_id: str, new_value: str) -> None:
        old_value = device._param_values.get(param_id, "")
        if old_value != new_value:
            device.set_param_value(param_id, new_value)
            self._emit("param_changed", device, param_id, old_value, new_value)

    def add_device(self, app: DeviceApplication, address: str = "") -> Device:
        device = Device(
            node_id=self._next_device_id,
            name=app.name,
            app=app,
            address=address,
        )
        self._next_device_id += 1
        self.devices.append(device)
        return device

    def add_device_with_id(
        self, app: DeviceApplication, node_id: int, address: str = ""
    ) -> Device:
        device = Device(
            node_id=node_id,
            name=app.name,
            app=app,
            address=address,
        )
        self.devices.append(device)
        return device

    def add_link(self, start_pin: int, end_pin: int) -> int:
        link_id = self._next_link_id
        self._next_link_id += 1
        self.links.append((link_id, start_pin, end_pin))
        self._emit("link_added", link_id, start_pin, end_pin)
        return link_id

    def remove_link(self, link_id: int) -> None:
        link_data = next((link for link in self.links if link[0] == link_id), None)
        self.links = [link for link in self.links if link[0] != link_id]
        if link_data:
            self._emit("link_removed", link_data[0], link_data[1], link_data[2])

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
