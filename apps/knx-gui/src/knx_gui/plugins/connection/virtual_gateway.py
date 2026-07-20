from __future__ import annotations

import asyncio
import contextlib
import socket
import threading
from enum import Enum
from typing import Any

from xknx.io import util
from xknx.knxip import (
    HPAI,
    DescriptionResponse,
    DIBDeviceInformation,
    DIBSuppSVCFamilies,
    KNXIPHeader,
    SearchResponse,
    SearchResponseExtended,
)
from xknx.knxip.knxip_enum import DIBServiceFamily, KNXIPServiceType
from xknx.telegram.address import IndividualAddress

_MCAST_GROUP = "224.0.23.12"
_SEARCH_REQUEST_SERVICE_TYPE = 0x0201
_SEARCH_REQUEST_EXTENDED_SERVICE_TYPE = 0x020B
_DESCRIPTION_REQUEST_SERVICE_TYPE = 0x0203
_KNXIP_HEADER_LENGTH = 6


class VirtualGatewayState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class _KNXIPResponder(asyncio.DatagramProtocol):
    def __init__(self, local_ip: str, port: int, name: str, logger: Any = None) -> None:
        self._local_ip = local_ip
        self._port = port
        self._name = name
        self._logger = logger
        self._transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self._transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:  # type: ignore[override]
        if len(data) < _KNXIP_HEADER_LENGTH or self._transport is None:
            return
        service_type = (data[2] << 8) | data[3]
        if service_type == _SEARCH_REQUEST_SERVICE_TYPE:
            resp = self._build_search_response()
            if self._logger:
                self._logger.info("search request", from_addr=f"{addr[0]}:{addr[1]}")
            self._send(resp, addr)
            if self._logger:
                self._logger.info("search response", to_addr=f"{addr[0]}:{addr[1]}", length=len(resp))
        elif service_type == _SEARCH_REQUEST_EXTENDED_SERVICE_TYPE:
            resp = self._build_search_response_extended()
            if self._logger:
                self._logger.info("search request extended", from_addr=f"{addr[0]}:{addr[1]}")
            self._send(resp, addr)
            if self._logger:
                self._logger.info("search response extended", to_addr=f"{addr[0]}:{addr[1]}", length=len(resp))
        elif service_type == _DESCRIPTION_REQUEST_SERVICE_TYPE:
            resp = self._build_description_response()
            if self._logger:
                self._logger.info("description request", from_addr=f"{addr[0]}:{addr[1]}")
            self._send(resp, addr)
            if self._logger:
                self._logger.info("description response", to_addr=f"{addr[0]}:{addr[1]}", length=len(resp))

    def _send(self, data: bytes, addr: tuple[str, int]) -> None:
        if self._transport is not None:
            self._transport.sendto(data, addr)

    def connection_lost(self, exc: Exception | None) -> None:
        pass

    def _dibs(self) -> list[DIBDeviceInformation | DIBSuppSVCFamilies]:
        dib_dev = DIBDeviceInformation()
        dib_dev.name = self._name
        dib_dev.multicast_address = _MCAST_GROUP
        dib_dev.individual_address = IndividualAddress("1.1.0")
        dib_dev.serial_number = "00:00:00:00:00:01"
        dib_dev.mac_address = "00:00:00:00:00:01"

        dib_svc = DIBSuppSVCFamilies()
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.CORE, 2))
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.TUNNELING, 2))
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.ROUTING, 1))
        return [dib_dev, dib_svc]

    def _build_search_response(self) -> bytes:
        body = SearchResponse(control_endpoint=HPAI(self._local_ip, self._port))
        body.dibs = self._dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.SEARCH_RESPONSE
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def _build_search_response_extended(self) -> bytes:
        body = SearchResponseExtended(control_endpoint=HPAI(self._local_ip, self._port))
        body.dibs = self._dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.SEARCH_RESPONSE_EXTENDED
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def _build_description_response(self) -> bytes:
        body = DescriptionResponse()
        body.dibs = self._dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.DESCRIPTION_RESPONSE
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def error_received(self, exc: Exception) -> None:
        if self._logger:
            self._logger.error("udp error", error=str(exc))


class VirtualGateway:
    """Minimal KNX/IP virtual gateway: responds to SEARCH_REQUEST and DESCRIPTION_REQUEST."""

    DEFAULT_PORT = 3671

    def __init__(self, name: str = "xknxtoolkit virtual gateway", port: int = DEFAULT_PORT, logger: Any = None) -> None:
        self._name = name
        self._port = port
        self._logger = logger
        self._state = VirtualGatewayState.STOPPED
        self._error: str | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._udp_transport: asyncio.DatagramTransport | None = None

    @property
    def state(self) -> VirtualGatewayState:
        return self._state

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def running(self) -> bool:
        return self._state == VirtualGatewayState.RUNNING

    def start(self) -> None:
        if self._state in (VirtualGatewayState.STARTING, VirtualGatewayState.RUNNING):
            return
        self._state = VirtualGatewayState.STARTING
        self._error = None

        loop_ready = threading.Event()

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            loop_ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run, daemon=True, name="KNX-VGW")
        self._thread.start()
        loop_ready.wait()
        assert self._loop is not None
        asyncio.run_coroutine_threadsafe(self._start_async(), self._loop)

    async def _start_async(self) -> None:
        try:
            local_ip = await util.get_default_local_ip(_MCAST_GROUP)
            if local_ip is None:
                raise RuntimeError("Could not determine local IP")
            if self._logger:
                self._logger.info("resolved interface", local_ip=local_ip)

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            with contextlib.suppress(AttributeError):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind(("", self._port))
            mreq = socket.inet_aton(_MCAST_GROUP) + socket.inet_aton(local_ip)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            loop = asyncio.get_running_loop()
            transport, _ = await loop.create_datagram_endpoint(
                lambda: _KNXIPResponder(local_ip, self._port, self._name, self._logger),
                sock=sock,
            )
            self._udp_transport = transport  # type: ignore[assignment]
            self._state = VirtualGatewayState.RUNNING
            if self._logger:
                self._logger.info("virtual gateway running", local_ip=local_ip, port=self._port)
        except Exception as e:
            self._state = VirtualGatewayState.ERROR
            self._error = str(e)
            if self._logger:
                self._logger.error("virtual gateway failed to start", error=str(e))

    def stop(self) -> None:
        if self._state == VirtualGatewayState.STOPPED:
            return
        if self._loop is not None:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self._loop)
        else:
            self._state = VirtualGatewayState.STOPPED

    async def _stop_async(self) -> None:
        try:
            if self._udp_transport is not None:
                self._udp_transport.close()
                self._udp_transport = None
        finally:
            self._state = VirtualGatewayState.STOPPED
            if self._logger:
                self._logger.info("virtual gateway stopped")
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None
