"""Drive the real KnxGuiApp under Dear ImGui Test Engine.

Two uses:

  - Formal UI tests: see `knx_gui/testing/tests/`, run via
    `uv run pytest src/knx_gui/testing/tests`.
  - Ad-hoc scripts during development: import `build_app` + `run_ui_test` (and
    `capture`) directly from a throwaway script, e.g. to reproduce a layout
    bug and grab a screenshot without needing a human to do it by hand.

Both build on `knx_gui.main.build_runner_params`, so a test interacts with
the exact same panels/docking/menus as production - not a reimplementation.

Dear ImGui Test Engine carries its own license, separate from Dear ImGui
itself (free for individuals, education, open-source and small business use;
paid for larger businesses - see
https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt).
It is a dev-only dependency: `use_imgui_test_engine` is only ever turned on
here, never in `knx_gui.main.main` (the production entry point).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from imgui_bundle import hello_imgui, imgui
from imgui_bundle.immapp import testing as imgui_testing

from knx_gui.main import KnxGuiApp, build_runner_params

if TYPE_CHECKING:
    from knx_gui.device import Device

TestContext = imgui.test_engine.TestContext
TestRunSpeed = imgui_testing.TestRunSpeed
TestFunction = Callable[[TestContext], None]

_APP_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CATALOG = _APP_DIR / "demo.xknxcatalog"
DEFAULT_PROJECT = _APP_DIR / "demo.xknx"


@dataclass
class AppHandle:
    app: KnxGuiApp
    runner_params: hello_imgui.RunnerParams


def build_app(
    *,
    catalog_path: Path = DEFAULT_CATALOG,
    project_path: Path | None = DEFAULT_PROJECT,
) -> AppHandle:
    """Build a fresh KnxGuiApp wired exactly like production.

    Defaults to the same demo catalog/project used for manual dev testing.
    Pass `project_path=None` to start with no project open.
    """
    app = KnxGuiApp(catalog_path)
    if project_path is not None and project_path.exists():
        app.open_project(str(project_path))
    runner_params = build_runner_params(app)
    return AppHandle(app=app, runner_params=runner_params)


def find_device(app_handle: AppHandle, predicate: Callable[[Device], bool]) -> Device:
    """The first device in `app_handle`'s project matching `predicate`.

    For building a deterministic test scenario - e.g. a device with no
    parameters/com objects, to isolate one panel section from another's own
    (possibly buggy) layout.
    """
    return next(d for d in app_handle.app.project.devices if predicate(d))


def run_ui_test(
    test_function: TestFunction,
    *,
    app_handle: AppHandle | None = None,
    run_speed: TestRunSpeed = TestRunSpeed.fast,
    exit_after_test: bool = True,
) -> None:
    """Run `test_function(ctx)` against the real app, then exit.

    `app_handle` defaults to `build_app()` (demo catalog + demo project).
    Set `exit_after_test=False` to leave the window open after the test body
    returns, e.g. for interactive inspection.
    """
    handle = app_handle or build_app()
    imgui_testing.run(
        gui_function=lambda: (
            None
        ),  # unused: runner_params already drives the real panels
        test_function=test_function,
        runner_params=handle.runner_params,
        exit_after_test=exit_after_test,
        run_speed=run_speed,
    )


def capture(ctx: TestContext, path: str | Path, *, window: str | None = None) -> Path:
    """Screenshot helper - creates the parent directory, returns the resolved path.

    See `imgui_bundle.immapp.testing.capture` for the full behavior (it yields
    a frame first so pending layout has a chance to settle).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    imgui_testing.capture(ctx, str(path), window=window)
    return path
