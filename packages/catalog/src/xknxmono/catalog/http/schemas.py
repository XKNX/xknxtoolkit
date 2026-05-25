"""Pydantic response schemas for the catalog HTTP API endpoints."""
import base64
import datetime

from pydantic import BaseModel, field_serializer


class ManufacturerOut(BaseModel):
  """API response schema for a KNX manufacturer."""

  id: str
  name: str | None
  model_config = {"from_attributes": True}


class ApplicationOut(BaseModel):
  """API response schema for an ETS application program."""

  id: str
  name: str
  application_number: int | None
  application_version: int | None
  mask_version: str | None
  is_secure_enabled: bool | None
  model_config = {"from_attributes": True}


class HardwareProgramOut(BaseModel):
  """API response schema for a hardware program, including its medium types and linked application."""

  id: str
  hardware_id: str
  medium_types: list[str]
  registration_status: str | None
  registration_number: str | None
  registration_date: datetime.date | None
  application: ApplicationOut | None
  model_config = {"from_attributes": True}


class HardwareOut(BaseModel):
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
  programs: list[HardwareProgramOut]
  model_config = {"from_attributes": True}


class CatalogSectionOut(BaseModel):
  """API response schema for a catalog section node, with nested children."""

  id: str
  name: str
  number: str | None
  manufacturer_id: str
  parent_id: str | None
  children: list["CatalogSectionOut"] = []


# --- On-demand application detail (loaded from .knxprod at request time) ---


class ComObjectFlagsOut(BaseModel):
  """Communication flags for a KNX group object."""

  communication: bool
  read: bool
  write: bool
  transmit: bool
  update: bool
  read_on_init: bool


class ComObjectOut(BaseModel):
  """API response schema for a KNX group object (communication object)."""

  id: str
  name: str
  number: int
  dpt_codes: list[str]
  flags: ComObjectFlagsOut


class EnumOptionOut(BaseModel):
  """A single option in an enumeration parameter type."""

  value: str
  text: str


class ParamTypeOut(BaseModel):
  """The type descriptor for an application parameter (enumeration, integer, etc.)."""

  kind: str
  options: list[EnumOptionOut] = []
  min_value: int | None
  max_value: int | None
  size_bits: int | None


class ParameterOut(BaseModel):
  """API response schema for an application parameter with its current value and type."""

  id: str
  ref_id: str
  name: str
  text: str
  value: str
  param_type: ParamTypeOut | None


class AbsoluteSegmentOut(BaseModel):
  """An absolute memory segment from the application code, with address and binary data encoded as base64."""

  id: str
  address: int
  size: int
  data: bytes | None
  mask: bytes | None
  name: str | None
  user_memory: bool
  model_config = {"from_attributes": True}

  @field_serializer("data", "mask")
  def _encode(self, v: bytes | None) -> str | None:
    """Serialize binary data and mask fields as base64 strings."""
    return base64.b64encode(v).decode() if v is not None else None


class RelativeSegmentOut(BaseModel):
  """A relative memory segment from the application code, with offset and binary data encoded as base64."""

  id: str
  offset: int
  size: int
  data: bytes | None
  mask: bytes | None
  name: str | None
  model_config = {"from_attributes": True}

  @field_serializer("data", "mask")
  def _encode(self, v: bytes | None) -> str | None:
    """Serialize binary data and mask fields as base64 strings."""
    return base64.b64encode(v).decode() if v is not None else None


class CodeOut(BaseModel):
  """The complete loadable code for an application program, split into absolute and relative segments."""

  absolute_segments: list[AbsoluteSegmentOut]
  relative_segments: list[RelativeSegmentOut]
  model_config = {"from_attributes": True}


class ApplicationDetailOut(BaseModel):
  """Full on-demand detail for an application program, parsed live from the .knxprod archive."""

  application_id: str
  name: str
  manufacturer_id: str
  com_objects: list[ComObjectOut]
  parameters: list[ParameterOut]
  code: CodeOut | None
