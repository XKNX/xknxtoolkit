from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from xknx.telegram import Telegram as XknxTelegram

from knx_gui.net import TelegramSource


@dataclass
class CemiRecord:
    """Raw CEMI frame captured from the network, including frames that can't be decoded as telegrams."""

    raw: bytes
    timestamp: datetime
    source_type: TelegramSource
    msg_code: str
    src_addr: str
    dst_addr: str
    flags: int | None
    hops: int | None

    @property
    def timestamp_str(self) -> str:
        return self.timestamp.strftime("%H:%M:%S")

    @property
    def raw_hex(self) -> str:
        return self.raw.hex(" ")


@dataclass
class TelegramRecord:
    telegram: XknxTelegram
    timestamp: datetime
    source_type: TelegramSource = TelegramSource.CONNECTION

    @property
    def source(self) -> str:
        return str(self.telegram.source_address)

    @property
    def destination(self) -> str:
        return str(self.telegram.destination_address)

    @property
    def service(self) -> str:
        if self.telegram.payload is None:
            return ""
        return type(self.telegram.payload).__name__

    @property
    def tpci(self) -> str:
        tpci = self.telegram.tpci
        if not tpci:
            return ""
        return type(tpci).__name__

    @property
    def dpt(self) -> str:
        if self.telegram.decoded_data is not None:
            return self.telegram.decoded_data.transcoder.__name__
        return ""

    @property
    def value(self) -> str:
        if self.telegram.decoded_data is not None:
            return str(self.telegram.decoded_data.value)
        payload = self.telegram.payload
        if payload is None:
            return ""
        return self._format_payload_value(payload)

    def _format_payload_value(self, payload: Any) -> str:
        name = type(payload).__name__

        if name == "DeviceDescriptorRead":
            return f"Desc{payload.descriptor}"
        if name == "DeviceDescriptorResponse":
            return f"Desc{payload.descriptor}: {payload.value:#06x}"
        if name == "IndividualAddressWrite":
            return str(payload.address)
        if name == "IndividualAddressSerialRead":
            return payload.serial.hex()
        if name == "IndividualAddressSerialResponse":
            return f"{payload.serial.hex()} -> {payload.address}"
        if name == "IndividualAddressSerialWrite":
            return f"{payload.serial.hex()} -> {payload.address}"
        if name == "MemoryRead":
            return f"@{payload.address:#06x} x{payload.count}"
        if name == "MemoryResponse":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "MemoryWrite":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "MemoryExtendedRead":
            return f"@{payload.address:#08x} x{payload.count}"
        if name == "MemoryExtendedReadResponse":
            return f"@{payload.address:#08x}: {payload.data.hex()} (rc={payload.return_code})"
        if name == "MemoryExtendedWrite":
            return f"@{payload.address:#08x}: {payload.data.hex()}"
        if name == "MemoryExtendedWriteResponse":
            return f"@{payload.address:#08x} (rc={payload.return_code})"
        if name == "UserMemoryRead":
            return f"@{payload.address:#06x} x{payload.count}"
        if name == "UserMemoryResponse":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "UserMemoryWrite":
            return f"@{payload.address:#06x}: {payload.data.hex()}"
        if name == "PropertyValueRead":
            return f"Obj{payload.object_index}/P{payload.property_id}[{payload.start_index}]"
        if name == "PropertyValueResponse":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "PropertyValueWrite":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "PropertyDescriptionRead":
            return f"Obj{payload.object_index}/P{payload.property_id}"
        if name == "PropertyDescriptionResponse":
            return f"Obj{payload.object_index}/P{payload.property_id} type={payload.type_:#x} max={payload.max_count}"
        if name == "FunctionPropertyCommand":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()}"
        if name == "FunctionPropertyStateRead":
            return f"Obj{payload.object_index}/P{payload.property_id}"
        if name == "FunctionPropertyStateResponse":
            return f"Obj{payload.object_index}/P{payload.property_id}: {payload.data.hex()} (rc={payload.return_code})"
        if name == "ADCRead":
            return f"Ch{payload.channel} x{payload.count}"
        if name == "ADCResponse":
            return f"Ch{payload.channel}: {payload.value}"
        if name == "AuthorizeRequest":
            return f"key={payload.key:#010x}"
        if name == "AuthorizeResponse":
            return f"level={payload.level}"
        if name == "UserManufacturerInfoRead":
            return ""
        if name == "UserManufacturerInfoResponse":
            return f"MfId={payload.manufacturer_id:#06x} {payload.data.hex()}"
        if name in ("IndividualAddressRead", "IndividualAddressResponse", "Restart"):
            return ""

        if hasattr(payload, "value"):
            payload_value = payload.value
            if payload_value is not None and hasattr(payload_value, "value"):
                return str(payload_value.value)
            return str(payload_value) if payload_value is not None else ""
        return ""

    @property
    def timestamp_str(self) -> str:
        return self.timestamp.strftime("%H:%M:%S")
