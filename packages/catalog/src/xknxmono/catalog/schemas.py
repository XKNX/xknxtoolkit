import base64
import datetime

from pydantic import BaseModel, field_serializer


class ManufacturerOut(BaseModel):
    id: str
    name: str | None
    model_config = {"from_attributes": True}


class ApplicationOut(BaseModel):
    id: str
    name: str
    application_number: int | None
    application_version: int | None
    mask_version: str | None
    is_secure_enabled: bool | None
    model_config = {"from_attributes": True}


class HardwareProgramOut(BaseModel):
    id: str
    hardware_id: str
    medium_types: list[str]
    registration_status: str | None
    registration_number: str | None
    registration_date: datetime.date | None
    application: ApplicationOut | None
    model_config = {"from_attributes": True}


class HardwareOut(BaseModel):
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
    id: str
    name: str
    number: str | None
    manufacturer_id: str
    parent_id: str | None
    children: list["CatalogSectionOut"] = []


# --- On-demand application detail (loaded from .knxprod at request time) ---

class ComObjectFlagsOut(BaseModel):
    communication: bool
    read: bool
    write: bool
    transmit: bool
    update: bool
    read_on_init: bool


class ComObjectOut(BaseModel):
    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: ComObjectFlagsOut


class EnumOptionOut(BaseModel):
    value: str
    text: str


class ParamTypeOut(BaseModel):
    kind: str
    options: list[EnumOptionOut] = []
    min_value: int | None
    max_value: int | None
    size_bits: int | None


class ParameterOut(BaseModel):
    id: str
    ref_id: str
    name: str
    text: str
    value: str
    param_type: ParamTypeOut | None


class AbsoluteSegmentOut(BaseModel):
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
        return base64.b64encode(v).decode() if v is not None else None


class RelativeSegmentOut(BaseModel):
    id: str
    offset: int
    size: int
    data: bytes | None
    mask: bytes | None
    name: str | None
    model_config = {"from_attributes": True}

    @field_serializer("data", "mask")
    def _encode(self, v: bytes | None) -> str | None:
        return base64.b64encode(v).decode() if v is not None else None


class CodeOut(BaseModel):
    absolute_segments: list[AbsoluteSegmentOut]
    relative_segments: list[RelativeSegmentOut]
    model_config = {"from_attributes": True}


class ApplicationDetailOut(BaseModel):
    application_id: str
    name: str
    manufacturer_id: str
    com_objects: list[ComObjectOut]
    parameters: list[ParameterOut]
    code: CodeOut | None
