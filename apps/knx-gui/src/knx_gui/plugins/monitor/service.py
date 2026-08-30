"""Group monitor service: track the latest group-address value seen on the bus, and send
GroupValueWrite / GroupValueRead. Decoding is left to the UI thread (it has the project DPT); this
service only stores the raw payload captured on the interface thread."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from xknx.cemi import CEMIFrame, CEMILData, CEMIMessageCode
from xknx.telegram import GroupAddress as XGroupAddress
from xknx.telegram import Telegram
from xknx.telegram.apci import GroupValueRead, GroupValueResponse, GroupValueWrite

from knx_gui.dpt import transcoder_for

if TYPE_CHECKING:
    from knx_gui.net import TelegramSource
    from knx_gui.plugins.base import Logger
    from knx_gui.plugins.connection.service import ConnectionService


@dataclass
class LiveValue:
    payload: Any  # DPTArray | DPTBinary
    timestamp: datetime
    service: str  # "Write" | "Response"


class MonitorService:
    def __init__(self, connection: ConnectionService) -> None:
        self._connection = connection
        self._log: Logger
        # address string -> latest value seen. Written on the interface thread, read on the UI
        # thread; dict item assignment is atomic under the GIL, which is enough here.
        self._values: dict[str, LiveValue] = {}

    def set_logger(self, log: Logger) -> None:
        self._log = log

    # --- incoming (interface thread) --------------------------------------

    def on_raw_cemi(self, raw_cemi: bytes, _source: TelegramSource) -> None:
        try:
            frame = CEMIFrame.from_knx(raw_cemi)
        except Exception:
            return
        data = frame.data
        if not isinstance(data, CEMILData):
            return
        payload = data.payload
        if isinstance(payload, GroupValueWrite):
            kind = "Write"
        elif isinstance(payload, GroupValueResponse):
            kind = "Response"
        else:
            return
        self._values[str(data.dst_addr)] = LiveValue(
            payload=payload.value, timestamp=datetime.now(), service=kind
        )

    def latest(self, address: str) -> LiveValue | None:
        return self._values.get(address)

    def clear(self) -> None:
        self._values = {}

    # --- outgoing (UI thread) ---------------------------------------------

    def send_write(self, address: str, dpt: str | None, text: str) -> bool:
        """Encode ``text`` per the group address' DPT and send a GroupValueWrite. Returns success."""
        transcoder = transcoder_for(dpt)
        if transcoder is None:
            self._log.warning("cannot write: unknown DPT", address=address, dpt=dpt)
            return False
        try:
            knx_value = transcoder.to_knx(_coerce(text))
        except Exception as e:  # xknx raises ConversionError/ValueError on bad input
            self._log.warning(
                "cannot encode value", address=address, value=text, error=str(e)
            )
            return False
        self._send(address, GroupValueWrite(knx_value))
        return True

    def send_read(self, address: str) -> None:
        self._send(address, GroupValueRead())

    def _send(self, address: str, payload: GroupValueWrite | GroupValueRead) -> None:
        telegram = Telegram(destination_address=XGroupAddress(address), payload=payload)
        frame = CEMIFrame(
            code=CEMIMessageCode.L_DATA_REQ,
            data=CEMILData.init_from_telegram(telegram),
        )
        self._connection.send_cemi(frame.to_knx())


def _coerce(text: str) -> Any:
    """Best-effort interpret a user-typed value: bool words, then int, then float, else the string."""
    t = text.strip()
    low = t.lower()
    if low in ("on", "true", "yes"):
        return True
    if low in ("off", "false", "no"):
        return False
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        pass
    return t
