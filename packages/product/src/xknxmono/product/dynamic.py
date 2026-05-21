from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .application import DynamicChoose, DynamicElement, DynamicWhen

if TYPE_CHECKING:
    from .application import ComObject, Parameter

Condition = Callable[[dict[str, str]], bool]


def always_visible(_: dict[str, str]) -> bool:
    return True


def make_condition(param_ref_id: str, test_values: list[str], is_default: bool) -> Condition:
    if is_default and not test_values:
        return always_visible

    def check(param_values: dict[str, str]) -> bool:
        if param_ref_id not in param_values:
            return True
        return param_values[param_ref_id] in test_values

    return check


def combine_conditions(parent: Condition, child: Condition) -> Condition:
    if parent is always_visible:
        return child
    if child is always_visible:
        return parent

    def check(param_values: dict[str, str]) -> bool:
        return parent(param_values) and child(param_values)

    return check


@dataclass
class TreeNode:
    id: str
    name: str | None
    text: str | None
    header_param_ref_id: str | None
    element: DynamicElement
    children: list[TreeNode] = field(default_factory=list)
    visibility: Condition = always_visible


def build_tree(dynamic: DynamicElement | None) -> list[TreeNode]:
    if dynamic is None:
        return []
    return _build_children(dynamic, always_visible)


def _build_children(element: DynamicElement, parent_condition: Condition) -> list[TreeNode]:
    nodes: list[TreeNode] = []

    for child in element.children:
        node = _build_node(child, parent_condition)
        nodes.append(node)

    for choose in element.chooses:
        for when in choose.conditions:
            when_condition = make_condition(choose.param_ref_id, when.test_values, when.is_default)
            combined = combine_conditions(parent_condition, when_condition)

            if when.content:
                nodes.extend(_build_children(when.content, combined))

    return nodes


def _build_node(element: DynamicElement, condition: Condition) -> TreeNode:
    return TreeNode(
        id=element.id or "node",
        name=element.name,
        text=element.text,
        header_param_ref_id=element.header_param_ref_id,
        element=element,
        children=_build_children(element, condition),
        visibility=condition,
    )


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
    tree = build_tree(dynamic)
    return evaluate_tree_cached(tree, param_values, params_by_id)


def evaluate_tree_cached(
    tree: list[TreeNode],
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> list[VisibleNode]:
    nodes = _evaluate_nodes(tree, param_values, params_by_id)
    _flatten_generic(nodes)
    _number_duplicates(nodes)
    return nodes


def _evaluate_nodes(
    nodes: list[TreeNode],
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> list[VisibleNode]:
    result: list[VisibleNode] = []

    for node in nodes:
        if not node.visibility(param_values):
            continue

        param_ids, com_ids = _collect_visible_refs(node.element, param_values)
        visible_children = _evaluate_nodes(node.children, param_values, params_by_id)

        if not param_ids and not com_ids and not visible_children:
            continue

        display_name = _resolve_name(node, params_by_id)

        result.append(VisibleNode(
            id=node.id,
            display_name=display_name or "?",
            param_ref_ids=param_ids,
            com_object_ref_ids=com_ids,
            children=visible_children,
        ))

    return result


def _collect_visible_refs(
    element: DynamicElement,
    param_values: dict[str, str],
) -> tuple[list[str], list[str]]:
    param_ids = list(element.param_ref_ids)
    com_ids = list(element.com_object_ref_ids)

    for choose in element.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            nested_params, nested_coms = _collect_visible_refs(matched.content, param_values)
            param_ids.extend(nested_params)
            com_ids.extend(nested_coms)

    return param_ids, com_ids


def collect_all_visible_refs(
    element: DynamicElement,
    param_values: dict[str, str],
) -> tuple[set[str], set[str]]:
    params: set[str] = set(element.param_ref_ids)
    coms: set[str] = set(element.com_object_ref_ids)

    for child in element.children:
        child_params, child_coms = collect_all_visible_refs(child, param_values)
        params.update(child_params)
        coms.update(child_coms)

    for choose in element.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            content_params, content_coms = collect_all_visible_refs(matched.content, param_values)
            params.update(content_params)
            coms.update(content_coms)

    return params, coms


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


def _resolve_name(node: TreeNode, params_by_id: dict[str, Parameter]) -> str | None:
    if node.header_param_ref_id:
        param = params_by_id.get(node.header_param_ref_id)
        if param and param.text:
            return param.text
    return node.text or node.name


def _flatten_generic(nodes: list[VisibleNode]) -> None:
    i = 0
    while i < len(nodes):
        node = nodes[i]
        name_lower = node.display_name.lower()
        if name_lower in ("generic", "channel", "?") and node.children and not node.param_ref_ids:
            nodes[i:i+1] = node.children
        else:
            _flatten_generic(node.children)
            i += 1


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
