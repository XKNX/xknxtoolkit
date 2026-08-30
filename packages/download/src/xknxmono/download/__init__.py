"""Download applications into KNX devices.

The package interprets the Load Procedure of a parsed application program and
executes it over a running ``xknx`` connection: driving each loadable part's
Load State Machine and writing the assembled download image via memory and
property services.
"""

from __future__ import annotations

from .commissioning import program_individual_address
from .download import download, preflight
from .errors import (
    DownloadError,
    ImageError,
    LoadStateError,
    UnsupportedProcedureError,
    VerificationError,
)
from .image import (
    DownloadImage,
    GroupCommunication,
    MemorySegment,
    PropertyValue,
    build_image,
)
from .load_state import LoadEvent, LoadState
from .merge import resolve_download_controls
from .preflight import (
    ByteRange,
    PreflightReport,
    PropertyDiff,
    SegmentDiff,
)
from .procedure import LoadProcedureRunner
from .programmer import ConnectionManager, DeviceProgrammer
from .project_data import (
    GroupObjectLink,
    SeedDevice,
    group_address_table,
    group_communication_from_device,
    module_instances_from_device,
    parameter_instance_refs_from_device,
    parameter_values_from_device,
)
from .scope import DownloadScope
from .tables import (
    Association,
    build_association_table,
    build_group_address_table,
)

__version__ = "0.1.0"

__all__ = [
    "Association",
    "ByteRange",
    "ConnectionManager",
    "DeviceProgrammer",
    "DownloadError",
    "DownloadImage",
    "DownloadScope",
    "GroupCommunication",
    "GroupObjectLink",
    "ImageError",
    "LoadEvent",
    "LoadProcedureRunner",
    "LoadState",
    "LoadStateError",
    "MemorySegment",
    "PreflightReport",
    "PropertyDiff",
    "PropertyValue",
    "SeedDevice",
    "SegmentDiff",
    "UnsupportedProcedureError",
    "VerificationError",
    "build_association_table",
    "build_group_address_table",
    "build_image",
    "download",
    "group_address_table",
    "group_communication_from_device",
    "module_instances_from_device",
    "parameter_instance_refs_from_device",
    "parameter_values_from_device",
    "preflight",
    "program_individual_address",
    "resolve_download_controls",
]
