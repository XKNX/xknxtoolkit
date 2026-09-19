"""White-box tests for the individual-address change flow.

Guards the cache/DB invariant broken by the bug where
``ProjectPlugin._handle_individual_address_change`` mutated the cache-shared
``Device`` *before* the persistence layer accepted the change: when the project
rejected the address (e.g. its ``(area, line)`` doesn't exist in the
installation), the swallowed error left the live ``Device`` stuck on a value the
DB never stored, with no cache invalidation to ever repair it. The fix adds a
``bool`` signal to ``ProjectService.set_device_individual_address`` and only
mutates ``device.individual_address`` once the project has accepted the change.

Drives a real ``ProjectService`` over a real ``xknxmono.project`` SQLite-backed
``_ProjectService`` (no mocks of the persistence layer) so the real
``KeyError``/``ValueError`` rejection paths from
``_ProjectService.set_individual_address`` are exercised end-to-end.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from knx_gui.plugins.base import Logger, PluginAPI
from knx_gui.plugins.catalog.service import CatalogService
from knx_gui.plugins.project.plugin import ProjectPlugin
from knx_gui.plugins.project.service import ProjectService
from xknxmono.product import Application
from xknxmono.project import ProjectService as _ProjectService

# The catalog/product refs are opaque strings as far as the project package is
# concerned (it's ref-only and never reads the catalog); they only need to line
# up with the fake catalog below so the GUI's _build_device can resolve an app.
_HW2PROG = "M-0001_H-x-1_HP-1"
_APP_ID = "M-0001_A-1"
_PRODUCT = "M-0001_H-x-1_P-1"


# --- fakes + helpers --------------------------------------------------------


def _fake_app() -> Application:
    # Device.__post_init__ only reads ``app.program.dynamic``; with None the
    # DynamicUI path is skipped and com_objects comes out empty, which is all
    # _build_device needs. Application is an xsdata-slots dataclass we don't
    # want to construct for a unit test (same cast pattern as test_device.py).
    program = SimpleNamespace(id=_APP_ID, name="Test App", dynamic=None)
    return cast(
        "Application",
        SimpleNamespace(program=program, version="2", manufacturer_id="M-0001"),
    )


def _fake_catalog() -> CatalogService:
    app = _fake_app()
    product = SimpleNamespace(
        product_ref_id=_PRODUCT,
        hardware2program_ref_id=_HW2PROG,
        application_id=_APP_ID,
    )

    def _get_products() -> list[Any]:
        return [product]

    def _get_application(app_id: str) -> Application | None:
        return app if app_id == _APP_ID else None

    def _get_hardware_by_program(_ref: str) -> Any:
        return None

    return cast(
        CatalogService,
        SimpleNamespace(
            get_products=_get_products,
            get_application=_get_application,
            get_hardware_by_program=_get_hardware_by_program,
        ),
    )


class _FakeLogger:
    def __init__(self) -> None:
        self.warnings: list[tuple[str, dict[str, Any]]] = []

    def info(self, event: str, **kwargs: Any) -> None: ...

    def debug(self, event: str, **kwargs: Any) -> None: ...

    def error(self, event: str, **kwargs: Any) -> None: ...

    def warning(self, event: str, **kwargs: Any) -> None:
        self.warnings.append((event, kwargs))


def _underlying(project: ProjectService) -> _ProjectService:
    # White-box: ProjectService._svc is the wrapped xknxmono service. Centralised
    # so the private-access pyright ignore lives in one place.
    return project._svc  # pyright: ignore[reportPrivateUsage]


def _version(project: ProjectService) -> int:
    return project._version  # pyright: ignore[reportPrivateUsage]


def _cache_version(project: ProjectService) -> int:
    return project._cache_version  # pyright: ignore[reportPrivateUsage]


def _bump(project: ProjectService) -> None:
    project._bump()  # pyright: ignore[reportPrivateUsage]


def _make_plugin(project: ProjectService) -> ProjectPlugin:
    # ProjectPlugin.__init__ builds imgui dockable panels; _handle_individual_address_change
    # only touches self._api.project.set_device_individual_address, so a bare __new__
    # plus a one-attribute _api stub drives it as a unit (the report's repro uses
    # the same bypass).
    plugin = object.__new__(ProjectPlugin)
    plugin._api = cast(PluginAPI, SimpleNamespace(project=project))  # pyright: ignore[reportPrivateUsage]
    return plugin


@pytest.fixture
def project_with_device(
    tmp_path: Path,
) -> tuple[ProjectService, str, int, _FakeLogger]:
    project = ProjectService(_fake_catalog())
    log = _FakeLogger()
    project.set_logger(cast(Logger, log))
    project.new(tmp_path / "p.xknx")
    pid = project._pid  # pyright: ignore[reportPrivateUsage]
    assert pid is not None
    backbone_seg = (
        _underlying(project).topology(pid, 0).areas[0].lines[0].segments[0].id
    )
    node_id = _underlying(project).add_device(
        pid,
        backbone_seg,
        _PRODUCT,
        address=5,
        name="D",
        hardware2program_ref_id=_HW2PROG,
    )
    _bump(project)  # the GUI's add_device would bump; we used _svc directly
    return project, pid, node_id, log


# --- ProjectService.set_device_individual_address ---------------------------


def test_returns_true_and_bumps_on_success(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    project, pid, node_id, _log = project_with_device
    version_before = _version(project)

    result = project.set_device_individual_address(node_id, "0.0.5", "0.0.9")

    assert result is True
    assert _version(project) == version_before + 1  # _bump() fired on success
    assert _underlying(project).individual_address(pid, node_id) == "0.0.9"


def test_returns_false_on_unknown_line_without_bump(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    # area 1 / line 5 doesn't exist in the skeleton installation (only area 0 /
    # line 0), so xknxmono raises KeyError("No line 1.5 ..."), which the GUI
    # adapter must catch and translate into a False return - never a raise, and
    # never a silent _bump (which would mask the rejection from the caller).
    project, pid, node_id, _log = project_with_device
    version_before = _version(project)

    result = project.set_device_individual_address(node_id, "0.0.5", "1.5.5")

    assert result is False
    assert _version(project) == version_before  # no _bump() on rejection
    assert _underlying(project).individual_address(pid, node_id) == "0.0.5"


def test_returns_false_on_duplicate_address_without_bump(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    project, pid, node_id, _log = project_with_device
    backbone_seg = (
        _underlying(project).topology(pid, 0).areas[0].lines[0].segments[0].id
    )
    _underlying(project).add_device(
        pid,
        backbone_seg,
        _PRODUCT,
        address=9,
        name="Other",
        hardware2program_ref_id=_HW2PROG,
    )
    _bump(project)
    version_before = _version(project)

    # xknxmono.move_device raises ValueError("already used") for a taken octet.
    result = project.set_device_individual_address(node_id, "0.0.5", "0.0.9")

    assert result is False
    assert _version(project) == version_before
    assert _underlying(project).individual_address(pid, node_id) == "0.0.5"


def test_returns_false_when_no_project_open(tmp_path: Path) -> None:
    project = ProjectService(_fake_catalog())
    project.set_logger(cast(Logger, _FakeLogger()))

    result = project.set_device_individual_address(1, "0.0.1", "0.0.2")

    assert result is False


def test_returns_false_on_unchanged_address(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    project, _pid, node_id, _log = project_with_device
    version_before = _version(project)

    result = project.set_device_individual_address(node_id, "0.0.5", "0.0.5")

    assert result is False
    assert _version(project) == version_before


def test_logs_warning_on_rejection(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    # The rejection may be log-only at the GUI layer, but it must not be SILENT:
    # the warning is the only breadcrumb a user (or test) has that the change
    # was rejected rather than accepted.
    project, _pid, node_id, log = project_with_device
    assert not log.warnings

    project.set_device_individual_address(node_id, "0.0.5", "1.5.5")

    assert len(log.warnings) == 1
    event, kwargs = log.warnings[0]
    assert event == "could not set individual address"
    assert kwargs["address"] == "1.5.5"
    assert "No line 1.5" in kwargs["error"]


# --- ProjectPlugin._handle_individual_address_change -----------------------


def test_handle_change_mutates_device_on_success(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    project, pid, node_id, _log = project_with_device
    plugin = _make_plugin(project)
    device = project.find_device_by_node_id(node_id)
    assert device is not None
    assert device.individual_address == "0.0.5"

    plugin._handle_individual_address_change(device, "0.0.9")  # pyright: ignore[reportPrivateUsage]

    # Live Device mutated to the accepted value (the Configure panel's
    # frame-local view updates immediately, before the cache rebuild).
    assert device.individual_address == "0.0.9"
    # The DB persisted it ...
    assert _underlying(project).individual_address(pid, node_id) == "0.0.9"
    # ... and _bump fired, so the next read rebuilds from the DB with the new IA
    # (the stale, mutated object is replaced by a fresh, DB-backed one).
    rebuilt = project.find_device_by_node_id(node_id)
    assert rebuilt is not None
    assert rebuilt is not device
    assert rebuilt.individual_address == "0.0.9"


def test_handle_change_does_not_mutate_device_on_rejection(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    """Regression test for the silent DB/cache desync.

    Before the fix the plugin mutated ``device.individual_address`` to the new
    value *before* calling the persistence layer; when the project rejected the
    address the swallowed error left the live, cache-shared ``Device`` stuck on
    a value the DB never stored, and the version-gated cache never rebuilt to
    repair it - so the Configure panel kept showing (and downstream code kept
    using) the rejected address. The fix mutates only after persistence accepts
    the change, so a rejection leaves the Device at its prior, DB-backed value.
    """
    project, pid, node_id, log = project_with_device
    plugin = _make_plugin(project)
    device = project.find_device_by_node_id(node_id)
    assert device is not None
    assert device.individual_address == "0.0.5"
    version_before = _version(project)

    plugin._handle_individual_address_change(device, "1.5.5")  # pyright: ignore[reportPrivateUsage]

    # The live, cache-shared Device is NOT mutated onto the rejected value ...
    assert device.individual_address == "0.0.5"
    # ... the cache still serves that same, un-corrupted object (no _bump, so
    # the cache is never rebuilt - and it didn't need to be) ...
    cached = project.find_device_by_node_id(node_id)
    assert cached is not None
    assert cached is device
    assert cached.individual_address == "0.0.5"
    assert _cache_version(project) == _version(project) == version_before
    # ... the DB never changed ...
    assert _underlying(project).individual_address(pid, node_id) == "0.0.5"
    # ... and the rejection surfaced as a warning rather than going silent.
    assert len(log.warnings) == 1


def test_handle_change_no_op_on_unchanged_address(
    project_with_device: tuple[ProjectService, str, int, _FakeLogger],
) -> None:
    project, _pid, node_id, _log = project_with_device
    plugin = _make_plugin(project)
    device = project.find_device_by_node_id(node_id)
    assert device is not None
    version_before = _version(project)

    plugin._handle_individual_address_change(device, "0.0.5")  # pyright: ignore[reportPrivateUsage]

    assert device.individual_address == "0.0.5"
    assert _version(project) == version_before  # no service call, no bump
