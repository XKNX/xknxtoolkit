from collections.abc import Callable

from imgui_bundle import imgui

from knx_gui.strings import S
from knx_gui.types import Device
from knx_gui.widgets import ComFlagsTable, render_parameters_grouped


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
        self._com_flags_table = ComFlagsTable(on_flag_change)

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
            self._com_flags_table.render(device, visible_cos)

    def _render_label_value(self, label: str, value: str) -> None:
        imgui.text_disabled(label)
        imgui.same_line(120.0)
        imgui.text(value)
