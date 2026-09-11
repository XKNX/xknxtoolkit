# knx-gui

## Required Reading

Before making changes, read these docs:
- `docs/architecture.md` - Template/instance pattern, data flow, key principles

## Commands

- Run unit tests: `uv run pytest src/knx_gui --ignore=src/knx_gui/testing -v` (the root `uv run pytest` only covers `packages/`, not `apps/`)
- Run e2e tests (Dear ImGui Test Engine, needs a real display): `uv run pytest src/knx_gui/testing -v`
- Run GUI: `uv run python -m knx_gui.main`
- Generate demo project: `uv run generate-demo`
- Generate catalog from knxprod: `uv run generate-catalog [files...]`
- Use `uv run` for all Python commands (not manual venv activation)

## UI testing / agentic development (Dear ImGui Test Engine)

`src/knx_gui/testing/harness.py` drives the *real* `KnxGuiApp` (same panels, docking, menus as production — `knx_gui.main.build_runner_params` is shared between them) under [Dear ImGui Test Engine](https://github.com/ocornut/imgui_test_engine), via `imgui_bundle`'s bindings (`imgui.test_engine`, `imgui_bundle.immapp.testing`). It can click, type, move the mouse, scroll, and capture real PNG screenshots of the running app — use it instead of asking a human for a screenshot when diagnosing a layout bug.

- `build_app(catalog_path=..., project_path=...)` → `AppHandle` — defaults to the demo catalog/project already in this repo (`demo.xknxcatalog` / `demo.xknx`).
- `run_ui_test(test_function, app_handle=...)` — runs `test_function(ctx: imgui.test_engine.TestContext)` against it, then exits. `ctx` has the full Test Engine API: `item_click`/`item_open`, `mouse_move`/`mouse_click`/`mouse_drag_with_delta`, `key_chars`, `scroll_to_*`, `get_window_by_ref` (inspect `.scroll_max`, `.content_size`, `.size`, etc. for a real window), and more.
- `capture(ctx, path, window=...)` — screenshot helper (creates the parent dir).
- For a *focused* test of one panel (bypassing the full app and other plugins — see `testing/tests/test_configure_panel.py` for the pattern), build the panel directly and drive `imgui_bundle.immapp.testing.run(gui_function, test_function)` yourself.

For a throwaway diagnostic during a session (not a checked-in test), write a short script importing `knx_gui.testing.harness` and run it with `uv run python <script>.py` — it can monkeypatch functions before importing the app to isolate which code path causes a symptom (see git history around the "Parameters tab bar" overflow bug for a worked example: bisecting by disabling one render function at a time, each in its own process, comparing `window.scroll_max`).

Needs a real display (it briefly opens an actual window) — that's why these tests aren't part of the root `uv run pytest`, and why CI runs them as their own `e2e-tests` job, under `xvfb-run` (virtual display + mesa's software GL) — see `.github/workflows/ci.yml`. Every other plugin's own tests (e.g. `network`) run in the `unit-tests` job instead, which auto-discovers anything under `src/knx_gui` except `src/knx_gui/testing`.

**Licensing**: Dear ImGui Test Engine has its own license, separate from Dear ImGui itself — free for individuals, education, open-source and small business use; paid for larger businesses (see [its LICENSE.txt](https://github.com/ocornut/imgui_test_engine/blob/main/imgui_test_engine/LICENSE.txt)). It's a dev-only dependency: `use_imgui_test_engine` is only ever turned on inside `knx_gui.testing.harness`, never in the production entry point (`knx_gui.main.main`).

## Plugin architecture

Features live under `src/knx_gui/plugins/<name>/`, one directory per plugin (`catalog`, `project`, `node_editor`, `connection`, `proxy`, `virtual`, `network`, `logger`, `cat`). A plugin typically has:
- `plugin.py` — lifecycle class implementing the `Plugin` protocol (`base/registry.py`): `__init__(self, api: PluginAPI)`, a `panels` property, `on_load`/`on_unload`
- `service.py` — plugin logic decoupled from imgui, sometimes exposed to other plugins as a shared service on `PluginAPI` (e.g. `connection`, `catalog`, `project`, `log`)
- `strings.py` — user-facing strings for this plugin's i18n domain (see below)
- `ui.py` — panel rendering, when the plugin owns a dockable panel

Plugins are instantiated and wired directly in `main.py::KnxGuiApp.__init__` (menus, panels, shutdown order) — `base/registry.PluginRegistry` exists but isn't used for dynamic discovery yet.

Plugins that need to interact (e.g. `proxy` relaying CEMI frames to/from the real KNX connection) only do so through a shared service on `PluginAPI`, never by holding a reference to another plugin instance directly.

## Tasks plugin (background work / status bar)

`plugins/tasks/` tracks background work (loading a knxprod, programming or
restarting a device) for the status bar pill (`TaskStatusWidget`, rendered via
`TasksPlugin.render_status_indicator()` from `main.py::gui_status_bar`
alongside `ConnectionPlugin`'s). Design decisions worth knowing before
touching it:

- **No progress percentage.** A task is `queued`, `running` (shown with a
  pulsing dot - the only feedback while it's in flight) or `error` (stays
  until dismissed). There's deliberately no `done` status - `TaskService.track()`
  removes a task outright on success rather than leaving a badge nobody needs
  to read once it's over.
- **Immediate-mode, no subscribe/notify**, like the rest of this app -
  `TaskService.tasks()` is just called every frame; nothing pushes.
- **`track(label, future)`** is the preferred way to add a task backed by a
  `Future`: it resolves itself via `future.add_done_callback`, which fires on
  whichever thread the future completes on (see `ConnectionService.run_async`)
  - same no-lock, plain-mutation pattern already used for restart/program
  results in the Configure panel. Use `add`/`update`/`remove` directly only
  for work that isn't `Future`-backed.
- **The pulsing dot** (`widgets/status_dot.py::render_pulsing_dot`) is shared
  with `ConnectionPlugin`'s CONNECTED indicator - both used to hand-animate
  this before it was extracted here. It only draws into the current draw list
  at a given center; the caller reserves layout space itself (`imgui.dummy`),
  since how much room to reserve varies per caller.
- **The status bar pill has no background/border/pill shape** - plain text
  matching the connection indicator beside it, not a standing-out chip - and
  shows a dim "No active tasks" dot rather than disappearing when there's nothing to
  report, for the same reason the connection indicator always shows something
  rather than going blank: an empty status bar reads as broken.
- It's wrapped in an invisible, unstyled `begin_child` purely so the whole
  pill is one clickable item (`is_item_clicked()` right after it) without
  manual hit-testing - per hello_imgui/Dear ImGui, `BeginChild` registers
  itself as a regular item in the parent window.
- It's horizontally centered across the *whole* status bar, not just the
  space left after the connection indicator - clamped so it never overlaps it.
- The popup list drops "Active"/"Queued"/"Errors" headings - each row's own
  dot color already says which group it's in.

## Conventions

- All user-facing strings must be defined in each plugin's `strings.py` (or `src/knx_gui/strings.py` for app-wide strings) for i18n support
- Panels hold their own internal state; shared state is accessed via dependency-injected callbacks
- Catalog stores immutable templates; project stores device instances with overrides
- Visibility (visible_com_objects, visible_parameters) computed at runtime, never baked into templates
