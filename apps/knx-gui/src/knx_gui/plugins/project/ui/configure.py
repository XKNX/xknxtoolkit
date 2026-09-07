from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S
from knx_gui.widgets import (
    ComFlagsTable,
    count_parameters,
    render_bounded_numeric_segment,
    render_ui_tree,
)
from xknxmono.project.core.addressing import format_ia, parse_ia

if TYPE_CHECKING:
    from xknxmono.catalog import ManufacturerInfo

# KNX v01.03.02 - Data Link Layer General - §1.4.2, Figure 2: Individual
# Address is a 16 bit value, Octet 0 = 4 bit Area + 4 bit Line, Octet 1 =
# the full 8 bit Device Address.
_MAX_AREA = 15
_MAX_LINE = 15
_MAX_DEVICE = 255

# Extra breathing room after a metadata label's own text, before its value column.
_COLUMN_PADDING = 24.0


@dataclass(frozen=True)
class _ResetMode:
    """One selectable entry in the reset-mode dropdown.

    ``erase_code`` is only meaningful when ``master_reset`` is True - see
    KNX v02.01.02 - Management Procedures 03.05.02 - §3.7.1.2.3.1, Table 4.
    ``destructive`` marks every mode that actually resets a Resource -
    anything but Basic Restart and Confirmed Restart - and gates the
    confirmation popup.

    Table 4 lets several of these Erase Codes scope to a single Channel
    Number instead of the whole device; there's no UI for that yet, so
    every request is sent with Channel Number 00h ("all Channels"), which
    every Erase Code accepts.
    """

    label: str
    master_reset: bool
    erase_code: int
    destructive: bool


def _reset_modes() -> list[_ResetMode]:
    """Build the dropdown entries fresh so labels pick up the current locale."""
    return [
        _ResetMode(S.RESET_MODE_BASIC_RESTART, False, 0, False),
        _ResetMode(S.RESET_MODE_CONFIRMED_RESTART, True, 0x01, False),
        _ResetMode(S.RESET_MODE_FACTORY_RESET, True, 0x02, True),
        _ResetMode(S.RESET_MODE_RESET_IA, True, 0x03, True),
        _ResetMode(S.RESET_MODE_RESET_AP, True, 0x04, True),
        _ResetMode(S.RESET_MODE_RESET_PARAM, True, 0x05, True),
        _ResetMode(S.RESET_MODE_RESET_LINKS, True, 0x06, True),
        _ResetMode(S.RESET_MODE_FACTORY_RESET_NO_IA, True, 0x07, True),
        _ResetMode(S.RESET_MODE_ERASE_APP_DATA, True, 0x08, True),
    ]


@dataclass(frozen=True)
class RestartRequest:
    """Parameters for one restart/reset call, matching dm_restart's own signature."""

    master_reset: bool
    erase_code: int
    channel_number: int


def _yes_no(value: bool) -> str:
    return S.YES if value else S.NO


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
        self._on_restart_device = on_restart_device
        self._get_manufacturer = get_manufacturer
        self._com_flags_table = ComFlagsTable(set_flag)
        self._name_buffer: str = ""
        self._ia_area: str = ""
        self._ia_line: str = ""
        self._ia_device: str = ""
        self._buffer_device_id: int | None = None
        self._reset_mode_index: int = 0

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
            self._render_metadata_section(device)

        if self._on_restart_device is not None and imgui.collapsing_header(
            S.CONFIGURE_RESET_SECTION
        ):
            self._render_restart_controls(device)

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

    def _clip_text(self, text: str, max_width: float) -> str:
        """Truncate `text` with an ellipsis so it fits `max_width`, or return it unchanged."""
        if imgui.calc_text_size(text).x <= max_width:
            return text
        if max_width <= 0:
            return ""
        ellipsis = "..."
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if imgui.calc_text_size(text[:mid] + ellipsis).x <= max_width:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + ellipsis

    def _render_clipped(self, value: str) -> None:
        """Render `value` clipped to the space left on the current line, with a hover
        tooltip showing the full text if it had to be clipped."""
        display = self._clip_text(value, imgui.get_content_region_avail().x)
        imgui.text(display)
        if display != value and imgui.is_item_hovered():
            imgui.set_tooltip(value)

    def _render_label_value(self, label: str, value: str, column: float) -> None:
        imgui.text_disabled(label)
        imgui.same_line(column)
        self._render_clipped(value)

    def _render_section_title(self, title: str) -> None:
        imgui.text(title)

    def _render_name_and_id(
        self, label: str, name: str | None, id_: str, column: float
    ) -> None:
        """Render "label: name" and "ID: id" as two full-width rows, each independently
        clipped - or just "ID: id" if there's no separate name."""
        if name and name != id_:
            self._render_label_value(label, name, column)
        self._render_label_value(S.CONFIGURE_ID, id_, column)

    def _render_fields(
        self, fields: list[tuple[str, str | None]], column: float
    ) -> None:
        """Render each (label, value) pair, skipping any with no value to show."""
        for label, value in fields:
            if value:
                self._render_label_value(label, value, column)

    def _label_column(self, labels: list[str]) -> float:
        """The x-position for values so every label in `labels` fits without collision.

        `same_line(x)`'s x is measured from the window's own left edge, not from the
        current line's start - so it ignores indent. Every caller renders this column
        one `imgui.indent()` level in, so the label itself (which *does* shift right
        with indent) needs that indent added back on top of its own width, or the
        value can land on top of the label's tail.

        Not capped against the available width: `labels` is a small, fixed set of UI
        strings, so this is naturally bounded (unlike the value side, which is
        arbitrary data and is clipped independently in `_render_clipped`) - a cap here
        previously clamped the column *below* a label's own width in a narrow panel,
        which guaranteed the collision it was meant to prevent.
        """
        widest = max((imgui.calc_text_size(label).x for label in labels), default=0.0)
        indent = imgui.get_style().indent_spacing
        return widest + indent + _COLUMN_PADDING

    def _render_metadata_section(self, device: Device) -> None:
        app = device.app
        program = app.program
        hardware = device.hardware

        manufacturer = self._get_manufacturer(app.manufacturer_id)

        program_fields: list[tuple[str, str | None]] = [
            (S.CONFIGURE_MASK_VERSION, program.mask_version),
            (S.CONFIGURE_PEI_TYPE, str(program.pei_type)),
            (S.CONFIGURE_APPLICATION_NUMBER, str(program.application_number)),
            (S.CONFIGURE_APPLICATION_VERSION, str(program.application_version)),
            (S.CONFIGURE_PROGRAM_TYPE, program.program_type.value),
            (S.CONFIGURE_LOAD_PROCEDURE_STYLE, program.load_procedure_style.value),
            (S.CONFIGURE_LINKABLE, _yes_no(program.linkable)),
            (
                S.CONFIGURE_DYNAMIC_TABLE_MANAGEMENT,
                _yes_no(program.dynamic_table_management),
            ),
            (S.CONFIGURE_SECURE_ENABLED, _yes_no(program.is_secure_enabled)),
            (
                S.CONFIGURE_ADDITIONAL_ADDRESSES,
                str(program.additional_addresses_count)
                if program.additional_addresses_count
                else None,
            ),
            (S.CONFIGURE_DESCRIPTION, program.visible_description),
            (S.CONFIGURE_ORIGINAL_MANUFACTURER, program.original_manufacturer),
        ]

        hardware_fields: list[tuple[str, str | None]] = []
        if hardware is not None:
            roles = [
                label
                for flag, label in (
                    (hardware.is_coupler, S.ROLE_COUPLER),
                    (hardware.is_power_supply, S.ROLE_POWER_SUPPLY),
                    (hardware.is_ip_enabled, S.ROLE_IP_ENABLED),
                )
                if flag
            ]
            hardware_fields = [
                (S.CONFIGURE_ORDER_NUMBER, hardware.order_number),
                (S.CONFIGURE_SERIAL_NUMBER, hardware.serial_number),
                (
                    S.CONFIGURE_VERSION_NUMBER,
                    str(hardware.version_number)
                    if hardware.version_number is not None
                    else None,
                ),
                (
                    S.CONFIGURE_BUS_CURRENT,
                    f"{hardware.bus_current:g} mA"
                    if hardware.bus_current is not None
                    else None,
                ),
                (
                    S.CONFIGURE_RAIL_MOUNTED,
                    _yes_no(hardware.is_rail_mounted)
                    if hardware.is_rail_mounted is not None
                    else None,
                ),
                (
                    S.CONFIGURE_WIDTH,
                    f"{hardware.width_mm:g} mm"
                    if hardware.width_mm is not None
                    else None,
                ),
                (
                    S.CONFIGURE_ROLE,
                    ", ".join(roles) if roles else S.ROLE_END_DEVICE,
                ),
            ]

        column = self._label_column(
            [S.CONFIGURE_NAME, S.CONFIGURE_ID]
            + [label for label, _ in program_fields]
            + [label for label, _ in hardware_fields]
        )

        self._render_section_title(S.CONFIGURE_MANUFACTURER)
        imgui.indent()
        self._render_name_and_id(
            S.CONFIGURE_NAME,
            manufacturer.name if manufacturer else None,
            app.manufacturer_id,
            column,
        )
        imgui.unindent()

        self._render_section_title(S.CONFIGURE_APPLICATION)
        imgui.indent()
        self._render_name_and_id(S.CONFIGURE_NAME, app.name, app.id, column)
        self._render_fields(program_fields, column)
        imgui.unindent()

        if hardware is not None:
            self._render_section_title(S.CONFIGURE_HARDWARE)
            imgui.indent()
            self._render_name_and_id(
                S.CONFIGURE_NAME, hardware.name, hardware.id, column
            )
            self._render_fields(hardware_fields, column)
            imgui.unindent()

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

    def _render_restart_controls(self, device: Device) -> None:
        modes = _reset_modes()
        mode_labels = [mode.label for mode in modes]

        imgui.text(S.CONFIGURE_RESET_HEADER)
        imgui.indent()

        imgui.set_next_item_width(220)
        _, self._reset_mode_index = imgui.combo(
            "##reset_mode", self._reset_mode_index, mode_labels
        )
        selected = modes[self._reset_mode_index]

        button_size = imgui.ImVec2(110, 0)
        imgui.same_line()
        avail = imgui.get_content_region_avail().x
        if avail > button_size.x:
            imgui.set_cursor_pos_x(imgui.get_cursor_pos_x() + avail - button_size.x)
        enabled = bool(device.individual_address)
        imgui.begin_disabled(not enabled)
        if imgui.button(S.BTN_RESET, button_size):
            if selected.destructive:
                imgui.open_popup(S.POPUP_CONFIRM_RESET_TITLE)
            else:
                self._do_restart(device, selected)
        imgui.end_disabled()

        imgui.unindent()

        # Called right after the button so a same-frame open_popup() (above)
        # is seen by this begin_popup_modal() before the frame ends - no
        # need to defer opening it to the next frame.
        self._render_reset_confirm_popup(device, selected)

    def _render_reset_confirm_popup(self, device: Device, selected: _ResetMode) -> None:
        if imgui.begin_popup_modal(
            S.POPUP_CONFIRM_RESET_TITLE, flags=imgui.WindowFlags_.always_auto_resize
        )[0]:
            imgui.text(
                S.POPUP_CONFIRM_RESET_TEXT.format(
                    mode=selected.label, device=device.name
                )
            )
            imgui.separator()
            if imgui.button(S.BTN_RESET, imgui.ImVec2(75, 0)):
                self._do_restart(device, selected)
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button(S.BTN_CANCEL, imgui.ImVec2(75, 0)):
                imgui.close_current_popup()
            imgui.end_popup()

    def _do_restart(self, device: Device, mode: _ResetMode) -> None:
        if self._on_restart_device is not None:
            self._on_restart_device(
                device,
                RestartRequest(
                    master_reset=mode.master_reset,
                    erase_code=mode.erase_code,
                    channel_number=0,
                ),
            )
