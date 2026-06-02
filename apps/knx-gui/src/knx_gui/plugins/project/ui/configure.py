from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.plugins.project.strings import S
from knx_gui.types import Device
from knx_gui.widgets import (
    ComFlagsTable,
    render_parameters_grouped,
    render_parameters_tree,
)


class ConfigurePanel:
    def __init__(
        self,
        get_devices: Callable[[], list[Device]],
        get_selected_device: Callable[[], Device | None],
        set_selected_device: Callable[[Device], None],
        on_param_change: Callable[[Device, str, str], None],
        on_individual_address_change: Callable[[Device, str], None],
        on_name_change: Callable[[Device, str], None],
        set_flag: Callable[[Device, str, str, bool], None],
        on_program_device: Callable[[Device], None] | None = None,
    ) -> None:
        self._get_devices = get_devices
        self._get_selected_device = get_selected_device
        self._set_selected_device = set_selected_device
        self._on_param_change = on_param_change
        self._on_individual_address_change = on_individual_address_change
        self._on_name_change = on_name_change
        self._on_program_device = on_program_device
        self._com_flags_table = ComFlagsTable(set_flag)
        self._name_buffer: str = ""
        self._address_buffer: str = ""
        self._buffer_device_id: int | None = None

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
            label = (
                f"{d.name} ({d.individual_address})" if d.individual_address else d.name
            )
            labels.append(label)
            if d.node_id == device.node_id:
                current_idx = i

        imgui.set_next_item_width(-1)
        changed, new_idx = imgui.combo("##device_select", current_idx, labels)
        if changed:
            self._set_selected_device(devices[new_idx])
            device = devices[new_idx]

        imgui.separator()

        if self._buffer_device_id != device.node_id:
            self._name_buffer = device.name
            self._address_buffer = device.individual_address
            self._buffer_device_id = device.node_id

        imgui.align_text_to_frame_padding()
        imgui.text_disabled(S.CONFIGURE_NAME)
        imgui.same_line(120.0)
        imgui.set_next_item_width(-1)
        _, self._name_buffer = imgui.input_text("##name", self._name_buffer)
        if imgui.is_item_deactivated_after_edit():
            self._on_name_change(device, self._name_buffer)
        if not imgui.is_item_active() and self._name_buffer != device.name:
            self._name_buffer = device.name

        imgui.align_text_to_frame_padding()
        imgui.text_disabled(S.CONFIGURE_INDIVIDUAL_ADDRESS)
        imgui.same_line(120.0)
        imgui.set_next_item_width(-1)
        _, self._address_buffer = imgui.input_text(
            "##individual_address", self._address_buffer
        )
        if imgui.is_item_deactivated_after_edit():
            self._on_individual_address_change(device, self._address_buffer)
        if (
            not imgui.is_item_active()
            and self._address_buffer != device.individual_address
        ):
            self._address_buffer = device.individual_address

        if self._on_program_device is not None:
            enabled = bool(device.individual_address)
            imgui.begin_disabled(not enabled)
            if imgui.button(S.BTN_PROGRAM_DEVICE):
                self._on_program_device(device)
            imgui.end_disabled()

        if imgui.collapsing_header(
            S.CONFIGURE_MANUFACTURER, imgui.TreeNodeFlags_.default_open
        ):
            self._render_label_value(
                S.CONFIGURE_MANUFACTURER, device.app.manufacturer_id
            )
            self._render_label_value(S.CONFIGURE_APPLICATION, device.app.id)

        params = device.get_visible_parameters()
        if params and imgui.collapsing_header(
            S.CONFIGURE_PARAMETERS.format(count=len(params)),
            imgui.TreeNodeFlags_.default_open,
        ):
            tree = device.get_visible_tree()
            if tree:
                render_parameters_tree(device, tree, self._on_param_change)
            else:
                render_parameters_grouped(device, params, self._on_param_change)

        visible_cos = device.get_visible_com_objects()
        if imgui.collapsing_header(
            S.CONFIGURE_COM_FLAGS.format(count=len(visible_cos)),
            imgui.TreeNodeFlags_.default_open,
        ):
            self._com_flags_table.render(device, visible_cos)

        lp = device.app.load_procedures
        if lp is not None:
            total_steps = sum(len(p.steps) for p in lp.procedures)
            if imgui.collapsing_header(
                S.CONFIGURE_LOAD_PROCEDURES.format(count=total_steps)
            ):
                imgui.text_disabled(lp.style)
                for i, proc in enumerate(lp.procedures):
                    label = f"Procedure {i + 1}  ({len(proc.steps)} steps)##lp{i}"
                    if imgui.tree_node(label):
                        _table_flags = (
                            imgui.TableFlags_.borders_outer
                            | imgui.TableFlags_.borders_inner_v
                            | imgui.TableFlags_.sizing_stretch_prop
                        )
                        if imgui.begin_table(f"##lpt{i}", 3, _table_flags):
                            imgui.table_setup_column(
                                "Kind", imgui.TableColumnFlags_.width_stretch, 0.3
                            )
                            imgui.table_setup_column(
                                "Applies To",
                                imgui.TableColumnFlags_.width_stretch,
                                0.15,
                            )
                            imgui.table_setup_column(
                                "Details", imgui.TableColumnFlags_.width_stretch, 0.55
                            )
                            imgui.table_headers_row()
                            for step in proc.steps:
                                imgui.table_next_row()
                                imgui.table_set_column_index(0)
                                imgui.text(step.kind)
                                imgui.table_set_column_index(1)
                                imgui.text_disabled(step.applies_to)
                                imgui.table_set_column_index(2)
                                imgui.text_disabled(step.details)
                            imgui.end_table()
                        imgui.tree_pop()

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(120.0)
        imgui.text(value)
