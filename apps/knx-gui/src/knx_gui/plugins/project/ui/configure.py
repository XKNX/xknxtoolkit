from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S
from xknxmono.download.scope import DownloadScope

if TYPE_CHECKING:
    from xknxmono.project.core.service import DeviceInfo
from knx_gui.widgets import (
    GroupObjectsTable,
    count_parameters,
    render_ui_tree,
)
from knx_gui.widgets.group_objects_widgets import (
    GroupAddressCatalog,
    GroupLinkResolver,
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
        get_links_for_com_object: GroupLinkResolver,
        get_all_group_addresses: GroupAddressCatalog,
        on_link_com_object: Callable[[int, int], None],
        on_unlink_com_object: Callable[[int], None],
        get_device_info: "Callable[[int], DeviceInfo | None]",
        on_program_device: Callable[[Device, DownloadScope], None] | None = None,
        on_eval_device: Callable[[Device, DownloadScope], None] | None = None,
        open_memory_preview: Callable[[Device], None] | None = None,
    ) -> None:
        self._get_devices = get_devices
        self._get_selected_device = get_selected_device
        self._set_selected_device = set_selected_device
        self._on_param_change = on_param_change
        self._on_individual_address_change = on_individual_address_change
        self._on_name_change = on_name_change
        self._on_program_device = on_program_device
        self._on_eval_device = on_eval_device
        self._open_memory_preview = open_memory_preview
        self._get_links = get_links_for_com_object
        self._get_all_gas = get_all_group_addresses
        self._get_device_info = get_device_info
        self._group_objects_table = GroupObjectsTable(
            set_flag, on_link_com_object, on_unlink_com_object
        )
        self._name_buffer: str = ""
        self._address_buffer: str = ""
        self._buffer_device_id: int | None = None
        self._download_scope: DownloadScope = DownloadScope.FULL
        self._confirm_program_open: bool = False

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
        labels: list[str] = []
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

        if self._on_program_device is not None or self._on_eval_device is not None:
            self._render_scope_selector()

        # Workflow order: dry run (preview changes) → preview memory image → program.
        if self._on_eval_device is not None:
            enabled = bool(device.individual_address)
            imgui.begin_disabled(not enabled)
            if imgui.button(S.BTN_EVAL_DEVICE):
                self._on_eval_device(device, self._download_scope)
            imgui.end_disabled()
            imgui.same_line()

        if self._open_memory_preview is not None:
            if imgui.button(S.BTN_PREVIEW_MEMORY):
                self._open_memory_preview(device)
            imgui.same_line()

        if self._on_program_device is not None:
            enabled = bool(device.individual_address)
            imgui.begin_disabled(not enabled)
            if imgui.button(S.BTN_PROGRAM_DEVICE):
                # Programming writes to the device; confirm first (like ETS).
                self._confirm_program_open = True
            imgui.end_disabled()
            if self._confirm_program_open:
                imgui.open_popup(S.PROGRAM_CONFIRM_TITLE)
                self._confirm_program_open = False
            self._render_program_confirm(device)

        if imgui.collapsing_header(
            S.CONFIGURE_MANUFACTURER, imgui.TreeNodeFlags_.default_open
        ):
            info = self._get_device_info(device.node_id)
            manufacturer = (
                info.manufacturer_name if info and info.manufacturer_name else None
            )
            self._render_label_value(
                S.CONFIGURE_MANUFACTURER, manufacturer or device.app.manufacturer_id
            )
            self._render_label_value(S.CONFIGURE_APPLICATION, device.app.id)
            if info is not None:
                if info.order_number:
                    self._render_label_value(
                        S.CONFIGURE_ORDER_NUMBER, info.order_number
                    )
                if info.hardware_name:
                    self._render_label_value(S.CONFIGURE_HARDWARE, info.hardware_name)
                if info.description:
                    self._render_label_value(S.CONFIGURE_DESCRIPTION, info.description)

        if imgui.begin_tab_bar("##editor_tabs"):
            ui_nodes = device.get_ui()
            param_count = count_parameters(ui_nodes)
            if imgui.begin_tab_item(S.EDITOR_TAB_PARAMETERS.format(count=param_count))[
                0
            ]:
                if ui_nodes:
                    render_ui_tree(device, ui_nodes, self._on_param_change)
                else:
                    imgui.text_disabled(S.CONFIGURE_NO_DEVICES)
                self._render_load_procedures(device)
                imgui.end_tab_item()

            visible_cos = device.get_visible_com_objects()
            if imgui.begin_tab_item(
                S.EDITOR_TAB_GROUP_OBJECTS.format(count=len(visible_cos))
            )[0]:
                self._group_objects_table.render(
                    device, visible_cos, self._get_links, self._get_all_gas
                )
                imgui.end_tab_item()

            imgui.end_tab_bar()

    def _render_load_procedures(self, device: Device) -> None:
        lp = device.app.load_procedures
        procedures = getattr(lp, "procedures", None)
        if not procedures:
            return
        total_steps = sum(len(p.steps) for p in procedures)
        if not imgui.collapsing_header(
            S.CONFIGURE_LOAD_PROCEDURES.format(count=total_steps)
        ):
            return
        imgui.text_disabled(getattr(lp, "style", ""))
        for i, proc in enumerate(procedures):
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
                        "Applies To", imgui.TableColumnFlags_.width_stretch, 0.15
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

    def _render_program_confirm(self, device: Device) -> None:
        if not imgui.begin_popup_modal(
            S.PROGRAM_CONFIRM_TITLE, None, imgui.WindowFlags_.always_auto_resize
        )[0]:
            return
        imgui.text_wrapped(
            S.PROGRAM_CONFIRM_TEXT.format(
                address=device.individual_address or "?",
                scope=self._download_scope.name,
            )
        )
        imgui.spacing()
        btn_w = imgui.ImVec2(140, 0)
        if imgui.button(S.BTN_PROGRAM_DEVICE, btn_w):
            if self._on_program_device is not None:
                self._on_program_device(device, self._download_scope)
            imgui.close_current_popup()
        imgui.same_line()
        if imgui.button(S.BTN_CANCEL, btn_w):
            imgui.close_current_popup()
        imgui.end_popup()

    def _render_scope_selector(self) -> None:
        """Select what a download/eval covers: full, parameters, or group comm."""
        order = [
            DownloadScope.FULL,
            DownloadScope.PARAMETERS,
            DownloadScope.GROUP_COMMUNICATION,
        ]
        labels = [S.SCOPE_FULL, S.SCOPE_PARAMETERS, S.SCOPE_GROUP_COMMUNICATION]
        current = order.index(self._download_scope)
        imgui.align_text_to_frame_padding()
        imgui.text_disabled(S.CONFIGURE_DOWNLOAD_SCOPE)
        imgui.same_line(120.0)
        imgui.set_next_item_width(220.0)
        changed, new_idx = imgui.combo("##download_scope", current, labels)
        if changed:
            self._download_scope = order[new_idx]
