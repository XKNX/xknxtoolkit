from __future__ import annotations

import asyncio
import contextlib
import socket
import threading
from collections.abc import Callable
from enum import Enum
from typing import Any

from xknx.exceptions import IncompleteKNXIPFrame
from xknx.io import util
from xknx.knxip import (
    DIB,
    HPAI,
    ConnectionStateRequest,
    ConnectionStateResponse,
    ConnectRequest,
    ConnectResponse,
    ConnectResponseData,
    DescriptionRequest,
    DescriptionResponse,
    DIBDeviceInformation,
    DIBSuppSVCFamilies,
    DisconnectRequest,
    DisconnectResponse,
    ErrorCode,
    HostProtocol,
    KNXIPBody,
    KNXIPFrame,
    SearchRequestExtended,
    SearchResponseExtended,
    TunnellingAck,
    TunnellingFeatureGet,
    TunnellingFeatureResponse,
    TunnellingFeatureSet,
    TunnellingFeatureType,
    TunnellingRequest,
)
from xknx.knxip.knxip_enum import DIBServiceFamily
from xknx.telegram.address import IndividualAddress
from xknx.telegram.apci import ReturnCode

from knx_gui.knxip_discovery import KNXIPDiscoveryResponder

# Static answers for TUNNELLING_FEATURE_GET - clients query these during
# TCP tunnel setup and won't proceed without a response. cEMI-only, one
# communication channel; we don't act differently based on any of
# these, so they're fixed rather than actually tracked. MAX_APDU_LENGTH
# isn't here since it's configurable per instance (see max_apdu_length).
_FEATURE_VALUES: dict[TunnellingFeatureType, bytes] = {
    TunnellingFeatureType.SUPPORTED_EMI_TYPE: bytes([0x00, 0x04]),  # cEMI only
    TunnellingFeatureType.ACTIVE_EMI_TYPE: bytes([0x00, 0x04]),
    TunnellingFeatureType.BUS_CONNECTION_STATUS: bytes([0x01]),  # connected
    TunnellingFeatureType.INTERFACE_FEATURE_INFO_ENABLE: bytes([0x00]),
    TunnellingFeatureType.DEVICE_DESCRIPTOR_TYPE_0: bytes([0x07, 0x00]),
}


class GatewayState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


class _ClientProtocol(asyncio.Protocol):
    """
    Thin per-connection I/O shim - all protocol logic lives on
    TunnellingGateway. Only one client is accepted at a time (rejected
    extras get closed immediately in `_client_connected`), but a
    rejected connection's own `connection_lost` still fires later -
    each instance tracks its own transport so it can tell whether it's
    still the active one before touching shared owner state.
    """

    def __init__(self, owner: TunnellingGateway) -> None:
        self._owner = owner
        self._transport: asyncio.Transport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self._transport = transport  # type: ignore[assignment]
        self._owner._client_connected(transport)  # type: ignore[arg-type]

    def data_received(self, data: bytes) -> None:
        if self._owner._transport is self._transport:
            self._owner._client_data_received(data)

    def connection_lost(self, exc: Exception | None) -> None:
        if self._owner._transport is self._transport:
            self._owner._client_connection_lost(exc)


class TunnellingGateway:
    """
    Minimal KNXnet/IP tunnelling server, over TCP.

    Used both as the standalone Proxy (relaying to/from a real KNX
    connection) and as the Virtual network's tunnelling entry point
    (relaying to/from a VirtualDevice and its routing bus) - this class
    only knows how to speak the tunnelling protocol to one connected
    client; what happens with the CEMI frames it receives, and what it's
    asked to send back out, is entirely up to `on_cemi`/`forward_cemi`
    and `send_cemi()`.

    Also joins the multicast group to answer SEARCH_REQUEST/
    SEARCH_REQUEST_EXTENDED/DESCRIPTION_REQUEST over UDP, via the shared
    `knx_gui.knxip_discovery.KNXIPDiscoveryResponder` - so it shows up in
    automatic gateway discovery instead of only being reachable by
    manually entering its IP. The advertised control endpoint carries
    `HostProtocol.IPV4_TCP`, telling clients to open a TCP connection to
    us for everything past discovery. Manual-add flows also commonly
    validate the address before letting you connect, over the same TCP
    connection, in two steps: a DESCRIPTION_REQUEST, then a unicast
    SEARCH_REQUEST_EXTENDED (over a second TCP connection, in practice)
    to fetch full capability DIBs - both are answered here too, over
    TCP, so validation succeeds either way. Handles the connection
    handshake (CONNECT_REQUEST/CONNECTIONSTATE_REQUEST/
    DISCONNECT_REQUEST) and relays TUNNELLING frames to/from a single
    connected client, optionally forwarding them on to another
    connection (see `forward_cemi`).

    TCP rather than UDP: KNXnet/IP tunnelling v2 (and most "add interface
    manually" flows) commonly goes over TCP, and unlike UDP a single
    stream connection carries everything - no separate control/data
    endpoint HPAIs, no route-back logic, no risk of a reply going to the
    wrong socket.

    CEMI payloads are passed through as opaque bytes in both directions.
    A real client tunnelling to us sends properly-formed L_Data.req
    frames as part of its own session with us, so there's nothing to
    reinterpret - this is transport framing, not application logic.
    """

    DEFAULT_PORT = 3671
    DEFAULT_MAX_APDU_LENGTH = 15
    DEFAULT_CLIENT_INDIVIDUAL_ADDRESS = "15.15.1"
    DEFAULT_MCAST_GROUP = "224.0.23.12"

    def __init__(
        self,
        port: int = DEFAULT_PORT,
        name: str = "xknxtoolkit gateway",
        serial_number: str = "00:00:00:00:00:02",
        mac_address: str = "00:00:00:00:00:02",
        max_apdu_length: int = DEFAULT_MAX_APDU_LENGTH,
        client_individual_address: str = DEFAULT_CLIENT_INDIVIDUAL_ADDRESS,
        multicast_group: str = DEFAULT_MCAST_GROUP,
        enable_discovery: bool = True,
        on_cemi: Callable[[bytes], None] | None = None,
        forward_cemi: Callable[[bytes], None] | None = None,
        logger: Any = None,
    ) -> None:
        self._port = port
        self._name = name
        self._serial_number = serial_number
        self._mac_address = mac_address
        self._max_apdu_length = max_apdu_length
        self._client_individual_address = IndividualAddress(client_individual_address)
        self._multicast_group = multicast_group
        # False when embedded in something that already runs its own
        # discovery responder covering us too (see VirtualRouter).
        self._enable_discovery = enable_discovery
        self._on_cemi = on_cemi
        self._forward_cemi = forward_cemi
        self._logger = logger

        self._state = GatewayState.STOPPED
        self._error: str | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        # False when running on a shared loop we don't own (start_on_loop) -
        # stop() must then leave that loop running for its actual owner.
        self._owns_loop = True
        self._thread: threading.Thread | None = None
        self._server: asyncio.Server | None = None
        self._discovery_transport: asyncio.DatagramTransport | None = None
        self._local_ips: list[str] = []

        self._transport: asyncio.Transport | None = None
        self._peer: tuple[str, int] | None = None
        self._buffer = b""
        self._channel_id: int | None = None
        self._out_sequence = 0
        self._cemi_count = 0

    @property
    def state(self) -> GatewayState:
        return self._state

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def connected(self) -> bool:
        return self._channel_id is not None

    @property
    def local_ips(self) -> list[str]:
        """Candidate IPs to add manually as an interface, once running."""
        return self._local_ips

    def set_forward(self, forward_cemi: Callable[[bytes], None] | None) -> None:
        self._forward_cemi = forward_cemi

    def start(self) -> None:
        if self._state in (GatewayState.STARTING, GatewayState.RUNNING):
            return
        self._state = GatewayState.STARTING
        self._error = None
        self._owns_loop = True

        loop_ready = threading.Event()

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            loop_ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run, daemon=True, name="KNX-Gateway")
        self._thread.start()
        loop_ready.wait()
        assert self._loop is not None
        asyncio.run_coroutine_threadsafe(self._start_async(), self._loop)

    async def start_on_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Run on an already-running event loop instead of spinning up our
        own dedicated thread - for embedding in something that already
        owns one (see VirtualRouter). `stop()`/`stop_on_loop()` then
        won't stop that shared loop out from under its actual owner.
        """
        self._owns_loop = False
        self._loop = loop
        self._state = GatewayState.STARTING
        self._error = None
        await self._start_async()

    async def stop_on_loop(self) -> None:
        """Counterpart to `start_on_loop` - stop in place on the caller's own loop."""
        await self._stop_async()

    async def _start_async(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            self._server = await loop.create_server(
                lambda: _ClientProtocol(self), host="0.0.0.0", port=self._port
            )

            if self._enable_discovery:
                local_ip = await util.get_default_local_ip(self._multicast_group)
                if local_ip is not None:
                    sock = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
                    )
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    with contextlib.suppress(AttributeError):
                        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    sock.bind(("", self._port))
                    mreq = socket.inet_aton(self._multicast_group) + socket.inet_aton(
                        local_ip
                    )
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                    transport, _ = await loop.create_datagram_endpoint(
                        lambda: KNXIPDiscoveryResponder(
                            local_ip,
                            self._port,
                            get_dibs=self._dibs,
                            protocol=HostProtocol.IPV4_TCP,
                            logger=self._logger,
                        ),
                        sock=sock,
                    )
                    self._discovery_transport = transport  # type: ignore[assignment]
                elif self._logger:
                    self._logger.warning(
                        "could not determine local IP - gateway will not be "
                        "discoverable over multicast, only by manual IP entry"
                    )

            self._state = GatewayState.RUNNING
            self._local_ips = [ip.ip for ip in util.get_local_ips()]
            if self._logger:
                self._logger.info(
                    "gateway running - add manually as an interface (TCP), "
                    "or discoverable automatically",
                    port=self._port,
                    candidate_ips=", ".join(self._local_ips),
                )
        except Exception as e:
            self._state = GatewayState.ERROR
            self._error = str(e)
            if self._logger:
                self._logger.error("gateway failed to start", error=str(e))

    def stop(self) -> None:
        if self._state == GatewayState.STOPPED:
            return
        if self._loop is not None:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self._loop)
        else:
            self._state = GatewayState.STOPPED

    async def _stop_async(self) -> None:
        try:
            if self._transport is not None:
                self._transport.close()
                self._transport = None
            if self._server is not None:
                self._server.close()
                self._server = None
            if self._discovery_transport is not None:
                self._discovery_transport.close()
                self._discovery_transport = None
        finally:
            self._channel_id = None
            self._peer = None
            self._buffer = b""
            self._local_ips = []
            self._state = GatewayState.STOPPED
            if self._logger:
                self._logger.info("gateway stopped", total_cemi=self._cemi_count)
            self._cemi_count = 0
            if self._owns_loop and self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None

    def send_cemi(self, raw_cemi: bytes) -> None:
        """Relay a CEMI frame to the connected client as a TUNNELLING_REQUEST."""
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._send_tunnelling_request, raw_cemi)

    def _send_tunnelling_request(self, raw_cemi: bytes) -> None:
        if self._channel_id is None:
            return
        request = TunnellingRequest(
            communication_channel_id=self._channel_id,
            sequence_counter=self._out_sequence,
            raw_cemi=raw_cemi,
        )
        self._send(request)
        self._out_sequence = (self._out_sequence + 1) & 0xFF

    # -- connection lifecycle (called by _ClientProtocol) -----------------

    def _client_connected(self, transport: asyncio.Transport) -> None:
        peer = transport.get_extra_info("peername")
        if self._transport is not None:
            if self._logger:
                self._logger.warning(
                    "rejecting tcp connection - already have a client",
                    existing=f"{self._peer[0]}:{self._peer[1]}" if self._peer else None,
                    new=f"{peer[0]}:{peer[1]}" if peer else None,
                )
            transport.close()
            return
        self._transport = transport
        self._peer = peer
        self._buffer = b""
        if self._logger:
            self._logger.debug(
                "tcp connection opened",
                from_addr=f"{peer[0]}:{peer[1]}" if peer else None,
            )

    def _client_data_received(self, data: bytes) -> None:
        if self._logger:
            self._logger.debug("tcp data received", hex=data.hex(" "))
        if self._buffer:
            data = self._buffer + data
            self._buffer = b""
        while data:
            try:
                frame, rest = KNXIPFrame.from_knx(data)
            except IncompleteKNXIPFrame:
                self._buffer = data
                return
            except Exception as e:
                # Catch broadly, not just the documented CouldNotParseKNXIP:
                # xknx's own frame parsing (e.g. an unrecognized SRP type
                # in SearchRequestExtended) can raise a plain ValueError
                # instead, which would otherwise tear down the whole
                # connection over one bad/unfamiliar frame.
                if self._logger:
                    self._logger.warning(
                        "could not parse frame", error=str(e), hex=data.hex(" ")
                    )
                return
            if self._logger:
                self._logger.debug(
                    "recv", service_type=frame.header.service_type_ident.name
                )
            self._handle_body(frame.body)
            data = rest

    def _client_connection_lost(self, exc: Exception | None) -> None:
        if self._logger:
            self._logger.debug("tcp connection closed", error=str(exc) if exc else None)
        if self._peer is not None and self._logger:
            self._logger.info(
                "client disconnected", from_addr=f"{self._peer[0]}:{self._peer[1]}"
            )
        self._transport = None
        self._peer = None
        self._channel_id = None
        self._buffer = b""

    # -- handlers -----------------------------------------------------

    def _send(self, body: KNXIPBody) -> None:
        if self._transport is None:
            return
        raw = KNXIPFrame.init_from_body(body).to_knx()
        if self._logger:
            self._logger.debug(
                "send", service_type=body.SERVICE_TYPE.name, hex=raw.hex(" ")
            )
        self._transport.write(raw)

    def _handle_body(self, body: KNXIPBody) -> None:
        if isinstance(body, ConnectRequest):
            self._handle_connect_request()
        elif isinstance(body, TunnellingRequest):
            self._handle_tunnelling_request(body)
        elif isinstance(body, TunnellingAck):
            self._handle_tunnelling_ack(body)
        elif isinstance(body, ConnectionStateRequest):
            self._handle_connectionstate_request(body)
        elif isinstance(body, DisconnectRequest):
            self._handle_disconnect_request(body)
        elif isinstance(body, DescriptionRequest):
            self._handle_description_request()
        elif isinstance(body, SearchRequestExtended):
            self._handle_search_request_extended()
        elif isinstance(body, TunnellingFeatureGet):
            self._handle_tunnelling_feature_get(body)
        elif isinstance(body, TunnellingFeatureSet):
            self._handle_tunnelling_feature_set(body)

    def _dibs(self) -> list[DIB]:
        dib_dev = DIBDeviceInformation()
        dib_dev.name = self._name
        dib_dev.individual_address = self._client_individual_address
        dib_dev.serial_number = self._serial_number
        dib_dev.mac_address = self._mac_address

        dib_svc = DIBSuppSVCFamilies()
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.CORE, 2))
        dib_svc.families.append(
            DIBSuppSVCFamilies.Family(DIBServiceFamily.TUNNELING, 2)
        )
        return [dib_dev, dib_svc]

    def _handle_description_request(self) -> None:
        response = DescriptionResponse()
        response.dibs = self._dibs()
        self._send(response)

    def _handle_search_request_extended(self) -> None:
        response = SearchResponseExtended(
            control_endpoint=HPAI(protocol=HostProtocol.IPV4_TCP)
        )
        response.dibs = self._dibs()
        self._send(response)

    def _feature_value(self, feature_type: TunnellingFeatureType) -> bytes | None:
        if feature_type == TunnellingFeatureType.INTERFACE_INDIVIDUAL_ADDRESS:
            return self._client_individual_address.to_knx()
        if feature_type == TunnellingFeatureType.MAX_APDU_LENGTH:
            return self._max_apdu_length.to_bytes(2, "big")
        return _FEATURE_VALUES.get(feature_type)

    def _handle_tunnelling_feature_get(self, body: TunnellingFeatureGet) -> None:
        if (
            self._channel_id is None
            or body.communication_channel_id != self._channel_id
        ):
            return
        data = self._feature_value(body.feature_type)
        self._send(
            TunnellingFeatureResponse(
                communication_channel_id=self._channel_id,
                sequence_counter=body.sequence_counter,
                feature_type=body.feature_type,
                return_code=ReturnCode.E_SUCCESS if data else ReturnCode.E_ERROR,
                data=data or bytes(2),
            )
        )

    def _handle_tunnelling_feature_set(self, body: TunnellingFeatureSet) -> None:
        if (
            self._channel_id is None
            or body.communication_channel_id != self._channel_id
        ):
            return
        # We don't act differently based on any feature value (e.g.
        # active EMI type) - CEMI is always passed straight through
        # regardless - so every set is just accepted and echoed back.
        self._send(
            TunnellingFeatureResponse(
                communication_channel_id=self._channel_id,
                sequence_counter=body.sequence_counter,
                feature_type=body.feature_type,
                return_code=ReturnCode.E_SUCCESS,
                data=body.data,
            )
        )

    def _handle_connect_request(self) -> None:
        self._channel_id = 1
        self._out_sequence = 0
        response = ConnectResponse(
            communication_channel=self._channel_id,
            status_code=ErrorCode.E_NO_ERROR,
            data_endpoint=HPAI(protocol=HostProtocol.IPV4_TCP),
            crd=ConnectResponseData(individual_address=self._client_individual_address),
        )
        self._send(response)
        if self._logger:
            self._logger.info(
                "client connected",
                from_addr=f"{self._peer[0]}:{self._peer[1]}" if self._peer else None,
                channel=1,
            )

    def _handle_tunnelling_request(self, body: TunnellingRequest) -> None:
        if (
            self._channel_id is None
            or body.communication_channel_id != self._channel_id
        ):
            return
        self._send(
            TunnellingAck(
                communication_channel_id=self._channel_id,
                sequence_counter=body.sequence_counter,
                status_code=ErrorCode.E_NO_ERROR,
            )
        )
        self._cemi_count += 1
        if self._logger:
            self._logger.debug(
                "cemi received", n=self._cemi_count, hex=body.raw_cemi.hex(" ")
            )
        if self._on_cemi is not None:
            self._on_cemi(body.raw_cemi)
        if self._forward_cemi is not None:
            self._forward_cemi(body.raw_cemi)

    def _handle_tunnelling_ack(self, body: TunnellingAck) -> None:
        if body.status_code != ErrorCode.E_NO_ERROR and self._logger:
            self._logger.warning("tunnelling ack error", status=body.status_code.name)

    def _handle_connectionstate_request(self, body: ConnectionStateRequest) -> None:
        status = (
            ErrorCode.E_NO_ERROR
            if self._channel_id is not None
            and body.communication_channel_id == self._channel_id
            else ErrorCode.E_CONNECTION_ID
        )
        self._send(
            ConnectionStateResponse(
                communication_channel_id=body.communication_channel_id,
                status_code=status,
            )
        )

    def _handle_disconnect_request(self, body: DisconnectRequest) -> None:
        self._send(
            DisconnectResponse(
                communication_channel_id=body.communication_channel_id,
                status_code=ErrorCode.E_NO_ERROR,
            )
        )
        if (
            self._channel_id == body.communication_channel_id
            and self._transport is not None
        ):
            self._transport.close()
