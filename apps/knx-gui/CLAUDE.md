# knx-gui

## Required Reading

Before making changes, read these docs:
- `docs/architecture.md` - Template/instance pattern, data flow, key principles

## Commands

- Run tests: `uv run pytest src/knx_gui/plugins/network/tests/ -v` (the only plugin with its own tests right now; the root `uv run pytest` only covers `packages/`, not `apps/`)
- Run GUI: `uv run python -m knx_gui.main`
- Generate demo project: `uv run generate-demo`
- Generate catalog from knxprod: `uv run generate-catalog [files...]`
- Use `uv run` for all Python commands (not manual venv activation)

## Plugin architecture

Features live under `src/knx_gui/plugins/<name>/`, one directory per plugin (`catalog`, `project`, `node_editor`, `connection`, `proxy`, `virtual`, `network`, `logger`, `cat`). A plugin typically has:
- `plugin.py` — lifecycle class implementing the `Plugin` protocol (`base/registry.py`): `__init__(self, api: PluginAPI)`, a `panels` property, `on_load`/`on_unload`
- `service.py` — plugin logic decoupled from imgui, sometimes exposed to other plugins as a shared service on `PluginAPI` (e.g. `connection`, `catalog`, `project`, `log`)
- `strings.py` — user-facing strings for this plugin's i18n domain (see below)
- `ui.py` — panel rendering, when the plugin owns a dockable panel

Plugins are instantiated and wired directly in `main.py::KnxGuiApp.__init__` (menus, panels, shutdown order) — `base/registry.PluginRegistry` exists but isn't used for dynamic discovery yet.

Plugins that need to interact (e.g. `proxy` relaying CEMI frames to/from the real KNX connection) only do so through a shared service on `PluginAPI`, never by holding a reference to another plugin instance directly.

## Conventions

- All user-facing strings must be defined in each plugin's `strings.py` (or `src/knx_gui/strings.py` for app-wide strings) for i18n support
- Panels hold their own internal state; shared state is accessed via dependency-injected callbacks
- Catalog stores immutable templates; project stores device instances with overrides
- Visibility (visible_com_objects, visible_parameters) computed at runtime, never baked into templates
