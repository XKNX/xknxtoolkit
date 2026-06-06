from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.plugins.node_editor.strings import S
from knx_gui.types import Device, Parameter
from xknxmono.product import GridLayout, ParamTypeKind, VisibleNode


@dataclass
class EnumPopupRequest:
    device: Device
    param: Parameter


def _render_int_param(
    widget_id: str,
    value: str,
    min_value: int | None,
    max_value: int | None,
    on_change: Callable[[str], None],
) -> None:
    """Render an integer parameter as a numeric text field. KNX number/time params are exact values
    (and a 32-bit param can exceed a slider's C int range), so this accepts free typing and clamps
    to the parameter's ``[min, max]`` once editing finishes."""
    _, new_text = imgui.input_text(
        f"##{widget_id}", value, imgui.InputTextFlags_.chars_decimal
    )
    # Commit once, when editing finishes — committing per keystroke rebuilds device state mid-edit
    # (and writes an undo event per character). Clamp the committed value to the parameter's range.
    if imgui.is_item_deactivated_after_edit():
        try:
            clamped = int(new_text)
        except ValueError:
            clamped = min_value if min_value is not None else 0
        if min_value is not None:
            clamped = max(min_value, clamped)
        if max_value is not None:
            clamped = min(max_value, clamped)
        if str(clamped) != value:
            on_change(str(clamped))


def group_parameters(params: list[Parameter]) -> dict[str, list[Parameter]]:
    groups: dict[str, list[Parameter]] = {}
    for param in params:
        text = param.text if param.text else param.name
        prefix = text.split(" - ")[0].strip() if " - " in text else "General"
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(param)
    return groups


def render_param_widget(
    param: Parameter,
    widget_id: str,
    on_change: Callable[[str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    pt = param.param_type
    if pt is None:
        _, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if imgui.is_item_deactivated_after_edit():
            on_change(new_value)
        return None

    if pt.kind == ParamTypeKind.ENUM:
        current_idx = 0
        for i, opt in enumerate(pt.options):
            if opt.value == param.value:
                current_idx = i
                break
        preview = pt.options[current_idx].text if pt.options else param.value

        if deferred_enum:
            if imgui.button(f"{preview}##{widget_id}", imgui.ImVec2(-1, 0)):
                return EnumPopupRequest(device=None, param=param)  # type: ignore
        else:
            if imgui.begin_combo(f"##{widget_id}", preview):
                for opt in pt.options:
                    selected = opt.value == param.value
                    if imgui.selectable(opt.text, selected)[0]:
                        on_change(opt.value)
                imgui.end_combo()
    elif pt.kind == ParamTypeKind.CHECKBOX:
        checked = param.value == "1"
        changed, new_checked = imgui.checkbox(f"##{widget_id}", checked)
        if changed:
            on_change("1" if new_checked else "0")
    elif pt.kind in (ParamTypeKind.NUMBER, ParamTypeKind.TIME):
        _render_int_param(widget_id, param.value, pt.min_value, pt.max_value, on_change)
    elif pt.kind == ParamTypeKind.TEXT:
        # Commit on blur/enter, not per keystroke (a mid-edit commit rebuilds device state).
        _, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if imgui.is_item_deactivated_after_edit():
            on_change(new_value)
    elif pt.kind == ParamTypeKind.PICTURE:
        imgui.text_disabled(S.NODE_IMAGE_PLACEHOLDER)
    else:
        _, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if imgui.is_item_deactivated_after_edit():
            on_change(new_value)
    return None


def render_parameters_grouped(
    device: Device,
    params: list[Parameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    popup_request: EnumPopupRequest | None = None
    groups = group_parameters(params)
    for group_name, group_params in sorted(groups.items()):
        group_label = f"{group_name}##{device.node_id}_{group_name}"
        is_open = imgui.tree_node(group_label)
        imgui.same_line()
        imgui.text_disabled(f"({len(group_params)})")
        if is_open:
            table_flags = imgui.TableFlags_.no_saved_settings
            if imgui.begin_table(
                f"##params_{device.node_id}_{group_name}", 2, table_flags
            ):
                imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch)
                imgui.table_setup_column(
                    "Value", imgui.TableColumnFlags_.width_fixed, 120
                )
                for param in group_params:
                    imgui.table_next_row()
                    imgui.table_set_column_index(0)
                    display_text = param.text if param.text else param.name
                    imgui.text(display_text)
                    imgui.table_set_column_index(1)
                    imgui.set_next_item_width(-1)
                    widget_id = f"{device.node_id}_{param.id}"
                    req = render_param_widget(
                        param,
                        widget_id,
                        lambda v, d=device, p=param.id: on_change(d, p, v),
                        deferred_enum=deferred_enum,
                    )
                    if req is not None:
                        popup_request = EnumPopupRequest(device=device, param=req.param)
                imgui.end_table()
            imgui.tree_pop()
    return popup_request


def render_parameters_tree(
    device: Device,
    nodes: list[VisibleNode],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    popup_request: EnumPopupRequest | None = None
    params_by_id = {p.id: p for p in device.get_visible_parameters()}

    for node in nodes:
        req = _render_node(device, node, params_by_id, on_change, deferred_enum)
        if req is not None:
            popup_request = req

    return popup_request


def _render_node(
    device: Device,
    node: VisibleNode,
    params_by_id: dict[str, Parameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
) -> EnumPopupRequest | None:
    # A plain grid block is pure layout (its "Grid" text is not a page header), so render it inline
    # without a collapsible tree node. A table keeps its title (e.g. "Channels") as a node.
    if node.grid is not None and not node.children and not _is_table(node.grid):
        return _render_grid_content(
            device, node, params_by_id, on_change, deferred_enum
        )

    popup_request: EnumPopupRequest | None = None
    label = f"{node.display_name}##{device.node_id}_{node.id}"

    param_count = _count_params(node)
    is_open = imgui.tree_node(label)
    imgui.same_line()
    imgui.text_disabled(f"({param_count})")

    if is_open:
        if node.grid is not None:
            req = _render_grid_content(
                device, node, params_by_id, on_change, deferred_enum
            )
            if req is not None:
                popup_request = req
        elif node.param_ref_ids:
            req = _render_param_table(
                device,
                node.param_ref_ids,
                params_by_id,
                on_change,
                deferred_enum,
                node.id,
            )
            if req is not None:
                popup_request = req

        for child in node.children:
            req = _render_node(device, child, params_by_id, on_change, deferred_enum)
            if req is not None:
                popup_request = req

        imgui.tree_pop()

    return popup_request


def _count_params(node: VisibleNode) -> int:
    count = len(node.param_ref_ids)
    for child in node.children:
        count += _count_params(child)
    return count


def _render_param_table(
    device: Device,
    param_ref_ids: list[str],
    params_by_id: dict[str, Parameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    popup_request: EnumPopupRequest | None = None
    params = [params_by_id[pid] for pid in param_ref_ids if pid in params_by_id]

    if not params:
        return None

    table_flags = imgui.TableFlags_.no_saved_settings
    table_id = f"##params_{device.node_id}_{prefix}"
    if imgui.begin_table(table_id, 2, table_flags):
        imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch)
        imgui.table_setup_column("Value", imgui.TableColumnFlags_.width_fixed, 120)

        for param in params:
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            display_text = param.text if param.text else param.name
            imgui.text(display_text)
            imgui.table_set_column_index(1)
            imgui.set_next_item_width(-1)
            widget_id = f"{device.node_id}_{param.id}"
            req = render_param_widget(
                param,
                widget_id,
                lambda v, d=device, p=param.id: on_change(d, p, v),
                deferred_enum=deferred_enum,
            )
            if req is not None:
                popup_request = EnumPopupRequest(device=device, param=req.param)

        imgui.end_table()

    return popup_request


def _is_table(grid: GridLayout) -> bool:
    """A grid with column/row headers is a ``Layout="Table"`` (rendered with a header row and a
    leading row-label column); without headers it's a plain layout grid."""
    return bool(grid.column_headers or grid.row_headers)


def _render_grid_content(
    device: Device,
    node: VisibleNode,
    params_by_id: dict[str, Parameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
) -> EnumPopupRequest | None:
    """Render a node's grid/table, plus any of its params the grid did not place into a cell."""
    assert node.grid is not None
    popup_request = _render_grid(
        device, node.grid, params_by_id, on_change, deferred_enum, node.id
    )
    grid_param_ids = {
        c.param_ref_id for c in node.grid.cells if c.param_ref_id is not None
    }
    leftover = [p for p in node.param_ref_ids if p not in grid_param_ids]
    if leftover:
        req = _render_param_table(
            device, leftover, params_by_id, on_change, deferred_enum, node.id
        )
        if req is not None:
            popup_request = req
    return popup_request


def _render_grid(
    device: Device,
    grid: GridLayout,
    params_by_id: dict[str, Parameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    """Render a ``Layout="Grid"`` / ``Layout="Table"`` ParameterBlock: cells positioned by
    (row, column) — parameter widgets and static labels (units like "ms", or help text). A table
    adds a column-header row and a leading row-label column."""
    popup_request: EnumPopupRequest | None = None
    by_pos = {(c.row, c.column): c for c in grid.cells}
    max_row = max((c.row for c in grid.cells), default=0)
    max_row = max(max_row, len(grid.row_headers))

    has_row_labels = bool(grid.row_headers)
    label_offset = 1 if has_row_labels else 0
    total_columns = grid.columns + label_offset

    # Default `sizing_stretch_prop` weights columns by content, so a long help-text/value column
    # swallows the width and squeezes the rest. Size each column by what it holds instead.
    table_flags = (
        imgui.TableFlags_.no_saved_settings | imgui.TableFlags_.sizing_stretch_prop
    )
    if _is_table(grid):
        table_flags |= imgui.TableFlags_.borders | imgui.TableFlags_.row_bg

    table_id = f"##grid_{device.node_id}_{prefix}"
    if imgui.begin_table(table_id, total_columns, table_flags):
        fixed = imgui.TableColumnFlags_.width_fixed
        stretch = imgui.TableColumnFlags_.width_stretch
        wrap_columns: set[int] = set()
        if has_row_labels:
            imgui.table_setup_column("", fixed)  # row-label column fits the K1/K2 text
        for col in range(1, grid.columns + 1):
            header = (
                grid.column_headers[col - 1]
                if col - 1 < len(grid.column_headers)
                else ""
            )
            col_cells = [c for c in grid.cells if c.column == col]
            has_param = any(c.param_ref_id for c in col_cells)
            longest = max((len(c.label or "") for c in col_cells), default=0)
            if has_param:
                imgui.table_setup_column(header, stretch, 1.0)
            elif longest > 16:  # a wrapping text column (e.g. help text) gets more room
                imgui.table_setup_column(header, stretch, 2.0)
                wrap_columns.add(col)
            else:  # a short unit label ("ms") just fits its content, unwrapped
                imgui.table_setup_column(header, fixed)
        if grid.column_headers:
            imgui.table_headers_row()

        for row in range(1, max_row + 1):
            imgui.table_next_row()
            if has_row_labels:
                imgui.table_set_column_index(0)
                if row - 1 < len(grid.row_headers):
                    imgui.text(grid.row_headers[row - 1])
            for col in range(1, grid.columns + 1):
                imgui.table_set_column_index(col - 1 + label_offset)
                cell = by_pos.get((row, col))
                if cell is None:
                    continue
                if cell.param_ref_id is not None:
                    param = params_by_id.get(cell.param_ref_id)
                    if param is None:
                        continue
                    imgui.set_next_item_width(-1)
                    widget_id = f"{device.node_id}_{param.id}"
                    req = render_param_widget(
                        param,
                        widget_id,
                        lambda v, d=device, p=param.id: on_change(d, p, v),
                        deferred_enum=deferred_enum,
                    )
                    if req is not None:
                        popup_request = EnumPopupRequest(device=device, param=req.param)
                elif cell.label:
                    # Wrap only the wide text columns; let short unit labels keep their full width.
                    if col in wrap_columns:
                        imgui.text_wrapped(cell.label)
                    else:
                        imgui.text(cell.label)
        imgui.end_table()

    return popup_request


class EnumPopup:
    def __init__(
        self,
        popup_id: str,
        on_change: Callable[[Device, str, str], None],
    ) -> None:
        self._popup_id = popup_id
        self._on_change = on_change
        self._request: EnumPopupRequest | None = None
        self._active: EnumPopupRequest | None = None

    def request(self, device: Device, param: Parameter) -> None:
        self._request = EnumPopupRequest(device=device, param=param)

    def render(self) -> None:
        if self._request is not None:
            self._active = self._request
            self._request = None
            imgui.open_popup(self._popup_id)

        if imgui.begin_popup(self._popup_id):
            target = self._active
            if target is not None and target.param.param_type is not None:
                for opt in target.param.param_type.options:
                    selected = opt.value == target.param.value
                    if imgui.menu_item(opt.text, "", selected)[0]:
                        self._on_change(target.device, target.param.id, opt.value)
            imgui.end_popup()
        else:
            self._active = None
