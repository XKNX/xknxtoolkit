# xknxtoolkit

UV monorepo for XKNX libraries.

## Packages

| Package | Import | Description |
|---------|--------|-------------|
| xknx-models | `from xknx.models import ...` | Shared models (base) |
| xknx-product | `from xknx.product import ...` | Product library |
| xknx-project | `from xknx.project import ...` | Project library |
| xknx-keys | `from xknx.keys import ...` | Keys library |

All packages depend on `xknx-models`.

## Structure

```
xknxtoolkit/
├── pyproject.toml              # Workspace config
├── ruff.toml                   # Linting config
├── pyrightconfig.json          # Type checking config
├── packages/
│   ├── models/
│   │   ├── pyproject.toml
│   │   ├── src/xknx/models/
│   │   └── tests/
│   ├── product/
│   │   ├── pyproject.toml
│   │   ├── src/xknx/product/
│   │   └── tests/
│   ├── project/
│   │   ├── pyproject.toml
│   │   ├── src/xknx/project/
│   │   └── tests/
│   └── keys/
│       ├── pyproject.toml
│       ├── src/xknx/keys/
│       └── tests/
```

## Setup

```bash
uv sync
```

## Commands

```bash
uv run pytest                       # Run all tests
uv run pytest packages/models       # Run tests for single package
uv run ruff check                   # Lint
uv run ruff format                  # Format
uv run pyright                      # Type check
```

## Adding a new package

1. Create `packages/<name>/` with:
   - `pyproject.toml` (set `name = "xknx-<name>"`)
   - `src/xknx/<name>/__init__.py`
   - `src/xknx/<name>/py.typed`
   - `tests/`

2. Add to root `pyproject.toml` dependencies:
   ```toml
   dependencies = [
       ...
       "xknx-<name>",
   ]
   ```

3. Run `uv sync`

## Requirements

- Python >= 3.12
- uv
