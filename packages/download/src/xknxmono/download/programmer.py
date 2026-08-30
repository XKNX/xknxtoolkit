"""Low level device programming operations over a point-to-point connection.

The :class:`DeviceProgrammer` turns the primitive application layer services
provided by ``xknx`` into the operations a Load Procedure needs: chunked memory
writes, property writes, and driving a Load State Machine with read-back
verification. Those services are defined in KNX Standard v3.0.0, Chapter 3/3/7
"Application Layer": A_Memory_Read (section 3.5.3), A_Memory_Write (section 3.5.4),
A_PropertyValue_Read/A_PropertyValue_Write, and A_DeviceDescriptor_Read
(section 3.4.2.1). Memory reads/writes are split to the connection's maximum APDU
length.

It talks to any object implementing :class:`BusConnection`; at runtime this is
``xknx.management.P2PConnection``, in tests it is a fake.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Protocol

from xknx.telegram.apci import (
    DeviceDescriptorRead,
    DeviceDescriptorResponse,
    FunctionPropertyCommand,
    FunctionPropertyStateRead,
    FunctionPropertyStateResponse,
    MemoryRead,
    MemoryResponse,
    MemoryWrite,
    PropertyValueRead,
    PropertyValueResponse,
    PropertyValueWrite,
    Restart,
    RestartMasterReset,
    RestartMasterResetResponse,
)

from . import load_state
from .errors import DownloadError, LoadStateError, VerificationError

if TYPE_CHECKING:
    from xknx.telegram import Telegram
    from xknx.telegram.apci import APCI

# Octets consumed by TPCI/APCI/count/address in a standard A_Memory_Write ASDU.
_MEMORY_OVERHEAD = 3
# A_Memory_Write encodes the byte count in 6 bits.
_MAX_MEMORY_CHUNK = 0x3F
# Octets consumed by APCI/object/property/count/index in A_PropertyValue_Write.
_PROPERTY_OVERHEAD = 5
# A_PropertyValue_Write encodes the element count in 4 bits.
_MAX_PROPERTY_ELEMENTS = 0xF
# Default APDU length every KNX device has to support.
DEFAULT_MAX_APDU_LENGTH = 15
# Upper bound used when negotiating the APDU length up from the default.
MAX_NEGOTIATED_APDU_LENGTH = 254
# Device Object property carrying the device's maximum APDU length (2 octets).
PID_MAX_APDU_LENGTH = 56
# Property id carrying an interface object's type (PID_OBJECT_TYPE).
PID_OBJECT_TYPE = 1
# Property id carrying a loadable part's table base address (PID_TABLE_REFERENCE).
PID_TABLE_REFERENCE = 7
# Highest interface object index scanned when locating an object by type.
_MAX_OBJECT_INDEX = 255


class BusConnection(Protocol):
    """Subset of ``xknx.management.P2PConnection`` used for programming."""

    async def send_data(self, payload: APCI, wait_for_ack: bool = True) -> None:
        """Send a payload and, by default, wait for the transport layer ACK."""
        ...

    async def request(self, payload: APCI, expected: type[APCI] | None) -> Telegram:
        """Send a payload and wait for the device's response telegram."""
        ...


class ConnectionManager(Protocol):
    """Opens and closes point-to-point connections for a Load Procedure.

    A Load Procedure opens the connection on a Connect control and closes it on
    a Disconnect (and after a Restart). Implementations map ``open`` to a fresh
    T_Connect and ``close`` to T_Disconnect.
    """

    async def open(self) -> BusConnection:
        """Open a connection to the device and return it."""
        ...

    async def close(self) -> None:
        """Close the currently open connection, if any."""
        ...


class DeviceProgrammer:
    """Perform programming operations over an open point-to-point connection."""

    def __init__(
        self,
        connection: BusConnection,
        *,
        max_apdu_length: int = DEFAULT_MAX_APDU_LENGTH,
    ) -> None:
        """Initialize with a connected bus connection and the negotiated APDU length."""
        self.connection = connection
        self.max_apdu_length = max_apdu_length
        self._object_index_cache: dict[tuple[int, int], int] = {}

    @property
    def memory_chunk_size(self) -> int:
        """Largest memory payload that fits into a single telegram (at least 1)."""
        return max(1, min(self.max_apdu_length - _MEMORY_OVERHEAD, _MAX_MEMORY_CHUNK))

    async def read_device_descriptor(self) -> int:
        """Read device descriptor type 0 (the mask version)."""
        telegram = await self.connection.request(
            DeviceDescriptorRead(descriptor=0), DeviceDescriptorResponse
        )
        payload = telegram.payload
        if not isinstance(payload, DeviceDescriptorResponse):
            raise VerificationError("no device descriptor response received")
        return payload.value

    async def read_max_apdu_length(self) -> int:
        """Read the device's maximum APDU length from the Device Object.

        PID_MAX_APDU_LENGTH (property 56 of the Device Object, interface object
        index 0) holds the largest APDU the device accepts, in octets. Falls back
        to the mandatory default when the device does not expose it.
        """
        data = await self.read_property(0, PID_MAX_APDU_LENGTH)
        if not data:
            return DEFAULT_MAX_APDU_LENGTH
        return int.from_bytes(data, "big")

    async def read_memory(self, address: int, size: int) -> bytes:
        """Read ``size`` octets starting at ``address``, chunked to the APDU length."""
        result = bytearray()
        chunk = self.memory_chunk_size
        offset = 0
        while offset < size:
            count = min(chunk, size - offset)
            telegram = await self.connection.request(
                MemoryRead(address=address + offset, count=count), MemoryResponse
            )
            payload = telegram.payload
            if not isinstance(payload, MemoryResponse):
                raise VerificationError(
                    f"no memory response for address {address + offset:#06x}"
                )
            if len(payload.data) != count:
                raise VerificationError(
                    f"short memory response at {address + offset:#06x}: "
                    f"asked {count} got {len(payload.data)}"
                )
            result.extend(payload.data)
            offset += count
        return bytes(result)

    async def write_memory(
        self, address: int, data: bytes, *, verify: bool = False
    ) -> None:
        """Write ``data`` starting at ``address``, chunked to the APDU length.

        With ``verify`` each block is read back and compared right after it is
        written (per KNX 3/5/2), so a lost EEPROM write is caught immediately.
        """
        chunk = self.memory_chunk_size
        for offset in range(0, len(data), chunk):
            block = data[offset : offset + chunk]
            block_address = address + offset
            await self.connection.send_data(
                MemoryWrite(address=block_address, data=block)
            )
            if verify:
                read_back = await self.read_memory(block_address, len(block))
                if read_back != block:
                    raise VerificationError(
                        f"memory verification failed at {block_address:#06x}: "
                        f"wrote {block.hex()} read {read_back.hex()}"
                    )

    async def read_property(
        self,
        object_index: int,
        property_id: int,
        *,
        count: int = 1,
        start_index: int = 1,
    ) -> bytes:
        """Read a property value from an interface object."""
        telegram = await self.connection.request(
            PropertyValueRead(
                object_index=object_index,
                property_id=property_id,
                count=count,
                start_index=start_index,
            ),
            PropertyValueResponse,
        )
        payload = telegram.payload
        if not isinstance(payload, PropertyValueResponse):
            raise VerificationError(
                f"no property response for object {object_index} property {property_id}"
            )
        return payload.data

    async def write_property(
        self,
        object_index: int,
        property_id: int,
        data: bytes,
        *,
        count: int = 1,
        start_index: int = 1,
    ) -> bytes:
        """Write a property value and return the resulting value.

        A_PropertyValue_Write is confirmed by A_PropertyValue_Response carrying
        the resulting value, so this waits for that response (via ``request``)
        rather than only the transport ACK - otherwise the buffered response
        would be mistaken for the answer to the next request.

        The element count is encoded in four bits and the data must fit the APDU,
        so a value spanning more than 15 elements or one frame is written in
        successive element ranges; the last response is returned.
        """
        element_size = (len(data) // count) if count > 1 else len(data)
        max_bytes = max(1, self.max_apdu_length - _PROPERTY_OVERHEAD)
        if element_size and element_size <= max_bytes:
            per_frame = max(1, min(_MAX_PROPERTY_ELEMENTS, max_bytes // element_size))
        else:
            per_frame = _MAX_PROPERTY_ELEMENTS

        result = b""
        element = 0
        while element < count:
            frame_count = min(per_frame, count - element)
            frame_data = (
                data[element * element_size : (element + frame_count) * element_size]
                if element_size
                else data
            )
            result = await self._write_property_frame(
                object_index,
                property_id,
                frame_data,
                frame_count,
                start_index + element,
            )
            element += frame_count
        return result

    async def _write_property_frame(
        self,
        object_index: int,
        property_id: int,
        data: bytes,
        count: int,
        start_index: int,
    ) -> bytes:
        """Send a single A_PropertyValue_Write and return the resulting value."""
        telegram = await self.connection.request(
            PropertyValueWrite(
                object_index=object_index,
                property_id=property_id,
                count=count,
                start_index=start_index,
                data=data,
            ),
            PropertyValueResponse,
        )
        payload = telegram.payload
        if not isinstance(payload, PropertyValueResponse):
            raise VerificationError(
                f"no property write response for object {object_index} "
                f"property {property_id}"
            )
        return payload.data

    async def invoke_function_property(
        self, object_index: int, property_id: int, data: bytes
    ) -> bytes:
        """Call a Function Property and return the resulting state.

        A_FunctionPropertyCommand invokes a use-case specific function on an
        interface object and is confirmed by A_FunctionPropertyState_Response
        carrying a return code and the resulting state (KNX Standard v3.0.0,
        3/3/7 section 3.4.7.1). A non-zero return code means the device rejected
        the command.
        """
        telegram = await self.connection.request(
            FunctionPropertyCommand(
                object_index=object_index, property_id=property_id, data=data
            ),
            FunctionPropertyStateResponse,
        )
        return self._function_property_result(telegram, object_index, property_id)

    async def read_function_property(
        self, object_index: int, property_id: int
    ) -> bytes:
        """Read a Function Property state and return it.

        A_FunctionPropertyState_Read reads the state of a function property and is
        answered by A_FunctionPropertyState_Response (KNX Standard v3.0.0, 3/3/7
        section 3.4.7.2).
        """
        telegram = await self.connection.request(
            FunctionPropertyStateRead(
                object_index=object_index, property_id=property_id
            ),
            FunctionPropertyStateResponse,
        )
        return self._function_property_result(telegram, object_index, property_id)

    @staticmethod
    def _function_property_result(
        telegram: Telegram, object_index: int, property_id: int
    ) -> bytes:
        """Validate a Function Property response and return its state data."""
        payload = telegram.payload
        if not isinstance(payload, FunctionPropertyStateResponse):
            raise VerificationError(
                f"no function property response for object {object_index} "
                f"property {property_id}"
            )
        if payload.return_code != 0:
            raise LoadStateError(
                f"function property {property_id} on object {object_index} "
                f"returned error code {payload.return_code:#04x}"
            )
        return payload.data

    async def read_table_reference(self, object_index: int) -> int:
        """Read a loadable part's table base address (PID_TABLE_REFERENCE)."""
        data = await self.read_property(object_index, PID_TABLE_REFERENCE)
        if not data:
            raise VerificationError(f"empty table reference for object {object_index}")
        return int.from_bytes(data, "big")

    async def locate_object(self, object_type: int, occurrence: int = 0) -> int:
        """Resolve the object index of the ``occurrence``-th object of a type.

        ``occurrence`` is zero-based, matching the product application program XML (``Occurrence="0"``
        is the first instance). Scans interface objects reading ``PID_OBJECT_TYPE``
        until the requested occurrence is found. Cached per programmer instance.
        """
        cached = self._object_index_cache.get((object_type, occurrence))
        if cached is not None:
            return cached
        ordinal = 0
        for index in range(_MAX_OBJECT_INDEX + 1):
            try:
                data = await self.read_property(index, PID_OBJECT_TYPE)
            except (VerificationError, DownloadError):
                break
            if len(data) < 2:
                break
            found_type = int.from_bytes(data[:2], "big")
            if found_type == object_type:
                if ordinal == occurrence:
                    self._object_index_cache[(object_type, occurrence)] = index
                    return index
                ordinal += 1
        raise LoadStateError(
            f"interface object type {object_type} occurrence {occurrence} not found"
        )

    async def read_load_state(self, object_index: int) -> load_state.LoadState:
        """Read the current state of an object's Load State Machine."""
        data = await self.read_property(object_index, load_state.PID_LOAD_STATE_CONTROL)
        if not data:
            raise LoadStateError(f"empty load state for object {object_index}")
        return _decode_load_state(data[0], object_index)

    async def send_load_event(
        self,
        object_index: int,
        event: bytes,
        expected: load_state.LoadState,
        *,
        retries: int = 30,
        retry_delay: float = 1.0,
    ) -> None:
        """Write a load event and verify the machine reaches ``expected``.

        ``LOAD_COMPLETE`` triggers a checksum calculation that can take a while,
        and a device may report a transient ``UNLOADING``/``LOAD_COMPLETING``
        state first, so the state is polled up to ``retries`` times.
        """
        resulting = await self.write_property(
            object_index, load_state.PID_LOAD_STATE_CONTROL, event
        )
        state = (
            _decode_load_state(resulting[0], object_index)
            if resulting
            else await self.read_load_state(object_index)
        )
        for _ in range(max(retries, 0)):
            if state == expected:
                return
            if state == load_state.LoadState.ERROR:
                raise LoadStateError(
                    f"object {object_index} entered ERROR state "
                    f"(expected {expected.name})"
                )
            await asyncio.sleep(retry_delay)
            state = await self.read_load_state(object_index)
        if state != expected:
            raise LoadStateError(
                f"object {object_index} did not reach {expected.name}, "
                f"last state {state.name}"
            )

    async def restart(self) -> None:
        """Restart the device (also closes the transport connection)."""
        await self.connection.send_data(Restart(), wait_for_ack=False)

    async def master_reset(self, erase_code: int, channel_number: int) -> int:
        """Perform a Master Reset and return the device's process time in ms.

        A Master Reset is an A_Restart with restart_type = 1, carrying an erase
        code and channel number (KNX Standard v3.0.0, 3/3/7 section 3.4.2.2; the
        erase codes are defined with DM_Restart in 3/5/2). Unlike a Basic Restart
        it is confirmed at the application layer by A_Restart_Master_Reset_Response
        with an error code and the process time the device needs before it is
        reachable again. A non-zero error code means the device refused the reset.
        The device restarts afterwards, tearing down the connection.
        """
        telegram = await self.connection.request(
            RestartMasterReset(erase_code=erase_code, channel_number=channel_number),
            RestartMasterResetResponse,
        )
        payload = telegram.payload
        if not isinstance(payload, RestartMasterResetResponse):
            raise LoadStateError("no master reset response received")
        if payload.error_code != 0:
            raise LoadStateError(
                f"device refused master reset (erase code {erase_code}, channel "
                f"{channel_number}): error code {payload.error_code:#04x}"
            )
        return payload.process_time


def _decode_load_state(value: int, object_index: int) -> load_state.LoadState:
    """Map a raw load state octet to :class:`LoadState`, erroring on unknowns."""
    try:
        return load_state.LoadState(value)
    except ValueError as exc:
        raise LoadStateError(
            f"object {object_index} reported unknown load state {value:#04x}"
        ) from exc
