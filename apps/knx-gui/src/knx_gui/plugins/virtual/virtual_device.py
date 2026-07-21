from __future__ import annotations

from typing import Any

from xknx.cemi import CEMIFrame, CEMILData, CEMIMessageCode
from xknx.telegram import Telegram
from xknx.telegram.address import GroupAddress, IndividualAddress
from xknx.telegram.apci import (
    APCI,
    IndividualAddressSerialRead,
    IndividualAddressSerialResponse,
    IndividualAddressSerialWrite,
    SystemNetworkParameterRead,
    SystemNetworkParameterResponse,
)

_DEVICE_OBJECT = 0
_PID_SERIAL_NUMBER = 11


class VirtualDevice:
    """
    A simulated KNX device that can be found and programmed by ETS.

    Implements the first steps of ETS programming, all gated on
    ``programming_mode`` like a real device's programming button/LED:
    - responds to the "which devices are in programming mode" broadcast
      (A_SystemNetworkParameter_Read for the Device Object's
      PID_SERIAL_NUMBER) with its serial number
    - adopts an individual address via A_IndividualAddress_SerialNumber_Write
      when addressed by its serial number
    - answers A_IndividualAddress_SerialNumber_Read with its current
      individual address
    """

    def __init__(
        self,
        name: str = "Virtual Device",
        serial_number: bytes = bytes.fromhex("000a2fab1f19"),
        individual_address: str = "15.15.255",
        logger: Any = None,
    ) -> None:
        self.name = name
        self.serial_number = serial_number
        self.individual_address = IndividualAddress(individual_address)
        self.programming_mode = False
        self._logger = logger

    def set_logger(self, logger: Any) -> None:
        self._logger = logger

    def handle_cemi(self, raw: bytes) -> CEMIFrame | None:
        if not self.programming_mode:
            return None
        try:
            frame = CEMIFrame.from_knx(raw)
        except Exception:
            return None
        data = frame.data
        if not isinstance(data, CEMILData):
            return None
        payload = data.payload

        if isinstance(payload, SystemNetworkParameterRead):
            return self._handle_programming_mode_scan(payload)
        if isinstance(payload, IndividualAddressSerialWrite):
            return self._handle_serial_write(payload)
        if isinstance(payload, IndividualAddressSerialRead):
            return self._handle_serial_read(payload)
        return None

    def _handle_programming_mode_scan(
        self, payload: SystemNetworkParameterRead
    ) -> CEMIFrame | None:
        if (
            payload.object_type != _DEVICE_OBJECT
            or payload.property_id != _PID_SERIAL_NUMBER
        ):
            return None

        if self._logger:
            self._logger.info(
                "responding to programming mode scan",
                device=self.name,
                serial_number=self.serial_number.hex(),
            )

        # test_info_and_result = the request's test_info echoed back,
        # followed by the actual test_result (the serial number) -
        # confirmed against a real ETS-accepted response frame.
        response = SystemNetworkParameterResponse(
            object_type=_DEVICE_OBJECT,
            property_id=_PID_SERIAL_NUMBER,
            test_info_and_result=payload.test_info + self.serial_number,
        )
        return self._broadcast(response)

    def _handle_serial_write(
        self, payload: IndividualAddressSerialWrite
    ) -> CEMIFrame | None:
        if payload.serial != self.serial_number:
            return None

        if self._logger:
            self._logger.info(
                "adopting individual address",
                device=self.name,
                address=str(payload.address),
            )
        # Unacknowledged: real devices don't reply to this write, they just
        # adopt the address - confirmed against a real ETS-sent frame.
        self.individual_address = payload.address
        return None

    def _handle_serial_read(
        self, payload: IndividualAddressSerialRead
    ) -> CEMIFrame | None:
        if payload.serial != self.serial_number:
            return None

        if self._logger:
            self._logger.info(
                "responding to individual address serial read",
                device=self.name,
                address=str(self.individual_address),
            )

        # `address` here is the PL/RF domain address, not the device's
        # individual address (that's conveyed via the CEMI source address
        # below) - 0 for TP media, confirmed against a real captured frame.
        response = IndividualAddressSerialResponse(
            serial=self.serial_number,
            address=IndividualAddress(0),
        )
        return self._broadcast(response)

    def _broadcast(self, payload: APCI) -> CEMIFrame:
        telegram = Telegram(
            destination_address=GroupAddress("0/0/0"),
            source_address=self.individual_address,
            payload=payload,
        )
        return CEMIFrame(
            code=CEMIMessageCode.L_DATA_IND,
            data=CEMILData.init_from_telegram(telegram),
        )
