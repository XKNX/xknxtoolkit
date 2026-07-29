from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from xknx.knxip import (
    DIB,
    HPAI,
    DescriptionResponse,
    HostProtocol,
    KNXIPHeader,
    SearchResponse,
    SearchResponseExtended,
)
from xknx.knxip.knxip_enum import KNXIPServiceType

_SEARCH_REQUEST_SERVICE_TYPE = 0x0201
_SEARCH_REQUEST_EXTENDED_SERVICE_TYPE = 0x020B
_DESCRIPTION_REQUEST_SERVICE_TYPE = 0x0203
_KNXIP_HEADER_LENGTH = 6


class KNXIPDiscoveryResponder(asyncio.DatagramProtocol):
    """
    Answers SEARCH_REQUEST/SEARCH_REQUEST_EXTENDED/DESCRIPTION_REQUEST over
    UDP multicast so a KNX/IP endpoint shows up in automatic gateway
    discovery instead of only being reachable by manually entering its
    IP. Used by both VirtualRouter (routing) and TunnelingProxy
    (TCP tunnelling) - factored out standalone so neither duplicates this
    protocol handling. The DIBs (device info + supported service
    families) are supplied by the caller via `get_dibs`, since they
    differ per endpoint kind; `protocol` controls what the advertised
    control endpoint tells clients to connect back with (UDP for
    routing/tunneling, TCP for a TCP-only tunnelling server).
    """

    def __init__(
        self,
        local_ip: str,
        port: int,
        get_dibs: Callable[[], list[DIB]],
        protocol: HostProtocol = HostProtocol.IPV4_UDP,
        logger: Any = None,
    ) -> None:
        self._local_ip = local_ip
        self._port = port
        self._get_dibs = get_dibs
        self._protocol = protocol
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
                self._logger.info(
                    "search response", to_addr=f"{addr[0]}:{addr[1]}", length=len(resp)
                )
        elif service_type == _SEARCH_REQUEST_EXTENDED_SERVICE_TYPE:
            resp = self._build_search_response_extended()
            if self._logger:
                self._logger.info(
                    "search request extended", from_addr=f"{addr[0]}:{addr[1]}"
                )
            self._send(resp, addr)
            if self._logger:
                self._logger.info(
                    "search response extended",
                    to_addr=f"{addr[0]}:{addr[1]}",
                    length=len(resp),
                )
        elif service_type == _DESCRIPTION_REQUEST_SERVICE_TYPE:
            resp = self._build_description_response()
            if self._logger:
                self._logger.info(
                    "description request", from_addr=f"{addr[0]}:{addr[1]}"
                )
            self._send(resp, addr)
            if self._logger:
                self._logger.info(
                    "description response",
                    to_addr=f"{addr[0]}:{addr[1]}",
                    length=len(resp),
                )

    def _send(self, data: bytes, addr: tuple[str, int]) -> None:
        if self._transport is not None:
            self._transport.sendto(data, addr)

    def connection_lost(self, exc: Exception | None) -> None:
        pass

    def _control_endpoint(self) -> HPAI:
        return HPAI(self._local_ip, self._port, self._protocol)

    def _build_search_response(self) -> bytes:
        body = SearchResponse(control_endpoint=self._control_endpoint())
        body.dibs = self._get_dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.SEARCH_RESPONSE
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def _build_search_response_extended(self) -> bytes:
        body = SearchResponseExtended(control_endpoint=self._control_endpoint())
        body.dibs = self._get_dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.SEARCH_RESPONSE_EXTENDED
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def _build_description_response(self) -> bytes:
        body = DescriptionResponse()
        body.dibs = self._get_dibs()
        header = KNXIPHeader()
        header.service_type_ident = KNXIPServiceType.DESCRIPTION_RESPONSE
        header.set_length(body)
        return header.to_knx() + body.to_knx()

    def error_received(self, exc: Exception) -> None:
        if self._logger:
            self._logger.error("udp error", error=str(exc))
