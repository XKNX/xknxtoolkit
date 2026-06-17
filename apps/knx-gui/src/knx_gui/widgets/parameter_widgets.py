from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from knx_gui.plugins.node_editor.strings import S
from knx_gui.types import Device
from xknxmono.models.intermediate.parameter_block_layout_t import ParameterBlockLayout
from xknxmono.product.parser_v2.ui import (
    UiComObject,
    UiNode,
    UiParameter,
    UiParameterBlock,
    UiSeparator,
    UiTab,
)
from xknxmono.product.parser_v2.ui.parameter import (
    CheckBoxWidget,
    EnumWidget,
    NumberSliderWidget,
    NumberWidget,
    PictureWidget,
    TextWidget,
)


@dataclass
class EnumPopupRequest:
    device: Device
    param: UiParameter


def render_param_widget(
    param: UiParameter,
    widget_id: str,
    on_change: Callable[[str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    match param.widget:
        case EnumWidget() as w:
            current_idx = 0
            for i, choice in enumerate(w.choices):
                if str(choice.value) == param.value:
                    current_idx = i
                    break
            preview = w.choices[current_idx].label if w.choices else param.value
            if deferred_enum:
                if imgui.button(f"{preview}##{widget_id}", imgui.ImVec2(-1, 0)):
                    return EnumPopupRequest(device=None, param=param)  # type: ignore[arg-type]
            else:
                if imgui.begin_combo(f"##{widget_id}", preview):
                    for choice in w.choices:
                        selected = str(choice.value) == param.value
                        if imgui.selectable(choice.label, selected)[0]:
                            on_change(str(choice.value))
                    imgui.end_combo()
        case NumberWidget() | NumberSliderWidget() as w:
            _render_int_param(widget_id, param.value, w.min, w.max, on_change)
        case CheckBoxWidget():
            checked = param.value == "1"
            changed, new_checked = imgui.checkbox(f"##{widget_id}", checked)
            if changed:
                on_change("1" if new_checked else "0")
        case TextWidget():
            _, new_value = imgui.input_text(f"##{widget_id}", param.value)
            if imgui.is_item_deactivated_after_edit():
                on_change(new_value)
        case PictureWidget():
            imgui.text_disabled(S.NODE_IMAGE_PLACEHOLDER)
        case _:
            _, new_value = imgui.input_text(f"##{widget_id}", param.value)
            if imgui.is_item_deactivated_after_edit():
                on_change(new_value)
    return None


def _render_int_param(
    widget_id: str,
    value: str,
    min_value: int | None,
    max_value: int | None,
    on_change: Callable[[str], None],
) -> None:
    _, new_text = imgui.input_text(
        f"##{widget_id}", value, imgui.InputTextFlags_.chars_decimal
    )
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


def count_parameters(nodes: list[UiNode] | tuple[UiNode, ...]) -> int:
    count = 0
    for node in nodes:
        if isinstance(node, UiParameter):
            count += 1
        elif isinstance(node, (UiTab, UiParameterBlock)):
            count += count_parameters(node.children)
    return count


def render_ui_tree(
    device: Device,
    nodes: list[UiNode],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool = False,
) -> EnumPopupRequest | None:
    """Render a UiNode list as a tab bar (one tab per UiTab channel)."""
    if not nodes:
        return None
    popup_request: EnumPopupRequest | None = None
    tabs = [n for n in nodes if isinstance(n, UiTab)]
    if tabs:
        if imgui.begin_tab_bar(f"##tabs_{device.node_id}"):
            for tab in tabs:
                label = tab.text or tab.name or tab.id or "Tab"
                if imgui.begin_tab_item(f"{label}##{device.node_id}_{tab.id}")[0]:
                    req = _render_children(
                        device, tab.children, on_change, deferred_enum,
                        f"{device.node_id}_{tab.id}",
                    )
                    if req is not None:
                        popup_request = req
                    imgui.end_tab_item()
            imgui.end_tab_bar()
    else:
        req = _render_children(
            device, tuple(nodes), on_change, deferred_enum, str(device.node_id)
        )
        if req is not None:
            popup_request = req
    return popup_request


def _render_children(
    device: Device,
    children: tuple[UiNode, ...],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    popup_request: EnumPopupRequest | None = None
    pending_params: list[UiParameter] = []
    table_idx = 0

    def flush() -> None:
        nonlocal popup_request, table_idx
        if not pending_params:
            return
        req = _render_param_table(device, pending_params, on_change, deferred_enum, f"{prefix}_{table_idx}")
        table_idx += 1
        if req is not None:
            popup_request = req
        pending_params.clear()

    for node in children:
        if isinstance(node, UiParameter):
            pending_params.append(node)
        elif isinstance(node, UiParameterBlock):
            flush()
            req = _render_block(device, node, on_change, deferred_enum, prefix)
            if req is not None:
                popup_request = req
        elif isinstance(node, UiSeparator):
            flush()
            _render_separator(node)
        elif isinstance(node, UiComObject):
            pass  # shown in the com flags panel

    flush()
    return popup_request


def _render_block(
    device: Device,
    block: UiParameterBlock,
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    block_prefix = f"{prefix}_{block.id}"

    if block.layout in (ParameterBlockLayout.GRID, ParameterBlockLayout.TABLE):
        return _render_grid_block(device, block, on_change, deferred_enum, block_prefix)

    if block.inline:
        return _render_children(device, block.children, on_change, deferred_enum, block_prefix)

    label = block.text or block.name or block.id
    param_count = count_parameters(block.children)
    popup_request: EnumPopupRequest | None = None
    is_open = imgui.tree_node(f"{label}##{block_prefix}")
    imgui.same_line()
    imgui.text_disabled(f"({param_count})")
    if is_open:
        req = _render_children(device, block.children, on_change, deferred_enum, block_prefix)
        if req is not None:
            popup_request = req
        imgui.tree_pop()
    return popup_request


def _render_grid_block(
    device: Device,
    block: UiParameterBlock,
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    """Render a GRID/TABLE block: UiParameter.cell holds the "row,col" position."""
    popup_request: EnumPopupRequest | None = None
    cells_by_pos: dict[tuple[int, int], UiParameter] = {}
    labels_by_pos: dict[tuple[int, int], str] = {}
    uncelled: list[UiParameter] = []

    for node in block.children:
        if isinstance(node, UiParameter):
            if node.cell:
                try:
                    r, c = node.cell.split(",")
                    cells_by_pos[(int(r), int(c))] = node
                    continue
                except ValueError:
                    pass
            uncelled.append(node)
        elif isinstance(node, UiSeparator) and node.cell and node.text:
            try:
                r, c = node.cell.split(",")
                labels_by_pos[(int(r), int(c))] = node.text
            except ValueError:
                pass

    if not cells_by_pos and not labels_by_pos:
        return _render_param_table(device, uncelled, on_change, deferred_enum, prefix)

    all_rows = {r for r, _ in cells_by_pos} | {r for r, _ in labels_by_pos}
    all_cols = {c for _, c in cells_by_pos} | {c for _, c in labels_by_pos}
    max_row = max(all_rows, default=1)
    max_col = max(all_cols, default=1)

    is_table = block.layout == ParameterBlockLayout.TABLE
    table_flags = imgui.TableFlags_.no_saved_settings | imgui.TableFlags_.sizing_stretch_prop
    if is_table:
        table_flags |= imgui.TableFlags_.borders | imgui.TableFlags_.row_bg

    has_row_labels = bool(block.row_labels)
    has_col_headers = bool(block.column_headers)
    col_offset = 1 if has_row_labels else 0
    declared_cols = max(max_col, len(block.column_headers))
    total_cols = declared_cols + col_offset

    if imgui.begin_table(f"##grid_{prefix}", total_cols, table_flags):
        if is_table and (has_row_labels or has_col_headers):
            if has_row_labels:
                imgui.table_setup_column(block.text or block.name or "")
            for header in block.column_headers:
                imgui.table_setup_column(header)
            for _ in range(declared_cols - len(block.column_headers)):
                imgui.table_setup_column("")
            imgui.table_headers_row()
        elif is_table:
            imgui.table_headers_row()
        for row in range(1, max_row + 1):
            imgui.table_next_row()
            if has_row_labels:
                imgui.table_set_column_index(0)
                label = block.row_labels[row - 1] if row - 1 < len(block.row_labels) else ""
                imgui.text_disabled(label)
            for col in range(1, max_col + 1):
                imgui.table_set_column_index(col - 1 + col_offset)
                param = cells_by_pos.get((row, col))
                label = labels_by_pos.get((row, col))
                if param is not None:
                    imgui.set_next_item_width(-1)
                    widget_id = f"{device.node_id}_{param.ref_id}"
                    req = render_param_widget(
                        param,
                        widget_id,
                        lambda v, d=device, p=param.ref_id: on_change(d, p, v),
                        deferred_enum=deferred_enum,
                    )
                    if req is not None:
                        popup_request = EnumPopupRequest(device=device, param=req.param)
                elif label is not None:
                    imgui.text_disabled(label)
        imgui.end_table()

    if uncelled:
        req = _render_param_table(device, uncelled, on_change, deferred_enum, prefix)
        if req is not None:
            popup_request = req

    return popup_request


def _render_param_table(
    device: Device,
    params: list[UiParameter],
    on_change: Callable[[Device, str, str], None],
    deferred_enum: bool,
    prefix: str,
) -> EnumPopupRequest | None:
    if not params:
        return None
    popup_request: EnumPopupRequest | None = None
    table_flags = imgui.TableFlags_.no_saved_settings
    if imgui.begin_table(f"##params_{prefix}", 2, table_flags):
        imgui.table_setup_column("Name", imgui.TableColumnFlags_.width_stretch)
        imgui.table_setup_column("Value", imgui.TableColumnFlags_.width_fixed, 120)
        for param in params:
            imgui.table_next_row()
            imgui.table_set_column_index(0)
            indent = param.indent_level * 12.0
            if indent > 0:
                imgui.indent(indent)
            imgui.text(param.label)
            if param.suffix:
                imgui.same_line()
                imgui.text_disabled(param.suffix)
            if indent > 0:
                imgui.unindent(indent)
            imgui.table_set_column_index(1)
            imgui.set_next_item_width(-1)
            widget_id = f"{device.node_id}_{param.ref_id}"
            req = render_param_widget(
                param,
                widget_id,
                lambda v, d=device, p=param.ref_id: on_change(d, p, v),
                deferred_enum=deferred_enum,
            )
            if req is not None:
                popup_request = EnumPopupRequest(device=device, param=req.param)
        imgui.end_table()
    return popup_request


def _render_separator(sep: UiSeparator) -> None:
    if sep.text:
        imgui.separator_text(sep.text)
    else:
        imgui.separator()


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

    def request(self, device: Device, param: UiParameter) -> None:
        self._request = EnumPopupRequest(device=device, param=param)

    def render(self) -> None:
        if self._request is not None:
            self._active = self._request
            self._request = None
            imgui.open_popup(self._popup_id)

        if imgui.begin_popup(self._popup_id):
            target = self._active
            if target is not None and isinstance(target.param.widget, EnumWidget):
                for choice in target.param.widget.choices:
                    selected = str(choice.value) == target.param.value
                    if imgui.menu_item(choice.label, "", selected)[0]:
                        self._on_change(target.device, target.param.ref_id, str(choice.value))
            imgui.end_popup()
        else:
            self._active = None
