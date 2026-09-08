from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui.components import (
    ComFlagsTable,
    LoadProceduresSection,
    MetadataSection,
    RestartRequest,
    RestartSection,
    count_parameters,
    render_ui_tree,
)
from knx_gui.widgets import render_bounded_numeric_segment
from xknxmono.project.core.addressing import format_ia, parse_ia

if TYPE_CHECKING:
    from xknxmono.catalog import ManufacturerInfo

__all__ = ["ConfigurePanel", "RestartRequest"]

# KNX v01.03.02 - Data Link Layer General - §1.4.2, Figure 2: Individual
# Address is a 16 bit value, Octet 0 = 4 bit Area + 4 bit Line, Octet 1 =
# the full 8 bit Device Address.
_MAX_AREA = 15
_MAX_LINE = 15
_MAX_DEVICE = 255


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
        # object, not None: the return value is discarded (fire-and-forget) here, but
        # the real implementation (connection.service.assign_individual_address_for_device)
        # returns a Future[Any] | None.
        on_program_device: Callable[[Device], object] | None = None,
        open_memory_preview: Callable[[Device], None] | None = None,
        on_restart_device: Callable[[Device, RestartRequest], None] | None = None,
        get_manufacturer: Callable[[str], "ManufacturerInfo | None"] = lambda _: None,
    ) -> None:
        self._get_devices = get_devices
        self._get_selected_device = get_selected_device
        self._set_selected_device = set_selected_device
        self._on_param_change = on_param_change
        self._on_individual_address_change = on_individual_address_change
        self._on_name_change = on_name_change
        self._on_program_device = on_program_device
        self._open_memory_preview = open_memory_preview
        self._metadata_section = MetadataSection(get_manufacturer)
        self._com_flags_table = ComFlagsTable(set_flag)
        self._restart_section = (
            RestartSection(on_restart_device) if on_restart_device is not None else None
        )
        self._load_procedures_section = LoadProceduresSection()
        self._name_buffer: str = ""
        self._ia_area: str = ""
        self._ia_line: str = ""
        self._ia_device: str = ""
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
            self._sync_address_buffers(device.individual_address)
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

        area = render_bounded_numeric_segment("##ia_area", self._ia_area, 2, _MAX_AREA)
        self._ia_area = area.value
        self._render_address_separator()

        if area.advance:
            imgui.set_keyboard_focus_here()
        line = render_bounded_numeric_segment("##ia_line", self._ia_line, 2, _MAX_LINE)
        self._ia_line = line.value
        self._render_address_separator()

        if line.advance:
            imgui.set_keyboard_focus_here()
        dev = render_bounded_numeric_segment(
            "##ia_device", self._ia_device, 3, _MAX_DEVICE
        )
        self._ia_device = dev.value

        if area.deactivated or line.deactivated or dev.deactivated:
            self._commit_address(device)
        # Re-sync if the address changed from outside this widget (undo,
        # drag-to-a-new-line, a successful "Program Device") while none of
        # the three segments is being edited right now.
        elif (
            not (area.active or line.active or dev.active)
            and self._assembled_address() != device.individual_address
        ):
            self._sync_address_buffers(device.individual_address)

        if self._on_program_device is not None:
            enabled = bool(device.individual_address)
            imgui.begin_disabled(not enabled)
            if imgui.button(S.BTN_PROGRAM_DEVICE):
                self._on_program_device(device)
            imgui.end_disabled()
            imgui.same_line()

        if self._open_memory_preview is not None and imgui.button(S.BTN_PREVIEW_MEMORY):
            self._open_memory_preview(device)

        if imgui.collapsing_header(
            S.CONFIGURE_METADATA, imgui.TreeNodeFlags_.default_open
        ):
            self._metadata_section.render(device)

        if self._restart_section is not None and imgui.collapsing_header(
            S.CONFIGURE_RESET_SECTION
        ):
            self._restart_section.render(device)

        ui_nodes = device.get_ui()
        param_count = count_parameters(ui_nodes)
        if ui_nodes and imgui.collapsing_header(
            S.CONFIGURE_PARAMETERS.format(count=param_count),
            imgui.TreeNodeFlags_.default_open,
        ):
            render_ui_tree(device, ui_nodes, self._on_param_change)

        visible_cos = device.get_visible_com_objects()
        if imgui.collapsing_header(
            S.CONFIGURE_COM_FLAGS.format(count=len(visible_cos)),
            imgui.TreeNodeFlags_.default_open,
        ):
            self._com_flags_table.render(device, visible_cos)

        lp = device.app.load_procedures
        procedures = getattr(lp, "procedures", None)
        if procedures:
            total_steps = sum(len(p.steps) for p in procedures)
            if imgui.collapsing_header(
                S.CONFIGURE_LOAD_PROCEDURES.format(count=total_steps)
            ):
                self._load_procedures_section.render(lp, procedures)

    def _sync_address_buffers(self, address: str) -> None:
        """Split an "area.line.device" address into the three segment buffers."""
        if address:
            try:
                area, line, device_octet = parse_ia(address)
            except ValueError:
                pass
            else:
                self._ia_area = str(area)
                self._ia_line = str(line)
                self._ia_device = str(device_octet)
                return
        self._ia_area = ""
        self._ia_line = ""
        self._ia_device = ""

    def _assembled_address(self) -> str:
        """The address the three segment buffers currently spell out, or "" if incomplete."""
        if self._ia_area and self._ia_line and self._ia_device:
            return format_ia(
                int(self._ia_area), int(self._ia_line), int(self._ia_device)
            )
        return ""

    def _render_address_separator(self) -> None:
        imgui.same_line(0, 2)
        imgui.align_text_to_frame_padding()
        imgui.text(".")
        imgui.same_line(0, 2)

    def _commit_address(self, device: Device) -> None:
        new_address = self._assembled_address()
        # 0.0.0 is the reserved "unassigned device" placeholder (KNX v01.03.02
        # - Data Link Layer General - §1.4.2: routers use Device Address 0,
        # other devices 1-255) - not a value a configured device should hold.
        if new_address and new_address != "0.0.0":
            self._on_individual_address_change(device, new_address)
