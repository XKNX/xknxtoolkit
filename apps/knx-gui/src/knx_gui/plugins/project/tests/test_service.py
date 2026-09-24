"""Tests for the GUI ``ProjectService``'s hardware resolution + per-SKU threading.

The Configure panel renders ``order_number`` / ``width_mm`` / ``is_rail_mounted``
directly from ``device.hardware`` (a :class:`HardwareInfo` snapshot). The bug that
this fix closes is that, for a multi-SKU hardware, an operator adding a non-first
SKU saw *another* SKU's order_number/width because ``_resolve_hardware`` resolved
the catalog hardware solely by the device's ``hardware2program_ref_id`` and pulled
the ``Hardware`` row's first-SKU display fields.

The GUI service now threads the project device's ``product_ref_id`` along with the
program ref through ``_resolve_hardware`` and on to ``catalog.get_hardware_by_program``,
so the catalog can return the per-SKU display fields for the SKU the operator
actually added (see the catalog package's ``test_hardware.py`` for the catalog half
of this contract).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

from knx_gui.plugins.catalog.service import CatalogService
from knx_gui.plugins.project.service import ProjectService

if TYPE_CHECKING:
    from collections.abc import Callable

    from xknxmono.catalog import HardwareInfo

_MFR = "M-0008"
_HW = "M-0008_H-1"
_PROG = "M-0008_H-1_HP-1"
_APP = "M-0008_A-1"

_MASTER_XML = (
    b'<?xml version="1.0" encoding="utf-8"?>'
    b'<KNX xmlns="http://knx.org/xml/project/23"></KNX>'
)

ALPHA = ("M-0008_H-1_P-1", "SKU Alpha", "ORD-ALPHA", 36.0)
BETA = ("M-0008_H-1_P-2", "SKU Beta", "ORD-BETA", 72.0)


def _product_xml(p: tuple[str, str, str, float]) -> str:
    pid, name, ord_no, width = p
    return (
        f'<Product Id="{pid}" Text="{name}" OrderNumber="{ord_no}" '
        f'IsRailMounted="true" WidthInMillimeter="{width:g}" />'
    )


def _hardware_xml(products: list[tuple[str, str, str, float]]) -> bytes:
    products_xml = f"<Products>{''.join(_product_xml(p) for p in products)}</Products>"
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Hardware>
        <Hardware Id="{_HW}" Name="Multi-SKU Device" SerialNumber="1" VersionNumber="0"
                  HasIndividualAddress="true" HasApplicationProgram="true">
          {products_xml}
          <Hardware2Programs>
            <Hardware2Program Id="{_PROG}">
              <ApplicationProgramRef RefId="{_APP}" />
            </Hardware2Program>
          </Hardware2Programs>
        </Hardware>
      </Hardware>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _catalog_xml(section_id: str) -> bytes:
    items = "".join(
        f'<CatalogItem Id="M-0008_CI-{i + 1}" Name="Device from {pid}" Number="{i + 1}" '
        f'ProductRefId="{pid}" Hardware2ProgramRefId="{_PROG}" />'
        for i, (pid, *_rest) in enumerate([ALPHA, BETA])
    )
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <Catalog>
        <CatalogSection Id="{section_id}" Name="Test" Number="1">
          {items}
        </CatalogSection>
      </Catalog>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _application_xml(app_id: str) -> bytes:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<KNX xmlns="http://knx.org/xml/project/23">
  <ManufacturerData>
    <Manufacturer RefId="{_MFR}">
      <ApplicationPrograms>
        <ApplicationProgram Id="{app_id}" Name="Test" ApplicationNumber="1"
                             ApplicationVersion="1" ProgramType="ApplicationProgram"
                             MaskVersion="MASK0001" LoadProcedureStyle="DefaultProcedure"
                             PeiType="0" DefaultLanguage="en-US"
                             DynamicTableManagement="false" Linkable="false">
          <Static>
            <Code />
          </Static>
        </ApplicationProgram>
      </ApplicationPrograms>
    </Manufacturer>
  </ManufacturerData>
</KNX>""".encode()


def _build_knxprod_bytes() -> bytes:
    entries = {
        "knx_master.xml": _MASTER_XML,
        f"{_MFR}/Hardware.xml": _hardware_xml([ALPHA, BETA]),
        f"{_MFR}/Catalog.xml": _catalog_xml("M-0008_CS-1"),
        f"{_MFR}/{_APP}.xml": _application_xml(_APP),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def _make_service_with_fake_catalog(
    get_hardware_by_program: Callable[..., HardwareInfo | None],
) -> ProjectService:
    fake = cast(
        CatalogService,
        SimpleNamespace(get_hardware_by_program=get_hardware_by_program),
    )
    return ProjectService(fake)


def test_resolve_hardware_threads_product_ref_id_to_catalog() -> None:
    """When ``product_ref_id`` is supplied, it is passed through to
    ``catalog.get_hardware_by_program`` alongside the program ref."""
    calls: list[tuple[str, str | None]] = []

    def fake_get(program_ref: str, product_ref_id: str | None = None) -> None:
        calls.append((program_ref, product_ref_id))

    service = _make_service_with_fake_catalog(
        cast("Callable[..., HardwareInfo | None]", fake_get)
    )
    resolve = service._resolve_hardware  # pyright: ignore[reportPrivateUsage]

    resolve(_PROG, BETA[0])
    assert calls == [(_PROG, BETA[0])]


def test_resolve_hardware_passes_none_when_no_product_ref_id() -> None:
    """The pre-existing single-arg call (no product_ref_id) still works — callers that
    haven't been updated to pass it stay compatible."""
    calls: list[tuple[str, str | None]] = []

    def fake_get(program_ref: str, product_ref_id: str | None = None) -> None:
        calls.append((program_ref, product_ref_id))

    service = _make_service_with_fake_catalog(
        cast("Callable[..., HardwareInfo | None]", fake_get)
    )
    resolve = service._resolve_hardware  # pyright: ignore[reportPrivateUsage]

    resolve(_PROG, None)
    assert calls == [(_PROG, None)]


def test_resolve_hardware_returns_none_for_none_program_ref_without_catalog_call() -> (
    None
):
    calls: list[tuple[str, str | None]] = []

    def fake_get(program_ref: str, product_ref_id: str | None = None) -> None:
        calls.append((program_ref, product_ref_id))

    service = _make_service_with_fake_catalog(
        cast("Callable[..., HardwareInfo | None]", fake_get)
    )
    resolve = service._resolve_hardware  # pyright: ignore[reportPrivateUsage]

    assert resolve(None, BETA[0]) is None
    assert calls == []


def test_resolve_hardware_cache_is_keyed_by_program_and_product_ref_id() -> None:
    """Cache hits only when both the program ref *and* the product_ref_id match — important
    because one program may back multiple SKUs of a multi-SKU hardware."""
    calls: list[tuple[str, str | None]] = []

    def fake_get(
        program_ref: str, product_ref_id: str | None = None
    ) -> HardwareInfo | None:
        calls.append((program_ref, product_ref_id))
        # Return a distinct value per call so cached identity is observable.
        from xknxmono.catalog import HardwareInfo

        return HardwareInfo(
            id=f"{program_ref}-{product_ref_id}",
            name=None,
            order_number=None,
            serial_number=None,
            version_number=None,
            bus_current=None,
            is_rail_mounted=None,
            width_mm=None,
            is_coupler=None,
            is_power_supply=None,
            is_ip_enabled=None,
        )

    service = _make_service_with_fake_catalog(
        cast("Callable[..., HardwareInfo | None]", fake_get)
    )
    resolve = service._resolve_hardware  # pyright: ignore[reportPrivateUsage]

    first = resolve(_PROG, BETA[0])
    assert len(calls) == 1

    # Same args → cached value, no fresh call.
    same = resolve(_PROG, BETA[0])
    assert same is first
    assert len(calls) == 1

    # Same program, different product_ref_id → fresh lookup (different SKU, different cache slot).
    resolve(_PROG, ALPHA[0])
    assert len(calls) == 2

    # Same args again → cached.
    resolve(_PROG, ALPHA[0])
    assert len(calls) == 2


def test_build_device_passes_product_ref_id_to_catalog(
    tmp_path: Path,
) -> None:
    """End-to-end: a multi-SKU catalog + project, an added device whose product_ref_id
    points at the *non-first* SKU surfaces *that* SKU's order_number/width_mm/is_rail_mounted
    on the device's hardware info — confirming the configure panel render chain now
    sources per-SKU fields correctly.
    """
    from xknxmono.catalog import CatalogService as _CatalogCoreService
    from xknxmono.product import Application

    # 1. Build a real catalog (multi-SKU hardware + catalog items + bundled application).
    catalog_db = tmp_path / "catalog.db"
    core_catalog = _CatalogCoreService(catalog_db)
    core_catalog.import_knxprod(_build_knxprod_bytes())

    # 2. Wrap it as the GUI-facing catalog service.
    gui_catalog = CatalogService(catalog_db)

    # 3. Create a project and add a device whose product_ref_id is the *non-first* SKU
    #    (Beta) — the very case the pre-fix code would have rendered with Alpha's display
    #    fields.
    project_service = ProjectService(gui_catalog)
    project_service.set_logger(_NullLogger())  # type: ignore[arg-type]
    project_service.new(tmp_path / "project.xknx")

    app = gui_catalog.get_application(_APP)
    assert app is not None, "catalog must expose the bundled application program"
    assert isinstance(app, Application)

    device_id = project_service.add_device(
        product_ref_id=BETA[0],
        hardware2program_ref_id=_PROG,
        name="Beta device",
        app=app,
    )
    assert device_id is not None

    # 4. The project device's resolved hardware must reflect *Beta*'s SKU fields —
    #    this is the operator-facing surface (metadata_section.py:79/95/101/137)
    #    renders unconditionally from `device.hardware`.
    [device] = project_service.devices
    hardware = device.hardware
    assert hardware is not None
    assert hardware.order_number == "ORD-BETA"
    assert hardware.width_mm == 72.0
    assert hardware.is_rail_mounted is True
    assert hardware.name == "SKU Beta"
    # Hardware-level fields still come from the Hardware row (unaffected by SKU).
    assert hardware.id == _HW


class _NullLogger:
    """A minimal `Logger` stand-in so ProjectService can emit warnings without dragging in the
    GUI's plugin logger (which depends on the broader app)."""

    def info(self, *args: Any, **kwargs: Any) -> None:
        pass

    def warning(self, *args: Any, **kwargs: Any) -> None:
        pass

    def error(self, *args: Any, **kwargs: Any) -> None:
        pass

    def debug(self, *args: Any, **kwargs: Any) -> None:
        pass
