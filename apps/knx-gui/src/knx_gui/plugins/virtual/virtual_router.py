from __future__ import annotations

import asyncio
import contextlib
import socket
import threading
from collections.abc import Callable
from enum import Enum
from typing import Any

from xknx import XKNX
from xknx.cemi import CEMIFrame
from xknx.io import util
from xknx.io.routing import Routing
from xknx.knxip import DIB, DIBDeviceInformation, DIBSuppSVCFamilies
from xknx.knxip.knxip_enum import DIBServiceFamily
from xknx.telegram.address import IndividualAddress

from knx_gui.knxip_discovery import KNXIPDiscoveryResponder
from knx_gui.knxip_tunnelling_gateway import TunnellingGateway


class VirtualRouterState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class VirtualRouter:
    """
    Minimal KNX/IP virtual network: a router (routing over multicast) and
    a point-to-point gateway (TCP tunnelling, via the shared
    `TunnellingGateway`), both fronting the same virtual bus - like a real
    hybrid interface that offers ROUTING and TUNNELING side by side, a
    client can reach it either way.

    This runs multiple sockets rather than one, and that's deliberate:
    `xknx.io.routing.Routing` (used below for L_Data) only parses
    RoutingIndication/RoutingBusy/RoutingLostMessage frames - anything
    else, including SEARCH_REQUEST/DESCRIPTION_REQUEST, is logged as
    "not implemented" and dropped. Its transport does expose
    `register_callback()` for other service types, but its `send()`
    forces every send to the multicast group whenever the transport is
    in multicast mode (which it always is here) - it will not unicast a
    reply to a specific address. That's a real requirement for
    discovery, not a style choice: SEARCH_REQUEST/DESCRIPTION_REQUEST
    arrive via multicast (any server might answer), but
    SEARCH_RESPONSE/DESCRIPTION_RESPONSE must go back via unicast to
    only the requester - otherwise every other client doing discovery
    on the network would receive replies meant for someone else.
    Reaching past `send()` into the transport's internals to force a
    unicast send would work, but couples us to an xknx implementation
    detail that isn't a supported extension point for this. Running our
    own small `KNXIPDiscoveryResponder` socket for discovery, alongside
    `Routing`'s own socket for L_Data, keeps both correct without that
    coupling - `SO_REUSEPORT` lets both bind the same multicast
    group/port without conflict (verified: both reach RUNNING
    simultaneously).

    The embedded `TunnellingGateway` runs with `enable_discovery=False`
    and shares our own event loop (`start_on_loop`/`stop_on_loop`)
    instead of spinning up a separate thread - our discovery responder's
    `_dibs()` already advertises both ROUTING and TUNNELING, so having
    the gateway run its own discovery too would answer every
    SEARCH_REQUEST twice with two conflicting, single-family DIB sets.
    """

    DEFAULT_PORT = 3671
    DEFAULT_MCAST_GROUP = "224.0.23.12"

    def __init__(
        self,
        name: str = "xknxtoolkit virtual router",
        port: int = DEFAULT_PORT,
        multicast_group: str = DEFAULT_MCAST_GROUP,
        individual_address: str = "1.1.0",
        client_individual_address: str = TunnellingGateway.DEFAULT_CLIENT_INDIVIDUAL_ADDRESS,
        serial_number: str = "00:00:00:00:00:01",
        mac_address: str = "00:00:00:00:00:01",
        on_cemi: Callable[[bytes], None] | None = None,
        on_gateway_cemi: Callable[[bytes], None] | None = None,
        logger: Any = None,
    ) -> None:
        self._name = name
        self._port = port
        self._multicast_group = multicast_group
        self._individual_address = individual_address
        self._client_individual_address = client_individual_address
        self._serial_number = serial_number
        self._mac_address = mac_address
        self._on_cemi = on_cemi
        self._on_gateway_cemi = on_gateway_cemi
        self._logger = logger
        self._state = VirtualRouterState.STOPPED
        self._error: str | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._udp_transport: asyncio.DatagramTransport | None = None
        self._routing: Routing | None = None
        self._xknx: XKNX | None = None
        self._gateway: TunnellingGateway | None = None

    @property
    def state(self) -> VirtualRouterState:
        return self._state

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def running(self) -> bool:
        return self._state == VirtualRouterState.RUNNING

    @property
    def gateway_connected(self) -> bool:
        return self._gateway is not None and self._gateway.connected

    def _dibs(self) -> list[DIB]:
        dib_dev = DIBDeviceInformation()
        dib_dev.name = self._name
        dib_dev.multicast_address = self._multicast_group
        dib_dev.individual_address = IndividualAddress(self._individual_address)
        dib_dev.serial_number = self._serial_number
        dib_dev.mac_address = self._mac_address

        dib_svc = DIBSuppSVCFamilies()
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.CORE, 2))
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.ROUTING, 1))
        dib_svc.families.append(
            DIBSuppSVCFamilies.Family(DIBServiceFamily.TUNNELING, 2)
        )
        return [dib_dev, dib_svc]

    def start(self) -> None:
        if self._state in (VirtualRouterState.STARTING, VirtualRouterState.RUNNING):
            return
        self._state = VirtualRouterState.STARTING
        self._error = None

        loop_ready = threading.Event()

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            loop_ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(
            target=_run, daemon=True, name="KNX-VirtualRouter"
        )
        self._thread.start()
        loop_ready.wait()
        assert self._loop is not None
        asyncio.run_coroutine_threadsafe(self._start_async(), self._loop)

    async def _start_async(self) -> None:
        try:
            local_ip = await util.get_default_local_ip(self._multicast_group)
            if local_ip is None:
                raise RuntimeError("Could not determine local IP")
            if self._logger:
                self._logger.info("resolved interface", local_ip=local_ip)

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            with contextlib.suppress(AttributeError):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind(("", self._port))
            mreq = socket.inet_aton(self._multicast_group) + socket.inet_aton(local_ip)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            loop = asyncio.get_running_loop()
            transport, _ = await loop.create_datagram_endpoint(
                lambda: KNXIPDiscoveryResponder(
                    local_ip,
                    self._port,
                    get_dibs=self._dibs,
                    logger=self._logger,
                ),
                sock=sock,
            )
            self._udp_transport = transport  # type: ignore[assignment]

            self._xknx = XKNX()
            self._routing = Routing(
                self._xknx,
                individual_address=None,
                cemi_received_callback=self._on_cemi_received,
                local_ip=local_ip,
                multicast_group=self._multicast_group,
                multicast_port=self._port,
            )
            await self._routing.connect()

            self._gateway = TunnellingGateway(
                port=self._port,
                name=self._name,
                serial_number=self._serial_number,
                mac_address=self._mac_address,
                client_individual_address=self._client_individual_address,
                multicast_group=self._multicast_group,
                enable_discovery=False,
                on_cemi=self._on_gateway_cemi_received,
                logger=self._logger,
            )
            await self._gateway.start_on_loop(loop)

            self._state = VirtualRouterState.RUNNING
            if self._logger:
                self._logger.info("virtual router running", local_ip=local_ip, port=self._port)
        except Exception as e:
            self._state = VirtualRouterState.ERROR
            self._error = str(e)
            if self._logger:
                self._logger.error("virtual router failed to start", error=str(e))

    def _on_cemi_received(self, raw: bytes) -> None:
        # TODO: xknx.io.routing.Routing.send_cemi() feeds a locally
        # synthesized L_Data.con echo of every frame *we* send back
        # through this same callback (plus a possible second copy via
        # IP_MULTICAST_LOOP, which nothing here disables). Harmless
        # today - VirtualDevice.handle_cemi() only matches Read/Write
        # APCIs, so the echo of our own Response is silently ignored -
        # but it likely double/triple-counts our replies in the Network
        # tab. Consider filtering L_Data.con here, or de-duping frames
        # we just sent via send_cemi().
        if self._logger:
            self._logger.info("cemi received", hex=raw.hex(" "))
        if self._on_cemi is not None:
            self._on_cemi(raw)

    def _on_gateway_cemi_received(self, raw: bytes) -> None:
        if self._on_gateway_cemi is not None:
            self._on_gateway_cemi(raw)

    def send_cemi(self, cemi: CEMIFrame) -> None:
        if self._loop is None or self._routing is None:
            return
        asyncio.run_coroutine_threadsafe(self._routing.send_cemi(cemi), self._loop)

    def send_gateway_cemi(self, raw_cemi: bytes) -> None:
        if self._gateway is None:
            return
        self._gateway.send_cemi(raw_cemi)

    def stop(self) -> None:
        if self._state == VirtualRouterState.STOPPED:
            return
        if self._loop is not None:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self._loop)
        else:
            self._state = VirtualRouterState.STOPPED

    async def _stop_async(self) -> None:
        try:
            if self._udp_transport is not None:
                self._udp_transport.close()
                self._udp_transport = None
            if self._gateway is not None:
                await self._gateway.stop_on_loop()
                self._gateway = None
            if self._routing is not None:
                await self._routing.disconnect()
                self._routing = None
                self._xknx = None
        finally:
            self._state = VirtualRouterState.STOPPED
            if self._logger:
                self._logger.info("virtual router stopped")
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None
