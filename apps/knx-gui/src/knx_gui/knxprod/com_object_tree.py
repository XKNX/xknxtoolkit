from __future__ import annotations

from typing import TYPE_CHECKING

from .parameter_tree import collect_all_visible_refs

if TYPE_CHECKING:
    from .types import ComObject, DynamicElement, Parameter


def visible_com_object_ids(
    dynamic: DynamicElement | None,
    param_values: dict[str, str],
) -> set[str]:
    if dynamic is None:
        return set()
    _, com_ids = collect_all_visible_refs(dynamic, param_values)
    return com_ids


def filter_visible_com_objects(
    com_objects: list[ComObject],
    dynamic: DynamicElement | None,
    param_values: dict[str, str],
) -> list[ComObject]:
    if dynamic is None:
        return com_objects
    visible_ids = visible_com_object_ids(dynamic, param_values)
    return [co for co in com_objects if co.id in visible_ids]
