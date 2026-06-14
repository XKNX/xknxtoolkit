"""The whole dynamic concern: build a flattened DynamicElement tree from the IR (resolving modules
and text templates), then evaluate parameter/com-object visibility over it for given values."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Protocol

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ComObjectParameterBlock,
    ComObjectRefRef,
    Module,
    ParameterBlockLayout,
    ParameterRefRef,
    ParameterSeparator,
)

from . import modules
from .com_objects import ComObject
from .parameters import Parameter

# --- flattened dynamic tree -------------------------------------------------------


@dataclass
class GridCell:
    """A cell in a grid-layout ParameterBlock: a parameter widget or a static label (a separator,
    e.g. a unit like "ms"). ``row``/``column`` are 1-based, from the IR's ``Cell="r,c"``."""

    row: int
    column: int
    param_ref_id: str | None = None
    label: str | None = None


@dataclass
class GridLayout:
    """A positioned cell layout for a ``Layout="Grid"`` or ``Layout="Table"`` ParameterBlock. A Table
    additionally carries column/row header text; when those are empty it's a plain grid."""

    columns: int
    cells: list[GridCell] = field(default_factory=list["GridCell"])
    column_headers: list[str] = field(default_factory=list[str])
    row_headers: list[str] = field(default_factory=list[str])


@dataclass
class DynamicElement:
    id: str | None = None
    name: str | None = None
    text: str | None = None
    number: int | None = None
    header_param_ref_id: str | None = None
    name_param_ref_id: str | None = None
    param_ref_ids: list[str] = field(default_factory=list[str])
    com_object_ref_ids: list[str] = field(default_factory=list[str])
    children: list[DynamicElement] = field(default_factory=list["DynamicElement"])
    chooses: list[DynamicChoose] = field(default_factory=list["DynamicChoose"])
    grid: GridLayout | None = None
    # Set on a spliced module-instance root: the module-def id this subtree came from and the
    # instance's full arguments (the numbering substrate; text args derive from them). The
    # instantiation pass uses these to rewrite refs and build the per-instance bundle
    # (see parser/instantiate.py); both ``None`` on ordinary nodes.
    module_def_id: str | None = None
    module_arguments: list[modules.ModuleArgument] | None = None


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
    # Substitute module args but keep the {{0}} name placeholder — it's filled per the channel's
    # name parameter (text_parameter_ref_id) at evaluation time, against live values.
    if text and text_args:
        text = modules.apply_text_args(text, text_args)

    grid = (
        _block_layout(node, text_args)
        if isinstance(node, ComObjectParameterBlock)
        else None
    )

    return DynamicElement(
        id=getattr(node, "id", None),
        name=getattr(node, "name", None),
        text=text,
        number=int(number) if number is not None else None,
        header_param_ref_id=getattr(node, "param_ref_id", None),
        name_param_ref_id=getattr(node, "text_parameter_ref_id", None),
        param_ref_ids=param_ref_ids,
        com_object_ref_ids=co_ref_ids,
        children=children,
        chooses=chooses,
        grid=grid,
    )


def _parse_cell(cell: str | None) -> tuple[int, int] | None:
    if not cell:
        return None
    parts = cell.split(",")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def _block_layout(
    block: ComObjectParameterBlock, text_args: dict[str, str] | None
) -> GridLayout | None:
    """The positioned cells of a ``Layout="Grid"`` or ``Layout="Table"`` block, keyed by their
    ``Cell="r,c"`` position: parameter widgets and separator labels. Cells placed conditionally
    (inside a ``<choose>``) are gathered from *every* branch — the actual visible branch is selected
    later by :func:`_visible_grid`. A Table also carries its column/row header text.

    The parsed IR carries the per-version enum (files.v23), a different class object than the
    ``intermediate`` re-export imported here, so identity/`==` fail — compare on ``.value``."""
    layout = block.layout.value
    if layout not in (
        ParameterBlockLayout.GRID.value,
        ParameterBlockLayout.TABLE.value,
    ):
        return None
    cells: list[GridCell] = []
    _collect_grid_cells(block.choice, text_args, cells)
    if not cells:
        return None
    columns = max(c.column for c in cells)
    column_headers: list[str] = []
    row_headers: list[str] = []
    if layout == ParameterBlockLayout.TABLE.value:
        column_headers = _header_texts(
            block.columns.column if block.columns else [], text_args
        )
        row_headers = _header_texts(block.rows.row if block.rows else [], text_args)
        columns = max(columns, len(column_headers))
    return GridLayout(
        columns=columns,
        cells=cells,
        column_headers=column_headers,
        row_headers=row_headers,
    )


class _Headered(Protocol):
    @property
    def text(self) -> str | None: ...


def _header_texts(
    items: Iterable[_Headered], text_args: dict[str, str] | None
) -> list[str]:
    out: list[str] = []
    for it in items:
        text = it.text or ""
        if text_args and text:
            text = modules.substitute_template(text, None, text_args)
        out.append(text)
    return out


def _collect_grid_cells(
    items: object, text_args: dict[str, str] | None, cells: list[GridCell]
) -> None:
    for item in items:  # type: ignore[attr-defined]
        if isinstance(item, ParameterRefRef):
            pos = _parse_cell(item.cell)
            if pos and item.ref_id:
                cells.append(GridCell(pos[0], pos[1], param_ref_id=item.ref_id))
        elif isinstance(item, ParameterSeparator):
            pos = _parse_cell(item.cell)
            if pos:
                label = item.text or ""
                if text_args:
                    label = modules.substitute_template(label, None, text_args)
                cells.append(GridCell(pos[0], pos[1], label=label))
        elif isinstance(item, modules.CHOOSE_TYPES):
            for when in item.when:
                _collect_grid_cells(when.choice, text_args, cells)


def _inline_module(
    module: Module, mods: modules.Modules, children: list[DynamicElement]
) -> None:
    """Splice a referenced module-def's dynamic tree in place of the <Module> reference."""
    mod_def = mods.defs.get(module.ref_id or "")
    if mod_def is None or mod_def.dynamic is None:
        return
    args = modules.text_args(module, mods)
    element = _element(mod_def.dynamic, mods, args)
    if len(element.children) == 1 and not element.param_ref_ids:
        element = element.children[0]
    element.id = module.id or element.id
    element.name = module.name or element.name
    element.module_def_id = module.ref_id
    element.module_arguments = modules.module_arguments(module, mods)
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

_OPERATORS = (">=", "<=", ">", "<")


def _token_matches(value: str, token: str) -> bool:
    """A ``<when Test=...>`` token: an exact value, or a comparison like ``>0`` / ``<=5``."""
    for op in _OPERATORS:
        if token.startswith(op):
            try:
                left, right = int(value), int(token[len(op) :])
            except ValueError:
                return False
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            return left < right
    return value == token


def _value_matches(value: str, test_values: list[str]) -> bool:
    return any(_token_matches(value, t) for t in test_values)


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
        return _value_matches(param_values[param_ref_id], test_values)

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
    grid: GridLayout | None = None


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
        grid = _visible_grid(node.element.grid, set(param_ids))
        if not param_ids and not com_ids and not visible_children:
            continue
        display_name = _resolve_name(node, params_by_id, param_values)
        result.append(
            VisibleNode(
                id=node.id,
                display_name=display_name or "?",
                param_ref_ids=param_ids,
                com_object_ref_ids=com_ids,
                children=visible_children,
                grid=grid,
            )
        )
    return result


def _visible_grid(
    grid: GridLayout | None, visible_param_ids: set[str]
) -> GridLayout | None:
    """Select the grid for the current values: keep the cells whose parameter is visible, plus the
    label cells in rows that still have a visible parameter (so a unit like "ms" stays with its
    field, but the labels of a hidden conditional row don't leak through)."""
    if grid is None:
        return None
    param_cells = [
        c for c in grid.cells if c.param_ref_id and c.param_ref_id in visible_param_ids
    ]
    if not param_cells:
        return None
    visible_rows = {c.row for c in param_cells}
    label_cells = [
        c for c in grid.cells if c.param_ref_id is None and c.row in visible_rows
    ]
    # A position can collect candidate params from several (mutually exclusive) choose branches;
    # keep the first visible one per cell so widgets never overlap.
    seen: set[tuple[int, int]] = set()
    cells: list[GridCell] = []
    for c in sorted(param_cells + label_cells, key=lambda c: (c.row, c.column)):
        pos = (c.row, c.column)
        if pos in seen:
            continue
        seen.add(pos)
        cells.append(c)
    return GridLayout(
        columns=grid.columns,
        cells=cells,
        column_headers=grid.column_headers,
        row_headers=grid.row_headers,
    )


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
        if _value_matches(current_value, when.test_values):
            return when
    for when in choose.conditions:
        if when.is_default:
            return when
    return None


def _resolve_name(
    node: TreeNode, params_by_id: dict[str, Parameter], param_values: dict[str, str]
) -> str | None:
    if node.header_param_ref_id:
        param = params_by_id.get(node.header_param_ref_id)
        if param and param.text:
            return param.text
    template = node.text or node.name
    if template is None:
        return None
    # Fill the {{0}} placeholder from the channel's name parameter (its value is the typed name).
    name_value = ""
    if node.element.name_param_ref_id:
        name_value = param_values.get(node.element.name_param_ref_id, "")
    return modules.fill_name(template, name_value)


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
