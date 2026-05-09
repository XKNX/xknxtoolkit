from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from xknx.product.archive import ProductArchive
from xknx.product.data import load_archive


@dataclass
class ParsedComObject:
    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: dict[str, bool]


@dataclass
class ParsedDeviceCandidate:
    application_id: str
    name: str
    manufacturer_id: str
    raw_com_objects: list[ParsedComObject]


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


def _extract_com_objects(application_program: Any) -> list[ParsedComObject]:
    static = getattr(application_program, "static", None)
    if static is None:
        return []
    com_object_table = getattr(static, "com_object_table", None)
    if com_object_table is None:
        return []
    raw_com_objects: list[Any] = list(getattr(com_object_table, "com_object", []) or [])
    parsed: list[ParsedComObject] = []
    for co in raw_com_objects:
        parsed.append(
            ParsedComObject(
                id=getattr(co, "id", "") or "",
                name=getattr(co, "text", None) or getattr(co, "name", None) or "Unnamed",
                number=int(getattr(co, "number", 0) or 0),
                dpt_codes=_dpt_codes(getattr(co, "datapoint_type", None)),
                flags={
                    "communication": _flag_enabled(getattr(co, "communication_flag", None)),
                    "read": _flag_enabled(getattr(co, "read_flag", None)),
                    "write": _flag_enabled(getattr(co, "write_flag", None)),
                    "transmit": _flag_enabled(getattr(co, "transmit_flag", None)),
                    "update": _flag_enabled(getattr(co, "update_flag", None)),
                    "read_on_init": _flag_enabled(getattr(co, "read_on_init_flag", None)),
                },
            )
        )
    parsed.sort(key=lambda c: c.number)
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
                    candidates.append(
                        ParsedDeviceCandidate(
                            application_id=app_id,
                            name=name,
                            manufacturer_id=manufacturer_id,
                            raw_com_objects=_extract_com_objects(app_program),
                        )
                    )
    return candidates
