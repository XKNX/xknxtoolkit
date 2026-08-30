from __future__ import annotations

import asyncio
import functools
import threading
import time
from collections.abc import Callable, Coroutine
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any

from xknx.cemi import CEMIFrame
from xknx.exceptions import ManagementConnectionError
from xknx.management.procedures import (
    nm_individual_address_read,
    nm_individual_address_serial_number_write,
    nm_individual_address_write,
)

if TYPE_CHECKING:
    from xknx import XKNX

    from knx_gui.device import Device
    from knx_gui.net import TelegramSource
    from knx_gui.plugins.base import Logger
    from xknxmono.download.image import GroupCommunication
    from xknxmono.download.scope import DownloadScope


class ConnectionService:
    def __init__(self) -> None:
        self._log: Logger
        self._raw_cemi_listeners: list[Callable[[bytes, TelegramSource], None]] = []
        self._connected_listeners: list[Callable[[], None]] = []
        self._xknx: XKNX | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        # Current point-to-point bus operation, so the UI can show an ETS-like
        # "programming/testing in progress" indicator. Set/cleared from worker threads.
        self._busy_lock = threading.Lock()
        self._busy: tuple[str, str] | None = None
        self._busy_progress: tuple[int, int] | None = None
        self._program_notice: tuple[bool, float] | None = None
        # Timestamp of the last connection-requiring call made while disconnected,
        # so the status bar can show a brief "no connection" notice.
        self._not_connected_notice: float | None = None

    @property
    def busy_operation(self) -> tuple[str, str] | None:
        """``(kind, address)`` of the running bus op (``kind`` is ``program``/``test``), or ``None``."""
        with self._busy_lock:
            return self._busy

    @property
    def busy_progress(self) -> tuple[int, int] | None:
        """``(done, total)`` load-control progress of the running download, or ``None``."""
        with self._busy_lock:
            return self._busy_progress

    def _set_busy(self, kind: str, address: str) -> None:
        with self._busy_lock:
            self._busy = (kind, address)
            self._busy_progress = None

    def _clear_busy(self) -> None:
        with self._busy_lock:
            self._busy = None
            self._busy_progress = None

    def _on_program_progress(self, done: int, total: int) -> None:
        with self._busy_lock:
            self._busy_progress = (done, total)

    def set_logger(self, log: Logger) -> None:
        self._log = log

    def not_connected(self, op: str) -> bool:
        """Guard for every connection-requiring call: log + a status-bar notice if no KNX link.

        Returns ``True`` when there is no connection (the caller must abort)."""
        if self._xknx is not None:
            return False
        self._log.error(f"{op} failed: no KNX connection")
        with self._busy_lock:
            self._not_connected_notice = time.monotonic()
        return True

    def not_connected_notice(self, max_age: float = 6.0) -> bool:
        """Whether a recent call was refused for lack of a connection (for the status bar)."""
        with self._busy_lock:
            stamp = self._not_connected_notice
        return (
            stamp is not None
            and self._xknx is None
            and time.monotonic() - stamp <= max_age
        )

    def add_raw_cemi_listener(
        self, callback: Callable[[bytes, TelegramSource], None]
    ) -> None:
        self._raw_cemi_listeners.append(callback)

    def add_connected_listener(self, callback: Callable[[], None]) -> None:
        self._connected_listeners.append(callback)

    def dispatch_raw_cemi(self, raw_cemi: bytes) -> None:
        from knx_gui.net import TelegramSource

        self._dispatch_cemi(raw_cemi, TelegramSource.CONNECTION)

    def dispatch_proxy_cemi(self, raw_cemi: bytes) -> None:
        from knx_gui.net import TelegramSource

        self._dispatch_cemi(raw_cemi, TelegramSource.PROXY)

    def dispatch_virtual_cemi(self, raw_cemi: bytes) -> None:
        from knx_gui.net import TelegramSource

        self._dispatch_cemi(raw_cemi, TelegramSource.VIRTUAL)

    def _dispatch_cemi(self, raw_cemi: bytes, source: TelegramSource) -> None:
        for cb in self._raw_cemi_listeners:
            cb(raw_cemi, source)

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
        if self.not_connected("send_cemi"):
            return None
        self._log.debug("send_cemi", hex=raw_cemi.hex(" "))
        try:
            cemi = CEMIFrame.from_knx(raw_cemi)
        except Exception as e:
            # xknx's send_cemi() always re-serializes via cemi.to_knx()
            # rather than sending raw_cemi verbatim, so a frame we can't
            # even parse can't currently be delivered at all - dropped
            # here instead of crashing the caller (an unparseable CEMI
            # from a real client used to take the whole TCP connection
            # down with it).
            self._log.error(
                "send_cemi: could not parse CEMI, not delivered",
                error=str(e),
                hex=raw_cemi.hex(" "),
            )
            return None
        reencoded = cemi.to_knx()
        if reencoded != raw_cemi:
            self._log.error(
                "send_cemi: cemi round-trip mismatch, delivering reencoded form",
                original=raw_cemi.hex(" "),
                reencoded=reencoded.hex(" "),
            )
        future = self.run_async(self._xknx.knxip_interface.send_cemi(cemi))
        if future is not None:
            future.add_done_callback(self._log_send_cemi_result)
        return future

    def _log_send_cemi_result(self, future: Future[Any]) -> None:
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._log.error("send_cemi failed", error=str(exc))
        else:
            self._log.debug("send_cemi ok")

    def read_programming_mode_devices(self, timeout: float = 3.0) -> Future[Any] | None:
        if self.not_connected("read_programming_mode_devices"):
            return None
        return self.run_async(nm_individual_address_read(self._xknx, timeout=timeout))

    def assign_individual_address_by_serial(
        self, serial: bytes, address: str
    ) -> Future[Any] | None:
        if self.not_connected("assign_individual_address_by_serial"):
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
        if self.not_connected("assign_individual_address"):
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

    def program_device(
        self,
        device: Device,
        scope: DownloadScope | None = None,
        group_communication: GroupCommunication | None = None,
    ) -> Future[Any] | None:
        """Download the device's configured application/parameters onto the bus.

        ``scope`` selects a full or partial download (defaults to full).
        ``group_communication`` supplies the address/association tables.
        """
        if self.not_connected("program_device"):
            return None
        if not device.individual_address:
            self._log.warning("Device has no individual address", device=device.name)
            return None
        from knx_gui.programming import download_device
        from xknxmono.download.scope import DownloadScope

        scope = scope or DownloadScope.FULL
        self._log.info(
            "Programming device",
            device=device.name,
            address=device.individual_address,
            scope=scope.name,
        )
        self._set_busy("program", device.individual_address)
        future = self.run_async(
            download_device(
                self._xknx,
                device,
                scope,
                group_communication,
                progress=self._on_program_progress,
            )
        )
        if future is not None:
            future.add_done_callback(self._log_program_result)
        else:
            self._clear_busy()
        return future

    def _log_program_result(self, future: Future[Any]) -> None:
        self._clear_busy()
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._log.error("Programming failed", error=str(exc))
            self._set_program_notice(False)
        else:
            self._log.info("Programming complete")
            self._set_program_notice(True)

    def _set_program_notice(self, ok: bool) -> None:
        with self._busy_lock:
            self._program_notice = (ok, time.monotonic())

    def program_notice(self, max_age: float = 6.0) -> bool | None:
        """Recent programming outcome (``True`` ok, ``False`` failed) within ``max_age`` s, else ``None``."""
        with self._busy_lock:
            notice = self._program_notice
        if notice is None or time.monotonic() - notice[1] > max_age:
            return None
        return notice[0]

    def evaluate_device(
        self,
        device: Device,
        scope: DownloadScope | None = None,
        group_communication: GroupCommunication | None = None,
    ) -> Future[Any] | None:
        """Dry run: read the device and log what programming it would change."""
        if self.not_connected("evaluate_device"):
            return None
        if not device.individual_address:
            self._log.warning("Device has no individual address", device=device.name)
            return None
        from knx_gui.programming import eval_device
        from xknxmono.download.scope import DownloadScope

        scope = scope or DownloadScope.FULL
        self._log.info(
            "Testing device before programming", device=device.name, scope=scope.name
        )
        self._set_busy("test", device.individual_address)
        future = self.run_async(
            eval_device(self._xknx, device, scope, group_communication)
        )
        if future is not None:
            future.add_done_callback(
                functools.partial(
                    self._log_evaluate_result, address=device.individual_address
                )
            )
        else:
            self._clear_busy()
        return future

    def _log_evaluate_result(
        self, future: Future[Any], address: str | None = None
    ) -> None:
        self._clear_busy()
        if future.cancelled():
            return
        exc = future.exception()
        if exc is not None:
            self._log.error("Evaluation failed", address=address, error=str(exc))
            if isinstance(exc, ManagementConnectionError):
                # A dry run still reads the live device over a point-to-point connection.
                # No ACK means nothing answered at that individual address on the bus.
                self._log.error(
                    "Device did not respond on the bus — check it is powered and "
                    "reachable from this interface (line/coupler) at the address",
                    address=address,
                )
            return
        report = future.result()
        self._log.info(
            "Pre-flight result",
            changed_bytes=report.total_changed_bytes,
            segments=len(report.changed_segments),
            properties=len(report.changed_properties),
        )
        for line in report.summary().splitlines():
            self._log.info(line.strip())

    def run_async(self, coro: Coroutine[Any, Any, Any]) -> Future[Any] | None:
        if self._loop is None:
            coro.close()
            return None
        return asyncio.run_coroutine_threadsafe(coro, self._loop)
