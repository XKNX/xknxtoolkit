# knx-gui

## Commands

- Run knxprod tests: `uv run pytest src/knx_gui/knxprod/tests/ -v`
- Run project tests: `uv run pytest src/knx_gui/project/tests/ -v`
- Run GUI: `uv run python -m knx_gui.main`
- Generate demo project: `uv run generate-demo`
- Generate catalog from knxprod: `uv run generate-catalog [files...]`
- Use `uv run` for all Python commands (not manual venv activation)

## Conventions

- All user-facing strings must be defined in `src/knx_gui/strings.py` for i18n support
- Panels hold their own internal state; shared state is accessed via dependency-injected callbacks
