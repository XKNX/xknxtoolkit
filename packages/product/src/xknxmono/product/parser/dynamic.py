"""The whole dynamic concern: build a flattened DynamicElement tree from the IR (resolving modules
and text templates), then evaluate parameter/com-object visibility over it for given values."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ComObjectRefRef,
    Module,
    ParameterRefRef,
)

from . import modules
from .com_objects import ComObject
from .parameters import Parameter

# --- flattened dynamic tree -------------------------------------------------------


@dataclass
class DynamicElement:
    id: str | None = None
    name: str | None = None
    text: str | None = None
    number: int | None = None
    header_param_ref_id: str | None = None
    param_ref_ids: list[str] = field(default_factory=list[str])
    com_object_ref_ids: list[str] = field(default_factory=list[str])
    children: list[DynamicElement] = field(default_factory=list["DynamicElement"])
    chooses: list[DynamicChoose] = field(default_factory=list["DynamicChoose"])


@dataclass
class DynamicWhen:
    test_values: list[str] = field(default_factory=list[str])
    is_default: bool = False
    content: DynamicElement | None = None


@dataclass
class DynamicChoose:
    param_ref_id: str
    conditions: list[DynamicWhen] = field(default_factory=list[DynamicWhen])


def build_app_dynamic_tree(app: ApplicationProgram) -> DynamicElement | None:
    if app.dynamic is None:
        return None
    return _element(app.dynamic, modules.collect(app))


def _element(
    node: modules.ChoiceContainer,
    mods: modules.Modules,
    text_args: dict[str, str] | None = None,
) -> DynamicElement:
    param_ref_ids: list[str] = []
    co_ref_ids: list[str] = []
    children: list[DynamicElement] = []
    chooses: list[DynamicChoose] = []

    for item in node.choice:
        if isinstance(item, ParameterRefRef):
            if item.ref_id:
                param_ref_ids.append(item.ref_id)
        elif isinstance(item, ComObjectRefRef):
            if item.ref_id:
                co_ref_ids.append(item.ref_id)
        elif isinstance(item, Module):
            _inline_module(item, mods, children)
        elif isinstance(item, modules.CHOOSE_TYPES):
            chooses.append(_choose(item, mods, text_args))
        elif isinstance(item, modules.CONTAINER_TYPES):
            children.append(_element(item, mods, text_args))

    # Optional header fields are genuinely heterogeneous across choice members — read defensively.
    text = getattr(node, "text", None)
    number = getattr(node, "number", None)
    if text_args and text:
        text = modules.substitute_template(text, None, text_args)

    return DynamicElement(
        id=getattr(node, "id", None),
        name=getattr(node, "name", None),
        text=text,
        number=int(number) if number is not None else None,
        header_param_ref_id=getattr(node, "param_ref_id", None),
        param_ref_ids=param_ref_ids,
        com_object_ref_ids=co_ref_ids,
        children=children,
        chooses=chooses,
    )


def _inline_module(
    module: Module, mods: modules.Modules, children: list[DynamicElement]
) -> None:
    """Splice a referenced module-def's dynamic tree in place of the <Module> reference."""
    mod_def = mods.defs.get(module.ref_id or "")
    if mod_def is None or mod_def.dynamic is None:
        return
    element = _element(mod_def.dynamic, mods, modules.text_args(module, mods))
    if len(element.children) == 1 and not element.param_ref_ids:
        element = element.children[0]
    element.id = module.id or element.id
    element.name = module.name or element.name
    children.append(element)


def _choose(
    choose: modules.Choose,
    mods: modules.Modules,
    text_args: dict[str, str] | None,
) -> DynamicChoose:
    return DynamicChoose(
        param_ref_id=choose.param_ref_id or "",
        conditions=[_when(w, mods, text_args) for w in choose.when],
    )


def _when(
    when: modules.When,
    mods: modules.Modules,
    text_args: dict[str, str] | None,
) -> DynamicWhen:
    test_values = (
        [v.strip() for v in str(when.test).split() if v.strip()]
        if when.test is not None
        else []
    )
    return DynamicWhen(
        test_values=test_values,
        is_default=bool(when.default),
        content=_element(when, mods, text_args),
    )


# --- visibility evaluation --------------------------------------------------------

Condition = Callable[[dict[str, str]], bool]


def always_visible(_: dict[str, str]) -> bool:
    return True


def make_condition(
    param_ref_id: str, test_values: list[str], is_default: bool
) -> Condition:
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
    children: list[TreeNode] = field(default_factory=list["TreeNode"])
    visibility: Condition = always_visible


def build_tree(dynamic: DynamicElement | None) -> list[TreeNode]:
    if dynamic is None:
        return []
    return _build_children(dynamic, always_visible)


def _build_children(
    element: DynamicElement, parent_condition: Condition
) -> list[TreeNode]:
    nodes: list[TreeNode] = []
    for child in element.children:
        nodes.append(_build_node(child, parent_condition))
    for choose in element.chooses:
        for when in choose.conditions:
            when_condition = make_condition(
                choose.param_ref_id, when.test_values, when.is_default
            )
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
    children: list[VisibleNode] = field(default_factory=list["VisibleNode"])


def evaluate_tree(
    dynamic: DynamicElement | None,
    param_values: dict[str, str],
    params_by_id: dict[str, Parameter],
) -> list[VisibleNode]:
    return evaluate_tree_cached(build_tree(dynamic), param_values, params_by_id)


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
        result.append(
            VisibleNode(
                id=node.id,
                display_name=display_name or "?",
                param_ref_ids=param_ids,
                com_object_ref_ids=com_ids,
                children=visible_children,
            )
        )
    return result


def _collect_visible_refs(
    element: DynamicElement, param_values: dict[str, str]
) -> tuple[list[str], list[str]]:
    param_ids = list(element.param_ref_ids)
    com_ids = list(element.com_object_ref_ids)
    for choose in element.chooses:
        matched = _find_matching_when(choose, param_values)
        if matched and matched.content:
            nested_params, nested_coms = _collect_visible_refs(
                matched.content, param_values
            )
            param_ids.extend(nested_params)
            com_ids.extend(nested_coms)
    return param_ids, com_ids


def collect_all_visible_refs(
    element: DynamicElement, param_values: dict[str, str]
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
            content_params, content_coms = collect_all_visible_refs(
                matched.content, param_values
            )
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
        if (
            name_lower in ("generic", "channel", "?")
            and node.children
            and not node.param_ref_ids
        ):
            nodes[i : i + 1] = node.children
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


def visible_parameters(
    params: list[Parameter],
    dynamic: DynamicElement | None,
    param_values: dict[str, str] | None = None,
) -> list[Parameter]:
    """Parameters reachable in the dynamic tree for the given values (all of them if no tree)."""
    if dynamic is None:
        return list(params)
    if param_values is None:
        param_values = {p.id: p.value for p in params}
    visible_ids, _ = collect_all_visible_refs(dynamic, param_values)
    return [p for p in params if p.id in visible_ids]


def visible_com_object_ids(
    dynamic: DynamicElement | None, param_values: dict[str, str]
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
