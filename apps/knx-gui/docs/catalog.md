# Catalog Database Architecture

## Overview

The catalog database stores application definitions extracted from `.knxprod` files. This allows devices to be reconstructed without needing the original knxprod file.

## Database Schema

### Applications Table

| Column          | Type        | Description                                           |
|-----------------|-------------|-------------------------------------------------------|
| id              | INTEGER     | Primary key, auto-increment                           |
| manufacturer_id | TEXT        | Manufacturer ID (e.g., "M-0001")                      |
| application_id  | TEXT        | Full application ID (unique, e.g., "M-0001_A-0001-00-0001") |
| name            | TEXT        | Application name                                      |
| xml_data        | BLOB        | Raw application XML from knxprod                      |
| created_at      | DATETIME    | When the entry was added (UTC)                        |

## Usage

### Populating the Catalog

```bash
# From specific knxprod files
uv run generate-catalog device1.knxprod device2.knxprod

# From all knxprod files in ~/knxprod/
uv run generate-catalog
```

### Programmatic Access

```python
from pathlib import Path
from knx_gui.catalog import CatalogDatabase, load_knxprod_to_catalog, get_application_xml

# Open or create catalog
catalog = CatalogDatabase(Path("catalog.db"))
catalog.open()  # or catalog.create() for new

# Add applications from knxprod
added = load_knxprod_to_catalog(catalog, Path("device.knxprod"))

# Retrieve XML by application_id
xml_data = get_application_xml(catalog, "M-0001_A-0001-00-0001")

catalog.close()
```

## Application ID

The `application_id` is a unique identifier from the knxprod file (e.g., "M-0001_A-0001-00-0001"). It combines the manufacturer ID with the application-specific identifier, making it globally unique across all KNX products.

This ensures:
- Duplicate detection (same application from different sources)
- Stable identifier for database references
- Direct lookup without computing hashes

## Integration with Projects

When a device is added from a knxprod file:
1. The application XML is added to the catalog (if not already present)
2. The project stores `template_id = "catalog:{application_id}"`
3. On reload, the project looks up the catalog by application_id to reconstruct the device

## File Location

Default catalog location: `apps/knx-gui/demo.xknxcatalog`

The catalog uses the `.xknxcatalog` extension and is shared across all projects.

## Migrations

Schema migrations use Alembic, same as the project database:
- Migration files in `src/knx_gui/catalog/migrations/versions/`
- Auto-runs on `open()`, auto-stamps on `create()`
