#!/usr/bin/env python3
"""Validate that CHANGELOG.md files follow the Keep a Changelog structure this repo uses."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VERSION_HEADER = re.compile(r"^## \[(?P<version>\d+\.\d+\.\d+|Unreleased)\](?: - (?P<date>\d{4}-\d{2}-\d{2}))?$")


def check(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    errors = []

    if not lines or lines[0] != "# Changelog":
        errors.append("must start with a '# Changelog' title")

    headers = [line for line in lines if line.startswith("## [")]
    if not headers or headers[0] != "## [Unreleased]":
        errors.append("first '## [...]' section must be '## [Unreleased]'")

    for header in headers:
        match = VERSION_HEADER.match(header)
        if match is None:
            errors.append(f"malformed section header: {header!r}")
        elif match.group("version") != "Unreleased" and match.group("date") is None:
            errors.append(f"released version header missing a date: {header!r}")

    return errors


def main() -> int:
    changelogs = sorted((*ROOT.glob("packages/*/CHANGELOG.md"), *ROOT.glob("apps/*/CHANGELOG.md")))
    if not changelogs:
        print("::error::no CHANGELOG.md files found under packages/*/ or apps/*/")
        return 1

    failed = False
    for changelog in changelogs:
        for error in check(changelog):
            rel = changelog.relative_to(ROOT)
            print(f"::error file={rel}::{error}")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
