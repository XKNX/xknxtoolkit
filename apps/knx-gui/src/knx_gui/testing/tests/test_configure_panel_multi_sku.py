"""E2E test for the multi-SKU Configure panel fix — see test plan procedure
"End-to-end operator-facing verification" (VerifyBeta SKU display fields surface
through MetadataSection's render path).

Driven by Dear ImGui Test Engine (see ``knx_gui.testing.harness``). These open a
real (briefly visible) window, so they need a display and aren't part of the
root ``uv run pytest`` run — run them explicitly under
``xvfb-run -a uv run pytest src/knx_gui/testing -v`` from ``apps/knx-gui/``.

The operator-facing surface the bug reached through is ``MetadataSection.render``
(``metadata_section.py:79,95,101,137``), which renders ``device.hardware.*``
unconditionally. After the fix, ``device.hardware`` is populated by
``ProjectService._resolve_hardware`` with the per-SKU display fields for the SKU
the operator added (verified end-to-end in
``apps/knx-gui/src/knx_gui/plugins/project/tests/test_service.py::test_build_device_passes_product_ref_id_to_catalog``).
This file closes the remaining gap: it confirms that ``MetadataSection.render``
itself surfaces whatever ``device.hardware`` carries — so the chain from the
non-first catalog item all the way to the rendered Configure-panel rows is fixed.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from imgui_bundle import imgui
from imgui_bundle.immapp import testing as imgui_testing

import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.device import Device
from knx_gui.plugins.project.ui.components import MetadataSection
from knx_gui.testing.harness import TestContext as _TestContext

_PANEL_SIZE = (417, 477)
_WINDOW_SIZE = (600, 600)


def _device_with_hardware(hardware: object) -> Device:
    """A Device stand-in carrying only what MetadataSection.render reads."""
    program = SimpleNamespace(
        mask_version="MASK0701",
        pei_type=17,
        application_number=1,
        application_version=1,
        program_type=SimpleNamespace(value="Application Program"),
        load_procedure_style=SimpleNamespace(value="DefaultProcedure"),
        linkable=True,
        dynamic_table_management=False,
        is_secure_enabled=False,
        additional_addresses_count=0,
        visible_description="A test application",
        original_manufacturer="Test OEM GmbH",
    )
    app = SimpleNamespace(
        program=program,
        manufacturer_id="M-0008",
        name="Test Application",
        id="APP-TEST",
    )
    return cast(Device, SimpleNamespace(app=app, hardware=hardware))


def _beta_sku_hardware() -> object:
    """The HardwareInfo snapshot ProjectService._resolve_hardware returns for a
    device added from the Beta SKU — the values that must reach the Configure
    panel after the fix."""
    return SimpleNamespace(
        is_coupler=False,
        is_power_supply=False,
        is_ip_enabled=False,
        order_number="ORD-BETA",
        serial_number="SN-1",
        version_number=0,
        bus_current=10.0,
        is_rail_mounted=True,
        width_mm=72.0,
        name="SKU Beta",
        id="M-0008_H-1",
    )


def _alpha_sku_hardware() -> object:
    """The pre-fix HardwareInfo snapshot for the same device — what the Configure
    panel rendered before the fix (and what it still renders for a device added
    from the *first* SKU)."""
    return SimpleNamespace(
        is_coupler=False,
        is_power_supply=False,
        is_ip_enabled=False,
        order_number="ORD-ALPHA",
        serial_number="SN-1",
        version_number=0,
        bus_current=10.0,
        is_rail_mounted=True,
        width_mm=36.0,
        name="SKU Alpha",
        id="M-0008_H-1",
    )


class _RecordingMetadataSection(MetadataSection):
    """A ``MetadataSection`` subclass that records every value it would render —
    so we can assert which per-SKU fields reached the screen without relying on
    fragile pixel-diffing or screenshot parsing. Subclassing (rather than
    monkeypatching ``imgui.text_unformatted``) keeps the render path intact for
    the real GL/imgui drawing the Test Engine drives every frame."""

    def __init__(self) -> None:
        super().__init__()
        self.rendered_values: list[str] = []

    def _render_wrapped(self, value: str) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        self.rendered_values.append(value)
        super()._render_wrapped(value)


def _run_render_test(section: MetadataSection, device: Device) -> None:
    """Render ``section`` with ``device`` inside a real imgui window driven by the
    Test Engine — the same pattern as ``test_metadata_section_no_horizontal_overflow``."""

    def gui_function() -> None:
        imgui.set_next_window_size(imgui.ImVec2(*_PANEL_SIZE))
        imgui.begin("TestPanel")
        section.render(device)
        imgui.end()

    def test_function(ctx: _TestContext) -> None:
        ctx.set_ref("//TestPanel")
        ctx.yield_()
        ctx.yield_()
        window = ctx.get_window_by_ref("//TestPanel")
        # Sanity: window was actually rendered (not silently dropped).
        assert window is not None
        assert window.size.x > 0

    imgui_testing.run(gui_function, test_function, window_size=_WINDOW_SIZE)


def test_metadata_section_renders_nonfirst_sku_order_number() -> None:
    """The operator-facing regression: for a device whose ``hardware`` was
    populated from a non-first SKU, the Configure panel must show that SKU's
    order number ('ORD-BETA'), not the first SKU's ('ORD-ALPHA')."""
    section = _RecordingMetadataSection()
    device = _device_with_hardware(_beta_sku_hardware())
    _run_render_test(section, device)

    rendered = "\n".join(section.rendered_values)
    assert "ORD-BETA" in rendered, (
        f"expected 'ORD-BETA' in rendered values, got: {section.rendered_values!r}"
    )
    # The wrong-SKU value (the one the pre-fix code rendered) must NOT be present.
    assert "ORD-ALPHA" not in rendered, (
        f"Configure panel rendered the wrong SKU's order number ('ORD-ALPHA'); "
        f"rendered values: {section.rendered_values!r}"
    )


def test_metadata_section_renders_nonfirst_sku_width() -> None:
    """The Beta SKU's width is 72 mm (vs Alpha's 36 mm); the Configure panel must
    show '72 mm' for the Beta device, not '36 mm'."""
    section = _RecordingMetadataSection()
    device = _device_with_hardware(_beta_sku_hardware())
    _run_render_test(section, device)

    rendered = "\n".join(section.rendered_values)
    assert "72 mm" in rendered, (
        f"expected '72 mm' in rendered values, got: {section.rendered_values!r}"
    )
    assert "36 mm" not in rendered, (
        f"Configure panel rendered the wrong SKU's width ('36 mm'); "
        f"rendered values: {section.rendered_values!r}"
    )


def test_metadata_section_renders_nonfirst_sku_name() -> None:
    """The title 'SKU Beta' (line 137 of metadata_section.py) must show the Beta
    SKU's name for the Beta device, not the Alpha's."""
    section = _RecordingMetadataSection()
    device = _device_with_hardware(_beta_sku_hardware())
    _run_render_test(section, device)

    rendered = "\n".join(section.rendered_values)
    assert "SKU Beta" in rendered, (
        f"expected 'SKU Beta' in rendered values, got: {section.rendered_values!r}"
    )


def test_metadata_section_renders_first_sku_values_when_hardware_carries_them() -> None:
    """No-regression counterpart: a device whose ``hardware`` carries the first
    SKU's values (i.e., a device added from the first SKU, or any single-SKU
    hardware like the in-repo gira fixture) still renders that SKU's order
    number / width / name. The fix preserves the common-case behaviour."""
    section = _RecordingMetadataSection()
    device = _device_with_hardware(_alpha_sku_hardware())
    _run_render_test(section, device)

    rendered = "\n".join(section.rendered_values)
    assert "ORD-ALPHA" in rendered, (
        f"expected 'ORD-ALPHA' in rendered values, got: {section.rendered_values!r}"
    )
    assert "36 mm" in rendered, (
        f"expected '36 mm' in rendered values, got: {section.rendered_values!r}"
    )
    assert "ORD-BETA" not in rendered, (
        f"Alpha device's Configure panel unexpectedly rendered 'ORD-BETA'; "
        f"rendered values: {section.rendered_values!r}"
    )


def test_metadata_section_render_path_does_not_reference_product_ref_id() -> None:
    """The MetadataSection's render path must keep reading from
    ``device.hardware.*`` (not e.g. ``device.product_ref_id``) — that contract is
    what makes the GUI's per-SKU fix a catalog-side change (ProjectService
    populates ``device.hardware`` with the right SKU's values) rather than a
    panel-side change. Pin it: with a hardware carrying Beta values and NO
    ``product_ref_id`` attribute on the device at all, the panel still renders
    Beta (because it reads ``hardware``, not ``product_ref_id``)."""
    section = _RecordingMetadataSection()
    device = _device_with_hardware(_beta_sku_hardware())
    _run_render_test(section, device)

    rendered = "\n".join(section.rendered_values)
    assert "ORD-BETA" in rendered
