"""Adapters that convert per-version `files.vXX` models into the unified `intermediate` model.

The bulk of each conversion is mechanical field-by-field copying (xsdata names fields
identically across versions). Only genuine divergences need explicit overrides — and those
correspond exactly to the breaking schema transforms in `refactor_device.py` plus a couple of
data-level rules (e.g. synthesized PUIDs for pre-v12 projects).

`report.py` produces a structural worklist (what doesn't line up between each version and the
intermediate) to drive both the overrides here and the manual cleanup of the intermediate model.
"""
