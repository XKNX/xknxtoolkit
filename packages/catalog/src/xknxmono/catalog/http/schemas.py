"""Pydantic response schemas for the catalog HTTP API endpoints.

All schemas that map to ORM models use ``model_config = {"from_attributes": True}``
so FastAPI can call ``model_validate`` automatically when a ``response_model`` is set.
Schemas that map to the ``xknxmono.product.application`` dataclasses do the same —
``from_attributes`` works for any Python object with the matching attribute names.

:class:`ApplicationDetailResponse` nests all its sub-schemas as inner classes so
they are namespaced under the parent and not exported individually.  ``from __future__
import annotations`` is required so that forward references like
``ApplicationDetailResponse.ComObject`` inside the class body resolve lazily, after
the outer class is fully defined.
"""
from __future__ import annotations

import base64
import datetime
from typing import Any

from pydantic import BaseModel, field_serializer, field_validator


class ManufacturerResponse(BaseModel):
  """API response schema for a KNX manufacturer."""

  id: str
  name: str | None
  model_config = {"from_attributes": True}


class HardwareProgramResponse(BaseModel):
  """API response schema for a hardware program, including its medium types and linked application."""

  model_config = {"from_attributes": True}

  class Application(BaseModel):
    """API response schema for an ETS application program."""

    model_config = {"from_attributes": True}
    id: str
    name: str
    application_number: int | None
    application_version: int | None
    mask_version: str | None
    is_secure_enabled: bool | None

  id: str
  hardware_id: str
  medium_types: list[str]
  registration_status: str | None
  registration_number: str | None
  registration_date: datetime.date | None
  application: HardwareProgramResponse.Application | None

  @field_validator("medium_types", mode="before")
  @classmethod
  def _flatten_medium_types(cls, v: Any) -> list[str]:
    """Accept either a list of ORM ``HardwareProgramMediumType`` objects or plain strings.

    When the value comes from the ORM relationship it is a list of
    ``HardwareProgramMediumType`` instances; extract their ``.medium_type``
    string attribute.  Plain ``str`` values (e.g. from tests or dict input)
    are passed through unchanged.
    """
    return [item.medium_type if hasattr(item, "medium_type") else item for item in v]


HardwareProgramResponse.model_rebuild()


class HardwareResponse(BaseModel):
  """API response schema for a hardware item, including all its associated programs."""

  id: str
  manufacturer_id: str
  name: str | None
  order_number: str | None
  description: str | None
  is_rail_mounted: bool | None
  width_mm: float | None
  serial_number: str | None
  version_number: int | None
  bus_current: float | None
  has_application_program: bool | None
  is_coupler: bool | None
  is_power_supply: bool | None
  is_ip_enabled: bool | None
  no_download_without_plugin: bool | None
  default_language: str | None
  programs: list[HardwareProgramResponse]
  model_config = {"from_attributes": True}


class CatalogSectionResponse(BaseModel):
  """API response schema for a catalog section node, with nested children."""

  id: str
  name: str
  number: str | None
  manufacturer_id: str
  parent_id: str | None
  children: list[CatalogSectionResponse] = []


class ApplicationDetailResponse(BaseModel):
  """Full on-demand detail for an application program, parsed live from the .knxprod archive.

  Sub-schemas are defined as inner classes so they are namespaced under this
  model and not exported individually from the module.
  """

  model_config = {"from_attributes": True}

  class ComObjectFlags(BaseModel):
    """Communication flags for a KNX group object."""

    model_config = {"from_attributes": True}
    communication: bool
    read: bool
    write: bool
    transmit: bool
    update: bool
    read_on_init: bool

  class ComObject(BaseModel):
    """A KNX group object (communication object)."""

    model_config = {"from_attributes": True}
    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: ApplicationDetailResponse.ComObjectFlags

  class EnumOption(BaseModel):
    """A single option in an enumeration parameter type."""

    model_config = {"from_attributes": True}
    value: str
    text: str

  class ParamType(BaseModel):
    """The type descriptor for an application parameter (enumeration, integer, etc.)."""

    model_config = {"from_attributes": True}
    kind: str
    options: list[ApplicationDetailResponse.EnumOption] = []
    min_value: int | None
    max_value: int | None
    size_bits: int | None

    @field_validator("kind", mode="before")
    @classmethod
    def _extract_enum_value(cls, v: Any) -> str:
      """Accept either a plain string or a ``ParamTypeKind`` enum; return its string value."""
      return v.value if hasattr(v, "value") else v

  class Parameter(BaseModel):
    """An application parameter with its current value and type."""

    model_config = {"from_attributes": True}
    id: str
    ref_id: str
    name: str
    text: str
    value: str
    param_type: ApplicationDetailResponse.ParamType | None

  class AbsoluteSegment(BaseModel):
    """An absolute memory segment from the application code, with binary data encoded as base64."""

    model_config = {"from_attributes": True}
    id: str
    address: int
    size: int
    data: bytes | None
    mask: bytes | None
    name: str | None
    user_memory: bool

    @field_serializer("data", "mask")
    def _encode(self, v: bytes | None) -> str | None:
      """Serialize binary data and mask fields as base64 strings."""
      return base64.b64encode(v).decode() if v is not None else None

  class RelativeSegment(BaseModel):
    """A relative memory segment from the application code, with binary data encoded as base64."""

    model_config = {"from_attributes": True}
    id: str
    offset: int
    size: int
    data: bytes | None
    mask: bytes | None
    name: str | None

    @field_serializer("data", "mask")
    def _encode(self, v: bytes | None) -> str | None:
      """Serialize binary data and mask fields as base64 strings."""
      return base64.b64encode(v).decode() if v is not None else None

  class Code(BaseModel):
    """The complete loadable code for an application program, split into absolute and relative segments."""

    model_config = {"from_attributes": True}
    absolute_segments: list[ApplicationDetailResponse.AbsoluteSegment]
    relative_segments: list[ApplicationDetailResponse.RelativeSegment]

  application_id: str
  name: str
  manufacturer_id: str
  com_objects: list[ApplicationDetailResponse.ComObject]
  parameters: list[ApplicationDetailResponse.Parameter]
  code: ApplicationDetailResponse.Code | None


ApplicationDetailResponse.model_rebuild()
