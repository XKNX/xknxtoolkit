"""The Configure panel's Metadata section: Manufacturer/Application/Hardware, each as
a title followed by a "Name: ..." / "ID: ..." row pair and (for Application/Hardware)
their indented detail fields.

See `knx_gui.plugins.project.ui.components` for why this lives here and not in
`knx_gui.widgets`.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from imgui_bundle import imgui

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S

if TYPE_CHECKING:
    from xknxmono.catalog import ManufacturerInfo

# Extra breathing room after a metadata label's own text, before its value column.
_COLUMN_PADDING = 24.0


def _yes_no(value: bool) -> str:
    return S.YES if value else S.NO


class MetadataSection:
    def __init__(
        self,
        get_manufacturer: Callable[[str], ManufacturerInfo | None] = lambda _: None,
    ) -> None:
        self._get_manufacturer = get_manufacturer

    def render(self, device: Device) -> None:
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

    def _render_wrapped(self, value: str) -> None:
        """Render `value` word-wrapped to the space left on the current line."""
        wrap_x = imgui.get_cursor_pos_x() + imgui.get_content_region_avail().x
        imgui.push_text_wrap_pos(wrap_x)
        imgui.text_unformatted(value)
        imgui.pop_text_wrap_pos()

    def _render_label_value(self, label: str, value: str, column: float) -> None:
        imgui.text_disabled(label)
        imgui.same_line(column)
        self._render_wrapped(value)

    def _render_section_title(self, title: str) -> None:
        imgui.text(title)

    def _render_name_and_id(
        self, label: str, name: str | None, id_: str, column: float
    ) -> None:
        """Render "label: name" and "ID: id" as two full-width rows, each independently
        wrapped - or just "ID: id" if there's no separate name."""
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
        arbitrary data and is wrapped independently in `_render_wrapped`) - a cap here
        previously clamped the column *below* a label's own width in a narrow panel,
        which guaranteed the collision it was meant to prevent.
        """
        widest = max((imgui.calc_text_size(label).x for label in labels), default=0.0)
        indent = imgui.get_style().indent_spacing
        return widest + indent + _COLUMN_PADDING
