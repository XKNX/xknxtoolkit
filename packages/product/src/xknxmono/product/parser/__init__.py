"""IR → product value resolution.

Submodules: `com_objects`, `parameters`, `dynamic` (tree + visibility), and `modules` (shared
module-def/instance handling + template substitution). Each result type is defined next to the
resolver that produces it; this package's public functions take an IR `ApplicationProgram` and
return those resolved types.
"""

from __future__ import annotations

from . import dynamic
from .com_objects import extract as extract_app_com_objects
from .dynamic import build_app_dynamic_tree
from .parameters import extract as extract_app_parameters
from .parameters import extract_types as extract_app_param_types
from .parameters import extract_values as extract_app_param_values

__all__ = [
    "build_app_dynamic_tree",
    "dynamic",
    "extract_app_com_objects",
    "extract_app_param_types",
    "extract_app_param_values",
    "extract_app_parameters",
]
