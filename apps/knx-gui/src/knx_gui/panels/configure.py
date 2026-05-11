from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.widgets import render_parameters_grouped
from knx_gui.strings import S
from knx_gui.types import (
    FLAG_LABELS,
    ComObject,
    Device,
)


class ConfigurePanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        get_selected_device: Callable[[], Device | None],
        set_selected_device: Callable[[Device], None],
        on_param_change: Callable[[Device, str, str], None],
        on_flag_change: Callable[[Device, str, str, bool], None],
    ) -> None:
        self._get_devices = get_devices
        self._get_selected_device = get_selected_device
        self._set_selected_device = set_selected_device
        self._on_param_change = on_param_change
        self._on_flag_change = on_flag_change

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

        if imgui.collapsing_header(
            S.CONFIGURE_MANUFACTURER, imgui.TreeNodeFlags_.default_open
        ):
            self._render_label_value(
                S.CONFIGURE_MANUFACTURER, device.app.manufacturer_id
            )
            self._render_label_value(S.CONFIGURE_APPLICATION, device.app.application_id)

        params = device.get_visible_parameters()
        if params and imgui.collapsing_header(
            S.CONFIGURE_PARAMETERS.format(count=len(params)),
            imgui.TreeNodeFlags_.default_open,
        ):
            render_parameters_grouped(device, params, self._on_param_change)

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
            self._render_com_object_row(
                device, com_obj, f"{device.node_id}_{com_obj.id}"
            )

        imgui.end_table()

    def _render_com_object_row(
        self, device: Device, com_object: ComObject, row_id: str
    ) -> None:
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
                self._on_flag_change(device, com_object.id, attr, new_value)
            if is_locked:
                imgui.end_disabled()

            if imgui.is_item_hovered(imgui.HoveredFlags_.allow_when_disabled):
                tooltip = (
                    S.TOOLTIP_LOCKED.format(name=full_name) if is_locked else full_name
                )
                imgui.set_tooltip(tooltip)
