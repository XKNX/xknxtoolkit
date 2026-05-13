"""Generate or update the catalog database from knxprod files."""

import sys
from pathlib import Path

from knx_gui.catalog.database import CatalogDatabase
from knx_gui.catalog.loader import load_knxprod_to_catalog


def generate_catalog(catalog_path: Path, knxprod_paths: list[Path]) -> None:
    if catalog_path.exists():
        print(f"Opening existing catalog: {catalog_path}")
        db = CatalogDatabase(catalog_path)
        db.open()
    else:
        print(f"Creating new catalog: {catalog_path}")
        db = CatalogDatabase(catalog_path)
        db.create()

    total_added = 0
    for knxprod_path in knxprod_paths:
        if not knxprod_path.exists():
            print(f"  Skipping (not found): {knxprod_path}")
            continue

        print(f"  Loading: {knxprod_path.name}")
        try:
            added = load_knxprod_to_catalog(db, knxprod_path)
            if added:
                print(f"    Added {len(added)} application(s)")
                for app_id in added:
                    print(f"      - {app_id}")
                total_added += len(added)
            else:
                print("    No new applications (already in catalog)")
        except Exception as e:
            print(f"    Error: {e}")

    db.close()
    print(f"\nCatalog updated: {total_added} application(s) added")
    print(f"Saved to: {catalog_path}")


def main() -> None:
    catalog_path = Path(__file__).parent.parent.parent.parent / "demo.xknxcatalog"

    if len(sys.argv) > 1:
        knxprod_paths = [Path(p) for p in sys.argv[1:]]
    else:
        internal_knxprod = (
            Path(__file__).parent.parent.parent.parent / "internal" / "knxprod"
        )
        if internal_knxprod.exists():
            knxprod_paths = list(internal_knxprod.glob("*.knxprod"))
            print(f"Loading from: {internal_knxprod}")
        else:
            knxprod_paths = []
            print("No knxprod files specified and internal/knxprod not found")
            print("Usage: generate-catalog [knxprod_file ...]")
            return

    generate_catalog(catalog_path, knxprod_paths)


if __name__ == "__main__":
    main()
