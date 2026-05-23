"""Bulk-ingest .knxprod files from a directory into the catalog database."""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from xknxmono.product.errors import ArchiveError

from xknxmono.catalog.db import get_knxprod_dir
from xknxmono.catalog.ingest import ingest_file


def main() -> None:
    source_dir = sys.argv[1] if len(sys.argv) > 1 else str(get_knxprod_dir())

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"ERROR: KNXPROD_DIR not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    dest_dir = get_knxprod_dir()
    files = sorted(source_path.glob("*.knxprod"))
    total = len(files)
    print(f"Found {total} .knxprod files in {source_path}")

    errors = 0
    for i, fp in enumerate(files, 1):
        if i % 100 == 0 or i == total:
            print(f"  [{i}/{total}] {fp.name}")
        try:
            ingest_file(fp.read_bytes(), dest_dir)
        except ArchiveError as e:
            print(f"  SKIP {fp.name}: {e}", file=sys.stderr)
            errors += 1
        except Exception as e:
            print(f"  ERROR {fp.name}: {e}", file=sys.stderr)
            errors += 1

    print(f"Done. {total - errors} succeeded, {errors} failed.")
