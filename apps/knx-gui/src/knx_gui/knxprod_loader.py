from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from xknx.product.archive import ProductArchive
from xknx.product.data import load_archive


class ParamTypeKind(Enum):
    ENUM = "enum"
    NUMBER = "number"
    TEXT = "text"
    TIME = "time"
    CHECKBOX = "checkbox"
    PICTURE = "picture"
    UNKNOWN = "unknown"


@dataclass
class EnumOption:
    value: str
    text: str


@dataclass
class ParsedParamType:
    kind: ParamTypeKind
    options: list[EnumOption] = field(default_factory=list)
    min_value: int | None = None
    max_value: int | None = None
    size_bits: int | None = None


@dataclass
class ParsedComObject:
    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: dict[str, bool]


@dataclass
class ParsedParameter:
    id: str
    ref_id: str
    name: str
    text: str
    value: str
    parameter_type_id: str
    param_type: ParsedParamType | None = None


@dataclass
class ParsedDeviceCandidate:
    application_id: str
    name: str
    manufacturer_id: str
    raw_com_objects: list[ParsedComObject]
    raw_parameters: list[ParsedParameter]


def _flag_enabled(value: Any) -> bool:
    if value is None:
        return False
    return str(value).split(".")[-1].lower() == "enabled"


def _dpt_codes(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        tokens = [str(v) for v in value if v]
    else:
        tokens = str(value).strip().split()
    codes: list[str] = []
    for token in tokens:
        parts = token.split("-")
        if len(parts) < 2 or parts[0] not in {"DPT", "DPST"}:
            continue
        try:
            major = int(parts[1])
            minor = int(parts[2]) if len(parts) >= 3 else 0
        except ValueError:
            continue
        codes.append(f"{major}.{minor}")
    return codes


def _resolve(*values: Any) -> Any:
    for v in values:
        if v is not None:
            return v
    return None


def _resolve_dpt_codes(*values: Any) -> list[str]:
    for v in values:
        if v is None:
            continue
        codes = _dpt_codes(v)
        if codes:
            return codes
    return []


def _to_com_object(ref: Any, base: Any | None) -> ParsedComObject:
    """Build a ParsedComObject by merging a ComObjectRef with its underlying ComObject.

    ComObjectRef values take precedence; fall back to the ComObject template.
    `ref` may be the bare ComObject when no ref is present.
    """
    name = (
        _resolve(getattr(ref, "text", None), getattr(base, "text", None) if base else None)
        or _resolve(getattr(ref, "name", None), getattr(base, "name", None) if base else None)
        or "Unnamed"
    )
    number_raw = _resolve(
        getattr(ref, "number", None) if hasattr(ref, "number") else None,
        getattr(base, "number", None) if base else None,
    )
    return ParsedComObject(
        id=getattr(ref, "id", "") or "",
        name=str(name),
        number=int(number_raw or 0),
        dpt_codes=_resolve_dpt_codes(
            getattr(ref, "datapoint_type", None),
            getattr(base, "datapoint_type", None) if base else None,
        ),
        flags={
            "communication": _flag_enabled(_resolve(
                getattr(ref, "communication_flag", None),
                getattr(base, "communication_flag", None) if base else None,
            )),
            "read": _flag_enabled(_resolve(
                getattr(ref, "read_flag", None),
                getattr(base, "read_flag", None) if base else None,
            )),
            "write": _flag_enabled(_resolve(
                getattr(ref, "write_flag", None),
                getattr(base, "write_flag", None) if base else None,
            )),
            "transmit": _flag_enabled(_resolve(
                getattr(ref, "transmit_flag", None),
                getattr(base, "transmit_flag", None) if base else None,
            )),
            "update": _flag_enabled(_resolve(
                getattr(ref, "update_flag", None),
                getattr(base, "update_flag", None) if base else None,
            )),
            "read_on_init": _flag_enabled(_resolve(
                getattr(ref, "read_on_init_flag", None),
                getattr(base, "read_on_init_flag", None) if base else None,
            )),
        },
    )


def _extract_com_objects(application_program: Any) -> list[ParsedComObject]:
    static = getattr(application_program, "static", None)
    if static is None:
        return []

    com_object_table = getattr(static, "com_object_table", None)
    bases: list[Any] = list(getattr(com_object_table, "com_object", []) or []) if com_object_table else []
    base_by_id: dict[str, Any] = {}
    for co in bases:
        co_id = getattr(co, "id", None)
        if co_id:
            base_by_id[co_id] = co

    com_object_refs = getattr(static, "com_object_refs", None)
    refs: list[Any] = list(getattr(com_object_refs, "com_object_ref", []) or []) if com_object_refs else []

    parsed: list[ParsedComObject] = []
    if refs:
        for ref in refs:
            ref_id = getattr(ref, "ref_id", None)
            base = base_by_id.get(ref_id) if ref_id else None
            parsed.append(_to_com_object(ref, base))
    else:
        for co in bases:
            parsed.append(_to_com_object(co, None))

    parsed.sort(key=lambda c: c.number)
    return parsed


def _parse_param_type(pt: Any) -> ParsedParamType:
    restrict = getattr(pt, "type_restriction", None)
    if restrict:
        enums = list(getattr(restrict, "enumeration", []) or [])
        if enums:
            options = [
                EnumOption(value=str(getattr(e, "value", "")), text=str(getattr(e, "text", "")))
                for e in enums
            ]
            return ParsedParamType(kind=ParamTypeKind.ENUM, options=options)

    type_number = getattr(pt, "type_number", None)
    if type_number:
        uihint = getattr(type_number, "uihint", None)
        if uihint and "checkbox" in str(uihint).lower():
            return ParsedParamType(kind=ParamTypeKind.CHECKBOX)
        min_val = getattr(type_number, "min_inclusive", None)
        max_val = getattr(type_number, "max_inclusive", None)
        size_bits = getattr(type_number, "size_in_bit", None)
        return ParsedParamType(
            kind=ParamTypeKind.NUMBER,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
            size_bits=int(size_bits) if size_bits is not None else None,
        )

    type_text = getattr(pt, "type_text", None)
    if type_text:
        size_bits = getattr(type_text, "size_in_bit", None)
        return ParsedParamType(
            kind=ParamTypeKind.TEXT,
            size_bits=int(size_bits) if size_bits is not None else None,
        )

    type_time = getattr(pt, "type_time", None)
    if type_time:
        min_val = getattr(type_time, "min_inclusive", None)
        max_val = getattr(type_time, "max_inclusive", None)
        return ParsedParamType(
            kind=ParamTypeKind.TIME,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
        )

    type_picture = getattr(pt, "type_picture", None)
    if type_picture:
        return ParsedParamType(kind=ParamTypeKind.PICTURE)

    return ParsedParamType(kind=ParamTypeKind.UNKNOWN)


def _extract_param_types(application_program: Any) -> dict[str, ParsedParamType]:
    static = getattr(application_program, "static", None)
    if static is None:
        return {}

    param_types = getattr(static, "parameter_types", None)
    if param_types is None:
        return {}

    types_list = list(getattr(param_types, "parameter_type", []) or [])
    result: dict[str, ParsedParamType] = {}
    for pt in types_list:
        pt_id = getattr(pt, "id", None)
        if pt_id:
            result[pt_id] = _parse_param_type(pt)
    return result


def _extract_parameters(application_program: Any, param_types: dict[str, ParsedParamType]) -> list[ParsedParameter]:
    static = getattr(application_program, "static", None)
    if static is None:
        return []

    parameters = getattr(static, "parameters", None)
    if parameters is None:
        return []

    base_params: list[Any] = list(getattr(parameters, "parameter", []) or [])
    base_by_id: dict[str, Any] = {}
    for p in base_params:
        p_id = getattr(p, "id", None)
        if p_id:
            base_by_id[p_id] = p

    param_refs_container = getattr(static, "parameter_refs", None)
    refs: list[Any] = list(getattr(param_refs_container, "parameter_ref", []) or []) if param_refs_container else []

    parsed: list[ParsedParameter] = []
    for ref in refs:
        ref_id = getattr(ref, "ref_id", None) or ""
        base = base_by_id.get(ref_id)
        name = _resolve(
            getattr(ref, "name", None),
            getattr(base, "name", None) if base else None,
        ) or ""
        text = _resolve(
            getattr(ref, "text", None),
            getattr(base, "text", None) if base else None,
        ) or ""
        if not text:
            continue
        value = _resolve(
            getattr(ref, "value", None),
            getattr(base, "value", None) if base else None,
        ) or ""
        param_type_id = str(getattr(base, "parameter_type", "") if base else "")
        param_type = param_types.get(param_type_id)
        parsed.append(ParsedParameter(
            id=getattr(ref, "id", "") or "",
            ref_id=ref_id,
            name=str(name),
            text=str(text),
            value=str(value),
            parameter_type_id=param_type_id,
            param_type=param_type,
        ))
    return parsed


def _walk_application_programs(knx: Any) -> list[Any]:
    apps: list[Any] = []
    manufacturer_data = getattr(knx, "manufacturer_data", None)
    if manufacturer_data is None:
        return apps
    for manufacturer in getattr(manufacturer_data, "manufacturer", []) or []:
        application_programs = getattr(manufacturer, "application_programs", None)
        if application_programs is None:
            continue
        apps.extend(getattr(application_programs, "application_program", []) or [])
    return apps


def parse_archive(path: str) -> list[ParsedDeviceCandidate]:
    candidates: list[ParsedDeviceCandidate] = []
    with ProductArchive(path) as archive:
        for manufacturer_id in sorted(archive.manufacturer_ids):
            data = load_archive(archive, manufacturer_id)
            for knx_app in data.applications:
                for app_program in _walk_application_programs(knx_app):
                    app_id = getattr(app_program, "id", "") or ""
                    name = getattr(app_program, "name", None) or app_id
                    param_types = _extract_param_types(app_program)
                    candidates.append(
                        ParsedDeviceCandidate(
                            application_id=app_id,
                            name=name,
                            manufacturer_id=manufacturer_id,
                            raw_com_objects=_extract_com_objects(app_program),
                            raw_parameters=_extract_parameters(app_program, param_types),
                        )
                    )
    return candidates
