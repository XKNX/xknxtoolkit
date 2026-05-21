from collections.abc import Callable
from dataclasses import dataclass

from imgui_bundle import imgui

from xknxmono.product import ParamTypeKind
from xknxmono.product.dynamic import VisibleNode
from knx_gui.plugins.node_editor.strings import S
from knx_gui.types import Device, Parameter


@dataclass
class EnumPopupRequest:
    device: Device
    param: Parameter


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
        changed, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if changed:
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
    elif pt.kind == ParamTypeKind.NUMBER:
        try:
            int_val = int(param.value)
        except ValueError:
            int_val = pt.min_value or 0
        min_v = pt.min_value if pt.min_value is not None else 0
        max_v = pt.max_value if pt.max_value is not None else 65535
        changed, new_val = imgui.drag_int(f"##{widget_id}", int_val, 1.0, min_v, max_v)
        if changed:
            on_change(str(new_val))
    elif pt.kind == ParamTypeKind.TIME:
        try:
            int_val = int(param.value)
        except ValueError:
            int_val = pt.min_value or 0
        min_v = pt.min_value if pt.min_value is not None else 0
        max_v = pt.max_value if pt.max_value is not None else 86400
        changed, new_val = imgui.drag_int(f"##{widget_id}", int_val, 1.0, min_v, max_v)
        if changed:
            on_change(str(new_val))
    elif pt.kind == ParamTypeKind.TEXT:
        changed, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if changed:
            on_change(new_value)
    elif pt.kind == ParamTypeKind.PICTURE:
        imgui.text_disabled(S.NODE_IMAGE_PLACEHOLDER)
    else:
        changed, new_value = imgui.input_text(f"##{widget_id}", param.value)
        if changed:
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
    popup_request: EnumPopupRequest | None = None
    label = f"{node.display_name}##{device.node_id}_{node.id}"

    param_count = _count_params(node)
    is_open = imgui.tree_node(label)
    imgui.same_line()
    imgui.text_disabled(f"({param_count})")

    if is_open:
        if node.param_ref_ids:
            req = _render_param_table(
                device, node.param_ref_ids, params_by_id, on_change, deferred_enum, node.id
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
