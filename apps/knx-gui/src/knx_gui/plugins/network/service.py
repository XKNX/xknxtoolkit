from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from knx_gui.types import TelegramRecord
from xknx.cemi import CEMIFrame
from xknx.telegram import Telegram


class CaptureState(Enum):
    STOPPED = "stopped"
    CAPTURING = "capturing"


class NetworkService:
    def __init__(self) -> None:
        self._telegrams: list[TelegramRecord] = []
        self._state = CaptureState.STOPPED
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    @property
    def state(self) -> CaptureState:
        return self._state

    @property
    def telegrams(self) -> list[TelegramRecord]:
        return self._telegrams

    def start(self) -> None:
        if self._state == CaptureState.CAPTURING:
            return
        self._telegrams.clear()
        self._state = CaptureState.CAPTURING
        self._emit("capture_state_changed", self._state)

    def stop(self) -> None:
        if self._state == CaptureState.STOPPED:
            return
        self._state = CaptureState.STOPPED
        self._emit("capture_state_changed", self._state)

    def add_raw(self, cemi_bytes: bytes) -> TelegramRecord | None:
        return self.add_raw_with_timestamp(cemi_bytes, datetime.now(UTC))

    def add_raw_with_timestamp(
        self, cemi_bytes: bytes, timestamp: datetime
    ) -> TelegramRecord | None:
        if self._state != CaptureState.CAPTURING:
            return None
        telegram = self._parse_cemi(cemi_bytes)
        if telegram is None:
            return None
        record = TelegramRecord(telegram=telegram, timestamp=timestamp)
        self._telegrams.append(record)
        self._emit("telegram_added", record)
        return record

    def clear(self) -> None:
        self._telegrams.clear()
        self._emit("cleared")

    def subscribe(self, event: str, handler: Callable[..., Any]) -> Callable[[], None]:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)
        return lambda: self._listeners[event].remove(handler)

    def _emit(self, event: str, *args: Any) -> None:
        for handler in self._listeners.get(event, []):
            handler(*args)

    def _parse_cemi(self, cemi_bytes: bytes) -> Telegram | None:
        try:
            frame = CEMIFrame.from_knx(cemi_bytes)
            data = frame.data
            if data is None:
                return None
            return Telegram(
                source_address=data.src_addr,
                destination_address=data.dst_addr,
                payload=data.payload,
                tpci=data.tpci,
            )
        except Exception:
            return None
