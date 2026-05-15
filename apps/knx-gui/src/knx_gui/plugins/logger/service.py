from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from typing import Any

import structlog

_MAX_RECORDS = 10_000


@dataclass
class LogRecord:
    timestamp: float
    level: str
    plugin: str
    event: str
    payload: dict[str, str] = field(default_factory=dict)

    @property
    def timestamp_str(self) -> str:
        t = time.localtime(self.timestamp)
        ms = int((self.timestamp % 1) * 1000)
        return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}.{ms:03d}"


class LogService:
    def __init__(self) -> None:
        self._records: deque[LogRecord] = deque(maxlen=_MAX_RECORDS)
        self._configure_structlog()

    def _wrap_payload(
        self, logger: Any, method: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        plugin = str(event_dict.pop("plugin", "app"))
        payload_keys = [k for k in event_dict if k != "event"]
        payload = {k: event_dict.pop(k) for k in payload_keys}
        event_dict["plugin"] = plugin
        if payload:
            event_dict["payload"] = payload
        return event_dict

    def _capture(
        self, logger: Any, method: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        payload = event_dict.get("payload", {})
        self._records.append(
            LogRecord(
                timestamp=time.time(),
                level=str(event_dict.get("level", method)),
                plugin=str(event_dict.get("plugin", "app")),
                event=str(event_dict.get("event", "")),
                payload={k: str(v) for k, v in payload.items()},
            )
        )
        return event_dict

    def _configure_structlog(self) -> None:
        structlog.configure(
            processors=[
                self._wrap_payload,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="%H:%M:%S", utc=False),
                self._capture,
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )

    def debug(self, event: str, plugin: str, **kwargs: Any) -> None:
        structlog.get_logger().debug(event, plugin=plugin, **kwargs)

    def info(self, event: str, plugin: str, **kwargs: Any) -> None:
        structlog.get_logger().info(event, plugin=plugin, **kwargs)

    def warning(self, event: str, plugin: str, **kwargs: Any) -> None:
        structlog.get_logger().warning(event, plugin=plugin, **kwargs)

    def error(self, event: str, plugin: str, **kwargs: Any) -> None:
        structlog.get_logger().error(event, plugin=plugin, **kwargs)

    def get_records(self) -> list[LogRecord]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()
