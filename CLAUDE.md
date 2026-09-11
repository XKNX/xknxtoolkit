# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                             # Install dependencies (packages/* only - apps/knx-gui isn't
                                     # a root dependency, so plain `uv sync` never installs it or
                                     # imgui-bundle; use `uv sync --all-packages`, or run a command
                                     # from inside apps/knx-gui, which lazily syncs it)
uv run pytest                       # Run all package tests
uv run pytest packages/models       # Run tests for a single package
uv run ruff check                   # Lint
uv run ruff format                  # Format
uv run pyright                      # Type check (strict mode)

# Regenerate KNX XML schema bindings (requires XSD files in packages/models/src/xknxmono/models/schemas/)
cd packages/models/src && uvx --from "xsdata[cli]" xsdata generate --config ../.xsdata.xml xknxmono/models/schemas/
```

### Coverage

CI's "coverage" job combines packages/, apps/knx-gui unit-test and apps/knx-gui
e2e-test coverage into one report (see `.github/workflows/ci.yml`). To reproduce
locally, set `COVERAGE_RCFILE` once (coverage.py reads it natively) rather than
passing `--rcfile` to every command — its config discovery doesn't walk up
parent directories the way pytest's does, so a command run from inside
`apps/knx-gui` would otherwise silently pick up that directory's own
(coverage-config-less) `pyproject.toml` instead of the root one. Likewise
`--source` is an absolute, repo-root-anchored path in every invocation, same as
CI, so the data collected from `apps/knx-gui` (a different cwd) can still be
combined without `[tool.coverage.paths]` remapping:

```bash
export ROOT="$(pwd)"
export COVERAGE_RCFILE="$ROOT/pyproject.toml"
uv run coverage run --source="$ROOT/packages" -m pytest
cd apps/knx-gui
uv run coverage run --source="$ROOT/apps/knx-gui/src/knx_gui" -m pytest src/knx_gui --ignore=src/knx_gui/testing
uv run coverage run --source="$ROOT/apps/knx-gui/src/knx_gui" -m pytest src/knx_gui/testing
cd "$ROOT"
uv run coverage combine . apps/knx-gui   # merges the three parallel .coverage.* data files -
                                          # combine only looks in the given directories, not
                                          # recursively, hence listing both explicitly
uv run coverage report    # or `coverage html` for a browsable report in htmlcov/
```

Other choices behind the CI setup (`.github/workflows/ci.yml`), each confirmed by actually
running the pipeline rather than assumed from the docs:

- `coverage run`, not `pytest --cov=...`: the latter does not honor `[tool.coverage.run]`'s
  `parallel = true` the same way, so the three runs' data files would collide instead of
  getting the unique suffixes `combine` needs.
- The `unit-tests`/`e2e-tests` jobs collect their `.coverage.*` files into a
  `$GITHUB_WORKSPACE/coverage-data/` directory before uploading them as artifacts, rather than
  leaving them where they land (`combine <dir>` isn't recursive, so an apps/knx-gui-nested
  file would otherwise be silently skipped) - and that directory is workspace-root-anchored
  rather than `apps/knx-gui`-relative, because `../coverage-data` from there resolves to
  `apps/coverage-data`, which matches the `apps/*` `[tool.uv.workspace]` members glob and
  breaks `uv run` in every later step.
- The "coverage" job syncs with `--no-install-workspace`: it only ever reads already-collected
  coverage data and the source files `actions/checkout` already provides - it never imports
  `packages/` or `apps/knx-gui` - so installing either (`imgui-bundle`, `sqlalchemy`, `xknx`, ...)
  is pure overhead there.

**Codecov**: the coverage job uploads `coverage.xml` to Codecov, which posts two status checks
on every PR (configured in `codecov.yml`) - `project` fails the PR if overall coverage drops
versus the base branch (`target: auto` compares against the base commit itself, so it isn't a
fixed number that needs bumping by hand), and `patch` (coverage of just the changed lines) is
informational-only, since a one-line fix in an otherwise-uncovered file shouldn't be gated on
covering that whole file. The Codecov GitHub App is already installed org-wide (from
`xknx/xknx` already using it) and reaches this repo automatically, but uploads still need a
`CODECOV_TOKEN` repository secret (from codecov.io's settings for xknxtoolkit) - without one,
Codecov rejects the upload ("Token required because branch is protected", its own per-repo
policy, unrelated to GitHub's own branch protection). `fail_ci_if_error: false` is deliberate:
a problem on Codecov's end, or the token not being set, shouldn't turn every PR's CI red over
a reporting step.

All Python commands must use `uv run` — do not activate the venv manually.

## Architecture

UV monorepo: `packages/` holds five core libraries; `apps/` holds applications.

**Package dependency order** (bottom to top):
- `xknx-models` — foundation: KNX XML schema bindings generated by xsdata for versions 10–14 and 20–23, plus `detect_version()`, `load_xml()`, `serialize_xml()`
- `xknx-product` — reads `.knxprod` archives (ZIP files), validates structure, parses manufacturer/catalog/hardware/application XMLs via models
- `xknx-catalog` — SQLite catalog of imported `.knxprod` hardware/applications, depends on product; also exposes an optional FastAPI HTTP layer (`xknxmono.catalog.http`) over the same data
- `xknx-project` — project state management, depends on models
- `xknx-keyring` — parses/serializes KNX keyring XML, depends on models
- `apps/knx-gui` — node-based GUI app; consumes all packages; see `apps/knx-gui/CLAUDE.md`

**Import paths** use the `xknxmono` namespace package (src layout):
- `from xknxmono.models import ...`
- `from xknxmono.product import ...`
- `from xknxmono.catalog import ...`
- `from xknxmono.project import ...`
- `from xknxmono.keyring import ...`

**Generated code** lives under `**/files/` and `**/intermediate/` (e.g. `xknxmono.models.files`, produced by xsdata from the KNX XML schemas) — never edit these directly. Both are excluded from linting and type checking.

## Code Style

- Pyright strict mode; all public APIs must be fully typed
- Ruff rules: E, W, F, I, UP, B, SIM, RUF — double quotes, 2-space indent, LF line endings

## Adding a New Package

1. Create `packages/<name>/` with `pyproject.toml` (`name = "xknx-<name>"`), `src/xknxmono/<name>/__init__.py`, `src/xknxmono/<name>/py.typed`, and `tests/`
2. Add `"xknx-<name>"` to root `pyproject.toml` dependencies
3. Run `uv sync`
