from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any

from xknx.cemi import CEMIFrame
from xknx.management.procedures import (
    nm_individual_address_read,
    nm_individual_address_serial_number_write,
    nm_individual_address_write,
)

if TYPE_CHECKING:
    from xknx import XKNX

    from knx_gui.plugins.base import Logger
    from knx_gui.types import Device


class ConnectionService:
    def __init__(self) -> None:
        self._log: Logger
        self._raw_cemi_listeners: list[Callable[[bytes], None]] = []
        self._connected_listeners: list[Callable[[], None]] = []
        self._xknx: XKNX | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_logger(self, log: Logger) -> None:
        self._log = log

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

    def set_connection(
        self,
        xknx: XKNX | None,
        loop: asyncio.AbstractEventLoop | None,
    ) -> None:
        self._xknx = xknx
        self._loop = loop

    @property
    def xknx(self) -> XKNX | None:
        return self._xknx

    def send_cemi(self, raw_cemi: bytes) -> Future[Any] | None:
        if self._xknx is None:
            return None
        cemi = CEMIFrame.from_knx(raw_cemi)
        return self.run_async(self._xknx.knxip_interface.send_cemi(cemi))

    def read_programming_mode_devices(self, timeout: float = 3.0) -> Future[Any] | None:
        if self._xknx is None:
            self._log.warning("read_programming_mode_devices called while disconnected")
            return None
        return self.run_async(nm_individual_address_read(self._xknx, timeout=timeout))

    def assign_individual_address_by_serial(
        self, serial: bytes, address: str
    ) -> Future[Any] | None:
        if self._xknx is None:
            self._log.warning(
                "assign_individual_address_by_serial called while disconnected"
            )
            return None
        self._log.debug(
            "Assigning individual address by serial",
            address=address,
            serial=serial.hex(),
        )
        return self.run_async(
            nm_individual_address_serial_number_write(self._xknx, serial, address)
        )

    def assign_individual_address(self, address: str) -> Future[Any] | None:
        if self._xknx is None:
            self._log.warning("assign_individual_address called while disconnected")
            return None
        self._log.debug("Assigning individual address", address=address)
        return self.run_async(nm_individual_address_write(self._xknx, address))

    def assign_individual_address_for_device(
        self, device: Device
    ) -> Future[Any] | None:
        if not device.individual_address:
            self._log.warning(
                "Device has no individual address assigned", device=device.name
            )
            return None
        return self.assign_individual_address(device.individual_address)

    def run_async(self, coro: Coroutine[Any, Any, Any]) -> Future[Any] | None:
        if self._loop is None:
            coro.close()
            return None
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
