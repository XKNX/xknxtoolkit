from __future__ import annotations

import asyncio
from typing import Any

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

_SEARCH_REQUEST_SERVICE_TYPE = 0x0201
_SEARCH_REQUEST_EXTENDED_SERVICE_TYPE = 0x020B
_DESCRIPTION_REQUEST_SERVICE_TYPE = 0x0203
_KNXIP_HEADER_LENGTH = 6


class KNXIPDiscoveryResponder(asyncio.DatagramProtocol):
    """
    Answers SEARCH_REQUEST/SEARCH_REQUEST_EXTENDED/DESCRIPTION_REQUEST so a
    multicast-only KNX/IP endpoint (routing, no tunneling) shows up in
    ETS's device list. Used by VirtualRouter; factored out standalone so
    any other multicast-only endpoint can reuse it without duplicating
    this logic.
    """

    def __init__(
        self,
        local_ip: str,
        port: int,
        name: str,
        multicast_group: str,
        individual_address: str = "1.1.0",
        serial_number: str = "00:00:00:00:00:01",
        mac_address: str = "00:00:00:00:00:01",
        logger: Any = None,
    ) -> None:
        self._local_ip = local_ip
        self._port = port
        self._name = name
        self._multicast_group = multicast_group
        self._individual_address = individual_address
        self._serial_number = serial_number
        self._mac_address = mac_address
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

    def _dibs(self) -> list[DIBDeviceInformation | DIBSuppSVCFamilies]:
        dib_dev = DIBDeviceInformation()
        dib_dev.name = self._name
        dib_dev.multicast_address = self._multicast_group
        dib_dev.individual_address = IndividualAddress(self._individual_address)
        dib_dev.serial_number = self._serial_number
        dib_dev.mac_address = self._mac_address

        dib_svc = DIBSuppSVCFamilies()
        dib_svc.families.append(DIBSuppSVCFamilies.Family(DIBServiceFamily.CORE, 2))
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
