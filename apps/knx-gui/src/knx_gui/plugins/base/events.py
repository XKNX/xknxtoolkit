from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable[[Any], None]) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: type, handler: Callable[[Any], None]) -> None:
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    def emit(self, event: object) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
