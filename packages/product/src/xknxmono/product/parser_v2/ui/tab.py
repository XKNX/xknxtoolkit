from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UiTab:
    children: tuple[object, ...]
    id: str | None = None
    name: str | None = None
    text: str | None = None
    number: str | None = None
    icon: str | None = None
