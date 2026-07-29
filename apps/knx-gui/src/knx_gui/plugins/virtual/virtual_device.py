from __future__ import annotations

from typing import Any

from xknx.cemi import CEMIFrame, CEMILData, CEMIMessageCode
from xknx.telegram import Telegram
from xknx.telegram.address import GroupAddress, IndividualAddress
from xknx.telegram.apci import (
    APCI,
    DeviceDescriptorRead,
    DeviceDescriptorResponse,
    FunctionPropertyExtStateRead,
    FunctionPropertyExtStateResponse,
    IndividualAddressSerialRead,
    IndividualAddressSerialResponse,
    IndividualAddressSerialWrite,
    PropertyValueRead,
    PropertyValueResponse,
    RestartMasterReset,
    RestartMasterResetResponse,
    ReturnCode,
    SystemNetworkParameterRead,
    SystemNetworkParameterResponse,
)
from xknx.telegram.tpci import TAck, TConnect, TDataConnected, TDisconnect

_DEVICE_OBJECT = 0
_PID_SERIAL_NUMBER = 11

# Static property values captured verbatim from a real device's responses
# (relayed through the proxy during an ETS programming session) - exact PID
# semantics weren't decoded from spec, these are just replayed byte-for-byte
# so the same read sequence gets an answer ETS already accepted once.
_STATIC_PROPERTY_VALUES: dict[tuple[int, int], bytes] = {
    (_DEVICE_OBJECT, 56): bytes.fromhex("00e9"),
}


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

    Once addressed, also accepts a point-to-point connection (T_Connect/
    T_Data_Connected/T_Disconnect) to its individual address - independent
    of programming_mode, like a real already-addressed device - and answers
    the DeviceDescriptorRead / PropertyValueRead / FunctionPropertyExtStateRead
    / RestartMasterReset sequence ETS runs when (re)programming a device,
    replayed from a real captured session.
    """

    def __init__(
        self,
        name: str = "Virtual Device",
        serial_number: bytes = bytes.fromhex("000a2fab1f19"),
        individual_address: str = "15.15.255",
        mask_version: int = 0x07B0,
        logger: Any = None,
    ) -> None:
        self.name = name
        self.serial_number = serial_number
        self.individual_address = IndividualAddress(individual_address)
        self.mask_version = mask_version
        self.programming_mode = False
        self._logger = logger

        self._conn_partner: IndividualAddress | None = None
        self._conn_out_seq = 0

    def set_logger(self, logger: Any) -> None:
        self._logger = logger

    def handle_cemi(self, raw: bytes) -> list[CEMIFrame]:
        try:
            frame = CEMIFrame.from_knx(raw)
        except Exception:
            return []
        data = frame.data
        if not isinstance(data, CEMILData):
            return []

        if data.dst_addr == self.individual_address:
            return self._handle_point_to_point(data)

        if not self.programming_mode:
            return []
        payload = data.payload
        if isinstance(payload, SystemNetworkParameterRead):
            return self._as_list(self._handle_programming_mode_scan(payload))
        if isinstance(payload, IndividualAddressSerialWrite):
            return self._as_list(self._handle_serial_write(payload))
        if isinstance(payload, IndividualAddressSerialRead):
            return self._as_list(self._handle_serial_read(payload))
        return []

    @staticmethod
    def _as_list(frame: CEMIFrame | None) -> list[CEMIFrame]:
        return [frame] if frame is not None else []

    # -- point-to-point connection (DeviceDescriptor/PropertyValue/Restart) -

    def _handle_point_to_point(self, data: CEMILData) -> list[CEMIFrame]:
        tpci = data.tpci
        source = data.src_addr

        if isinstance(tpci, TConnect):
            self._conn_partner = source
            self._conn_out_seq = 0
            if self._logger:
                self._logger.debug(
                    "point-to-point connected", device=self.name, partner=str(source)
                )
            return []

        if isinstance(tpci, TDisconnect):
            if self._conn_partner == source:
                self._conn_partner = None
            return []

        if isinstance(tpci, TDataConnected) and self._conn_partner == source:
            frames = [self._ack(source, tpci.sequence_number)]
            response = self._handle_p2p_payload(data.payload)
            if response is not None:
                frames.append(self._send_connected(source, response))
            return frames

        # TAck (our own response being acknowledged) or an unnumbered
        # TDataConnected from a partner we're not connected to - nothing to
        # send back either way.
        return []

    def _handle_p2p_payload(self, payload: APCI | None) -> APCI | None:
        if isinstance(payload, DeviceDescriptorRead):
            return DeviceDescriptorResponse(
                descriptor=payload.descriptor, value=self.mask_version
            )
        if isinstance(payload, PropertyValueRead):
            return self._handle_property_value_read(payload)
        if isinstance(payload, FunctionPropertyExtStateRead):
            # Accepted unconditionally, echoing the request's data back -
            # real behavior for the specific object/property ETS queried
            # here wasn't decoded, only that this reply satisfied it.
            return FunctionPropertyExtStateResponse(
                interface_object_type=payload.interface_object_type,
                object_instance=payload.object_instance,
                property_id=payload.property_id,
                return_code=ReturnCode.E_SUCCESS,
                data=payload.data,
            )
        if isinstance(payload, RestartMasterReset):
            return RestartMasterResetResponse(error_code=0, process_time=0)
        return None

    def _handle_property_value_read(
        self, payload: PropertyValueRead
    ) -> PropertyValueResponse | None:
        if (
            payload.object_index == _DEVICE_OBJECT
            and payload.property_id == _PID_SERIAL_NUMBER
        ):
            data = self.serial_number
        else:
            data = _STATIC_PROPERTY_VALUES.get(
                (payload.object_index, payload.property_id)
            )
        if data is None:
            return None
        return PropertyValueResponse(
            object_index=payload.object_index,
            property_id=payload.property_id,
            count=payload.count,
            start_index=payload.start_index,
            data=data,
        )

    def _ack(self, partner: IndividualAddress, sequence_number: int) -> CEMIFrame:
        telegram = Telegram(
            destination_address=partner,
            source_address=self.individual_address,
            tpci=TAck(sequence_number=sequence_number),
        )
        return CEMIFrame(
            code=CEMIMessageCode.L_DATA_IND,
            data=CEMILData.init_from_telegram(telegram),
        )

    def _send_connected(self, partner: IndividualAddress, payload: APCI) -> CEMIFrame:
        telegram = Telegram(
            destination_address=partner,
            source_address=self.individual_address,
            tpci=TDataConnected(sequence_number=self._conn_out_seq),
            payload=payload,
        )
        self._conn_out_seq = (self._conn_out_seq + 1) & 0xF
        return CEMIFrame(
            code=CEMIMessageCode.L_DATA_IND,
            data=CEMILData.init_from_telegram(telegram),
        )

    # -- programming-mode broadcast services --------------------------------

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
