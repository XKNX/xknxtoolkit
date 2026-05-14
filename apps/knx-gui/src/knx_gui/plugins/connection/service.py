from collections.abc import Callable


class ConnectionService:
    def __init__(self) -> None:
        self._raw_cemi_listeners: list[Callable[[bytes], None]] = []
        self._connected_listeners: list[Callable[[], None]] = []

    def add_raw_cemi_listener(self, callback: Callable[[bytes], None]) -> None:
        self._raw_cemi_listeners.append(callback)

    def add_connected_listener(self, callback: Callable[[], None]) -> None:
        self._connected_listeners.append(callback)

    def dispatch_raw_cemi(self, raw_cemi: bytes) -> None:
        for cb in self._raw_cemi_listeners:
            cb(raw_cemi)

    def dispatch_connected(self) -> None:
        for cb in self._connected_listeners:
            cb()
