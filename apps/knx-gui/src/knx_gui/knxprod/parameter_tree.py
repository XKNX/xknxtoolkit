from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .types import DynamicChoose, DynamicElement, DynamicWhen

if TYPE_CHECKING:
    from .types import Parameter


@dataclass
class VisibleNode:
    id: str
    display_name: str
    param_ref_ids: list[str]
    com_object_ref_ids: list[str]
    children: list[VisibleNode] = field(default_factory=list)


def evaluate_tree(
    dynamic: DynamicElement | None,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> list[VisibleNode]:
    if dynamic is None:
        return []

    root_params, root_coms = _collect_visible(dynamic, param_values)
    children = _evaluate_children(dynamic, param_values, params_by_id)

    if root_params or root_coms:
        root_name = _resolve_name(dynamic, params_by_id, "Settings")
        root_node = VisibleNode(
            id=dynamic.id or "root",
            display_name=root_name,
            param_ref_ids=root_params,
            com_object_ref_ids=root_coms,
            children=[],
        )
        return [root_node] + children

    return children


def _evaluate_children(
    element: DynamicElement,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> list[VisibleNode]:
    nodes: list[VisibleNode] = []

    for child in element.children:
        node = _evaluate_element(child, param_values, params_by_id)
        if node:
            nodes.append(node)

    for choose in element.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            for child in matched.content.children:
                node = _evaluate_element(child, param_values, params_by_id)
                if node:
                    nodes.append(node)
            nodes.extend(_evaluate_children(matched.content, param_values, params_by_id))

    _number_duplicates(nodes)
    return nodes


def _evaluate_element(
    element: DynamicElement,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> VisibleNode | None:
    param_ids, com_ids = _collect_visible(element, param_values)
    children = _evaluate_children(element, param_values, params_by_id)

    if not param_ids and not com_ids and not children:
        return None

    display_name = _resolve_name(element, params_by_id, "Settings")

    return VisibleNode(
        id=element.id or "node",
        display_name=display_name,
        param_ref_ids=param_ids,
        com_object_ref_ids=com_ids,
        children=children,
    )


def _collect_visible(
    element: DynamicElement,
    param_values: dict[str, str],
) -> tuple[list[str], list[str]]:
    param_ids = list(element.param_ref_ids)
    com_ids = list(element.com_object_ref_ids)

    for choose in element.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            nested_params, nested_coms = _collect_visible(matched.content, param_values)
            param_ids.extend(nested_params)
            com_ids.extend(nested_coms)

    return param_ids, com_ids


def _find_matching_when(
    choose: DynamicChoose, param_values: dict[str, str]
) -> DynamicWhen | None:
    current_value = param_values.get(choose.param_ref_id, "")

    for when in choose.conditions:
        if current_value in when.test_values:
            return when

    for when in choose.conditions:
        if when.is_default:
            return when

    return None


def _resolve_name(
    element: DynamicElement,
    params_by_id: dict[str, Parameter],
    fallback: str,
) -> str:
    if element.header_param_ref_id:
        param = params_by_id.get(element.header_param_ref_id)
        if param and param.text:
            return param.text
    return element.text or element.name or element.id or fallback


def _number_duplicates(nodes: list[VisibleNode]) -> None:
    counts: dict[str, int] = {}
    for node in nodes:
        counts[node.display_name] = counts.get(node.display_name, 0) + 1

    indices: dict[str, int] = {}
    for node in nodes:
        if counts[node.display_name] > 1:
            idx = indices.get(node.display_name, 0) + 1
            indices[node.display_name] = idx
            node.display_name = f"{node.display_name} {idx}"
