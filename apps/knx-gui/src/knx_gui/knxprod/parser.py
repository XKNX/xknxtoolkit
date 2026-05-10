from __future__ import annotations

from typing import Any

from xknx.product.archive import ProductArchive
from xknx.product.data import load_archive

from .types import (
    ComObject,
    ComObjectFlags,
    DeviceApplication,
    DynamicChoose,
    DynamicElement,
    DynamicWhen,
    EnumOption,
    Parameter,
    ParamType,
    ParamTypeKind,
)


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


def _parse_com_object(ref: Any, base: Any | None) -> ComObject:
    name = (
        _resolve(getattr(ref, "text", None), getattr(base, "text", None) if base else None)
        or _resolve(getattr(ref, "name", None), getattr(base, "name", None) if base else None)
        or "Unnamed"
    )
    number_raw = _resolve(
        getattr(ref, "number", None) if hasattr(ref, "number") else None,
        getattr(base, "number", None) if base else None,
    )
    return ComObject(
        id=getattr(ref, "id", "") or "",
        name=str(name),
        number=int(number_raw or 0),
        dpt_codes=_resolve_dpt_codes(
            getattr(ref, "datapoint_type", None),
            getattr(base, "datapoint_type", None) if base else None,
        ),
        flags=ComObjectFlags(
            communication=_flag_enabled(
                _resolve(
                    getattr(ref, "communication_flag", None),
                    getattr(base, "communication_flag", None) if base else None,
                )
            ),
            read=_flag_enabled(
                _resolve(
                    getattr(ref, "read_flag", None),
                    getattr(base, "read_flag", None) if base else None,
                )
            ),
            write=_flag_enabled(
                _resolve(
                    getattr(ref, "write_flag", None),
                    getattr(base, "write_flag", None) if base else None,
                )
            ),
            transmit=_flag_enabled(
                _resolve(
                    getattr(ref, "transmit_flag", None),
                    getattr(base, "transmit_flag", None) if base else None,
                )
            ),
            update=_flag_enabled(
                _resolve(
                    getattr(ref, "update_flag", None),
                    getattr(base, "update_flag", None) if base else None,
                )
            ),
            read_on_init=_flag_enabled(
                _resolve(
                    getattr(ref, "read_on_init_flag", None),
                    getattr(base, "read_on_init_flag", None) if base else None,
                )
            ),
        ),
    )


def _extract_com_objects(static: Any) -> list[ComObject]:
    com_object_table = getattr(static, "com_object_table", None)
    com_objects_container = getattr(static, "com_objects", None)
    bases: list[Any] = []
    if com_object_table:
        bases = list(getattr(com_object_table, "com_object", []) or [])
    elif com_objects_container:
        bases = list(getattr(com_objects_container, "com_object", []) or [])
    base_by_id: dict[str, Any] = {}
    for co in bases:
        co_id = getattr(co, "id", None)
        if co_id:
            base_by_id[co_id] = co

    com_object_refs = getattr(static, "com_object_refs", None)
    refs: list[Any] = list(getattr(com_object_refs, "com_object_ref", []) or []) if com_object_refs else []

    parsed: list[ComObject] = []
    if refs:
        for ref in refs:
            ref_id = getattr(ref, "ref_id", None)
            base = base_by_id.get(ref_id) if ref_id else None
            parsed.append(_parse_com_object(ref, base))
    else:
        for co in bases:
            parsed.append(_parse_com_object(co, None))

    parsed.sort(key=lambda c: c.number)
    return parsed


def _parse_param_type(pt: Any) -> ParamType:
    restrict = getattr(pt, "type_restriction", None)
    if restrict:
        enums = list(getattr(restrict, "enumeration", []) or [])
        if enums:
            options = [
                EnumOption(value=str(getattr(e, "value", "")), text=str(getattr(e, "text", "")))
                for e in enums
            ]
            return ParamType(kind=ParamTypeKind.ENUM, options=options)

    type_number = getattr(pt, "type_number", None)
    if type_number:
        uihint = getattr(type_number, "uihint", None)
        if uihint and "checkbox" in str(uihint).lower():
            return ParamType(kind=ParamTypeKind.CHECKBOX)
        min_val = getattr(type_number, "min_inclusive", None)
        max_val = getattr(type_number, "max_inclusive", None)
        size_bits = getattr(type_number, "size_in_bit", None)
        return ParamType(
            kind=ParamTypeKind.NUMBER,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
            size_bits=int(size_bits) if size_bits is not None else None,
        )

    type_text = getattr(pt, "type_text", None)
    if type_text:
        size_bits = getattr(type_text, "size_in_bit", None)
        return ParamType(
            kind=ParamTypeKind.TEXT,
            size_bits=int(size_bits) if size_bits is not None else None,
        )

    type_time = getattr(pt, "type_time", None)
    if type_time:
        min_val = getattr(type_time, "min_inclusive", None)
        max_val = getattr(type_time, "max_inclusive", None)
        return ParamType(
            kind=ParamTypeKind.TIME,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
        )

    type_picture = getattr(pt, "type_picture", None)
    if type_picture:
        return ParamType(kind=ParamTypeKind.PICTURE)

    return ParamType(kind=ParamTypeKind.UNKNOWN)


def _extract_param_types(static: Any) -> dict[str, ParamType]:
    param_types = getattr(static, "parameter_types", None)
    if param_types is None:
        return {}

    types_list = list(getattr(param_types, "parameter_type", []) or [])
    result: dict[str, ParamType] = {}
    for pt in types_list:
        pt_id = getattr(pt, "id", None)
        if pt_id:
            result[pt_id] = _parse_param_type(pt)
    return result


def _extract_parameters(static: Any, param_types: dict[str, ParamType]) -> list[Parameter]:
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

    parsed: list[Parameter] = []
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
        parsed.append(
            Parameter(
                id=getattr(ref, "id", "") or "",
                ref_id=ref_id,
                name=str(name),
                text=str(text),
                value=str(value),
                param_type_id=param_type_id,
                param_type=param_type,
            )
        )
    return parsed


def _parse_dynamic_element(raw: Any, module_defs: dict[str, Any] | None = None) -> DynamicElement:
    if module_defs is None:
        module_defs = {}

    param_ref_ids: list[str] = []
    co_ref_ids: list[str] = []
    children: list[DynamicElement] = []
    chooses: list[DynamicChoose] = []

    for pr in list(getattr(raw, "parameter_ref_ref", []) or []):
        ref_id = getattr(pr, "ref_id", None)
        if ref_id:
            param_ref_ids.append(ref_id)

    for cr in list(getattr(raw, "com_object_ref_ref", []) or []):
        ref_id = getattr(cr, "ref_id", None)
        if ref_id:
            co_ref_ids.append(ref_id)

    for pb in list(getattr(raw, "parameter_block", []) or []):
        children.append(_parse_dynamic_element(pb, module_defs))

    for ch in list(getattr(raw, "channel", []) or []):
        children.append(_parse_dynamic_element(ch, module_defs))

    for module_ref in list(getattr(raw, "module", []) or []):
        ref_id = getattr(module_ref, "ref_id", None)
        if ref_id and ref_id in module_defs:
            mod_def = module_defs[ref_id]
            mod_dynamic = getattr(mod_def, "dynamic", None)
            if mod_dynamic:
                children.append(_parse_dynamic_element(mod_dynamic, module_defs))

    for choose_raw in list(getattr(raw, "choose", []) or []):
        chooses.append(_parse_dynamic_choose(choose_raw, module_defs))

    return DynamicElement(
        param_ref_ids=param_ref_ids,
        com_object_ref_ids=co_ref_ids,
        children=children,
        chooses=chooses,
    )


def _parse_dynamic_choose(raw: Any, module_defs: dict[str, Any] | None = None) -> DynamicChoose:
    param_ref_id = getattr(raw, "param_ref_id", None) or ""
    conditions: list[DynamicWhen] = []

    for when_raw in list(getattr(raw, "when", []) or []):
        conditions.append(_parse_dynamic_when(when_raw, module_defs))

    return DynamicChoose(param_ref_id=param_ref_id, conditions=conditions)


def _parse_dynamic_when(raw: Any, module_defs: dict[str, Any] | None = None) -> DynamicWhen:
    test_raw = getattr(raw, "test", None)
    default = bool(getattr(raw, "default", False))

    test_values: list[str] = []
    if test_raw is not None:
        test_str = str(test_raw)
        test_values = [v.strip() for v in test_str.split() if v.strip()]

    content = _parse_dynamic_element(raw, module_defs)

    return DynamicWhen(test_values=test_values, is_default=default, content=content)


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


def parse_archive(path: str) -> list[DeviceApplication]:
    applications: list[DeviceApplication] = []
    with ProductArchive(path) as archive:
        for manufacturer_id in sorted(archive.manufacturer_ids):
            data = load_archive(archive, manufacturer_id)
            for knx_app in data.applications:
                for app_program in _walk_application_programs(knx_app):
                    app_id = getattr(app_program, "id", "") or ""
                    name = getattr(app_program, "name", None) or app_id

                    static = getattr(app_program, "static", None)
                    dynamic = getattr(app_program, "dynamic", None)

                    if static is None:
                        continue

                    param_types = _extract_param_types(static)

                    module_defs_raw = getattr(app_program, "module_defs", None)
                    module_defs: dict[str, Any] = {}
                    if module_defs_raw:
                        for md in list(getattr(module_defs_raw, "module_def", []) or []):
                            md_id = getattr(md, "id", None)
                            if md_id:
                                module_defs[md_id] = md
                                md_static = getattr(md, "static", None)
                                if md_static:
                                    md_param_types = _extract_param_types(md_static)
                                    param_types.update(md_param_types)

                    parameters = _extract_parameters(static, param_types)
                    com_objects = _extract_com_objects(static)
                    for md in module_defs.values():
                        md_static = getattr(md, "static", None)
                        if md_static:
                            parameters.extend(_extract_parameters(md_static, param_types))
                            com_objects.extend(_extract_com_objects(md_static))

                    dynamic_tree = _parse_dynamic_element(dynamic, module_defs) if dynamic else None

                    applications.append(
                        DeviceApplication(
                            application_id=app_id,
                            name=name,
                            manufacturer_id=manufacturer_id,
                            com_objects=com_objects,
                            parameters=parameters,
                            dynamic=dynamic_tree,
                        )
                    )
    return applications
