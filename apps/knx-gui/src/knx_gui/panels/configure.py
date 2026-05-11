from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.knxprod import ParamTypeKind
from knx_gui.strings import S
from knx_gui.types import (
    FLAG_LABELS,
    ComObject,
    Device,
    Parameter,
)


class ConfigurePanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        get_selected_device: Callable[[], Device | None],
        set_selected_device: Callable[[Device], None],
        on_param_change: Callable[[Device, str, str], None],
    ) -> None:
        self._get_devices = get_devices
        self._get_selected_device = get_selected_device
        self._set_selected_device = set_selected_device
        self._on_param_change = on_param_change

    def render(self) -> None:
        devices = self._get_devices()
        if not devices:
            imgui.text_disabled(S.CONFIGURE_NO_DEVICES)
            return

        device = self._get_selected_device()
        if device is None:
            device = devices[0]
            self._set_selected_device(device)

        current_idx = 0
        labels = []
        for i, d in enumerate(devices):
            label = f"{d.name} ({d.address})" if d.address else d.name
            labels.append(label)
            if d.node_id == device.node_id:
                current_idx = i

        imgui.set_next_item_width(-1)
        changed, new_idx = imgui.combo("##device_select", current_idx, labels)
        if changed:
            self._set_selected_device(devices[new_idx])
            device = devices[new_idx]

        imgui.separator()

        config = device.template.config
        if imgui.collapsing_header(
            S.CONFIGURE_MANUFACTURER, imgui.TreeNodeFlags_.default_open
        ):
            self._render_label_value(S.CONFIGURE_MANUFACTURER, config.manufacturer)
            self._render_label_value(S.CONFIGURE_APPLICATION, config.application)
            self._render_label_value(S.CONFIGURE_HARDWARE, config.hardware)
            self._render_label_value(S.CONFIGURE_FIRMWARE, config.firmware)

        params = device.get_visible_parameters()
        if params and imgui.collapsing_header(
            S.CONFIGURE_PARAMETERS.format(count=len(params)),
            imgui.TreeNodeFlags_.default_open,
        ):
            self._render_parameters(device, params)

        visible_cos = device.get_visible_com_objects()
        if imgui.collapsing_header(
            S.CONFIGURE_COM_FLAGS.format(count=len(visible_cos)),
            imgui.TreeNodeFlags_.default_open,
        ):
            self._render_com_objects(device, visible_cos)

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(120.0)
        imgui.text(value)

    def _render_parameters(self, device: Device, params: list[Parameter]) -> None:
        groups = self._group_parameters(params)
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
                    imgui.table_setup_column(
                        "Name", imgui.TableColumnFlags_.width_stretch
                    )
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
                        self._render_param_widget(device, param)
                    imgui.end_table()
                imgui.tree_pop()

    def _group_parameters(self, params: list[Parameter]) -> dict[str, list[Parameter]]:
        groups: dict[str, list[Parameter]] = {}
        for param in params:
            text = param.text if param.text else param.name
            prefix = text.split(" - ")[0].strip() if " - " in text else "General"
            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(param)
        return groups

    def _render_param_widget(self, device: Device, param: Parameter) -> None:
        pt = param.param_type
        if pt is None:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._on_param_change(device, param.id, new_value)
            return

        if pt.kind == ParamTypeKind.ENUM:
            current_idx = 0
            for i, opt in enumerate(pt.options):
                if opt.value == param.value:
                    current_idx = i
                    break
            preview = pt.options[current_idx].text if pt.options else param.value
            if imgui.begin_combo(f"##{param.id}", preview):
                for opt in pt.options:
                    selected = opt.value == param.value
                    if imgui.selectable(opt.text, selected)[0]:
                        self._on_param_change(device, param.id, opt.value)
                imgui.end_combo()
        elif pt.kind == ParamTypeKind.CHECKBOX:
            checked = param.value == "1"
            changed, new_checked = imgui.checkbox(f"##{param.id}", checked)
            if changed:
                self._on_param_change(device, param.id, "1" if new_checked else "0")
        elif pt.kind == ParamTypeKind.NUMBER:
            try:
                int_val = int(param.value)
            except ValueError:
                int_val = pt.min_value or 0
            min_v = pt.min_value if pt.min_value is not None else 0
            max_v = pt.max_value if pt.max_value is not None else 65535
            changed, new_val = imgui.drag_int(
                f"##{param.id}", int_val, 1.0, min_v, max_v
            )
            if changed:
                self._on_param_change(device, param.id, str(new_val))
        elif pt.kind == ParamTypeKind.TIME:
            try:
                int_val = int(param.value)
            except ValueError:
                int_val = pt.min_value or 0
            min_v = pt.min_value if pt.min_value is not None else 0
            max_v = pt.max_value if pt.max_value is not None else 86400
            changed, new_val = imgui.drag_int(
                f"##{param.id}", int_val, 1.0, min_v, max_v
            )
            if changed:
                self._on_param_change(device, param.id, str(new_val))
        elif pt.kind == ParamTypeKind.TEXT:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._on_param_change(device, param.id, new_value)
        elif pt.kind == ParamTypeKind.PICTURE:
            imgui.text_disabled(S.NODE_IMAGE_PLACEHOLDER)
        else:
            changed, new_value = imgui.input_text(f"##{param.id}", param.value)
            if changed:
                self._on_param_change(device, param.id, new_value)

    def _render_com_objects(self, device: Device, com_objects: list[ComObject]) -> None:
        flags = imgui.TableFlags_.borders_inner | imgui.TableFlags_.sizing_fixed_fit
        if not imgui.begin_table(
            f"##com_objs_{device.node_id}", 1 + len(FLAG_LABELS), flags
        ):
            return

        imgui.table_setup_column("Name")
        for _attr, letter, _name in FLAG_LABELS:
            imgui.table_setup_column(letter)
        imgui.table_headers_row()

        for com_obj in com_objects:
            self._render_com_object_row(com_obj, f"{device.node_id}_{com_obj.id}")

        imgui.end_table()

    def _render_com_object_row(self, com_object: ComObject, row_id: str) -> None:
        imgui.table_next_row()
        imgui.table_set_column_index(0)
        imgui.text(com_object.name)

        for col, (attr, _letter, full_name) in enumerate(FLAG_LABELS, start=1):
            imgui.table_set_column_index(col)
            current = getattr(com_object.flags, attr)
            locked_attr = f"{attr}_locked"
            is_locked = (
                getattr(com_object.flags, locked_attr, False)
                if attr != "communication"
                else False
            )

            if is_locked:
                imgui.begin_disabled()
            changed, new_value = imgui.checkbox(f"##{row_id}_{attr}", current)
            if changed and not is_locked:
                setattr(com_object.flags, attr, new_value)
            if is_locked:
                imgui.end_disabled()

            if imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_disabled):
                tooltip = (
                    S.TOOLTIP_LOCKED.format(name=full_name) if is_locked else full_name
                )
                imgui.set_tooltip(tooltip)
