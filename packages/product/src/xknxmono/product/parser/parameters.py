"""Resolve IR parameters/refs into `Parameter`, and classify ParameterType variants into `ParamType`.

Each ParameterType variant is the single member of `ParameterType.choice`; one typed handler per
variant, dispatched on its concrete type.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramStatic,
    ApplicationProgramStaticParameters,
    ApplicationProgramStaticParametersParameter,
    ApplicationProgramStaticParametersUnion,
    ParameterRef,
    ParameterType,
    ParameterTypeTypeFloat,
    ParameterTypeTypeNumber,
    ParameterTypeTypePicture,
    ParameterTypeTypeRestriction,
    ParameterTypeTypeText,
    ParameterTypeTypeTime,
)

from . import modules


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
class ParamType:
    kind: ParamTypeKind
    options: list[EnumOption] = field(default_factory=list[EnumOption])
    min_value: int | None = None
    max_value: int | None = None
    size_bits: int | None = None


@dataclass
class Parameter:
    """A parameter resolved from a ParameterRef merged with its base Parameter."""

    id: str
    ref_id: str
    name: str
    text: str
    value: str
    param_type_id: str
    param_type: ParamType | None = None


def _as_int(value: int | str | None) -> int | None:
    return int(value) if value is not None else None


# --- ParameterType variants (one typed handler each) ------------------------------


def _restriction(v: ParameterTypeTypeRestriction) -> ParamType:
    if not v.enumeration:
        return ParamType(kind=ParamTypeKind.UNKNOWN)
    return ParamType(
        kind=ParamTypeKind.ENUM,
        options=[
            EnumOption(value=str(e.value), text=str(e.text or ""))
            for e in v.enumeration
        ],
    )


def _number(v: ParameterTypeTypeNumber) -> ParamType:
    if v.uihint is not None and "checkbox" in str(v.uihint).lower():
        return ParamType(kind=ParamTypeKind.CHECKBOX)
    return ParamType(
        kind=ParamTypeKind.NUMBER,
        min_value=_as_int(v.min_inclusive),
        max_value=_as_int(v.max_inclusive),
        size_bits=_as_int(v.size_in_bit),
    )


def _text(v: ParameterTypeTypeText) -> ParamType:
    return ParamType(kind=ParamTypeKind.TEXT, size_bits=_as_int(v.size_in_bit))


def _time(v: ParameterTypeTypeTime) -> ParamType:
    return ParamType(
        kind=ParamTypeKind.TIME,
        min_value=_as_int(v.min_inclusive),
        max_value=_as_int(v.max_inclusive),
    )


def _picture(v: ParameterTypeTypePicture) -> ParamType:
    return ParamType(kind=ParamTypeKind.PICTURE)


def _float(v: ParameterTypeTypeFloat) -> ParamType:
    return ParamType(kind=ParamTypeKind.NUMBER)


_HANDLERS: dict[type, Callable[..., ParamType]] = {
    ParameterTypeTypeRestriction: _restriction,
    ParameterTypeTypeNumber: _number,
    ParameterTypeTypeText: _text,
    ParameterTypeTypeTime: _time,
    ParameterTypeTypePicture: _picture,
    ParameterTypeTypeFloat: _float,
}


def parse_param_type(pt: ParameterType) -> ParamType:
    handler = _HANDLERS.get(type(pt.choice))
    return handler(pt.choice) if handler else ParamType(kind=ParamTypeKind.UNKNOWN)


def _types_from_static(static: modules.Static) -> dict[str, ParamType]:
    holder = (
        static.parameter_types if isinstance(static, ApplicationProgramStatic) else None
    )
    if holder is None:
        return {}
    return {pt.id: parse_param_type(pt) for pt in holder.parameter_type if pt.id}


# --- parameters -------------------------------------------------------------------


def _iter_bases(
    container: ApplicationProgramStaticParameters
    | ApplicationProgramStaticParametersUnion,
) -> Iterator[ApplicationProgramStaticParametersParameter]:
    """Yield base Parameter elements. A Union holds its parameters in `.parameter` (its own
    `.choice` is just the MemoryUnion/PropertyUnion discriminator); the top-level Parameters holds
    Parameter | Union members in its compound `.choice`."""
    if isinstance(container, ApplicationProgramStaticParametersUnion):
        # The IR's Union holds its own parallel `...UnionParameter` type; treated uniformly here.
        yield from container.parameter  # pyright: ignore[reportReturnType]
        return
    for item in container.choice:
        if isinstance(item, ApplicationProgramStaticParametersUnion):
            yield from _iter_bases(item)
        else:
            yield item


def _params_from_static(
    static: modules.Static, param_types: dict[str, ParamType]
) -> list[Parameter]:
    parameters = static.parameters
    if parameters is None:
        return []
    # `static.parameters` is the app-static or module-def variant; both expose the same shape.
    base_by_id = {p.id: p for p in _iter_bases(parameters) if p.id}  # pyright: ignore[reportArgumentType]

    refs_container = static.parameter_refs
    refs: list[ParameterRef] = refs_container.parameter_ref if refs_container else []

    parsed: list[Parameter] = []
    for ref in refs:
        ref_id = ref.ref_id or ""
        base = base_by_id.get(ref_id)
        text = ref.text or (base.text if base else None) or ""
        if not text:
            continue
        name = ref.name or (base.name if base else None) or ""
        value = ref.value or (base.value if base else None) or ""
        param_type_id = str(base.parameter_type) if base and base.parameter_type else ""
        parsed.append(
            Parameter(
                id=ref.id or "",
                ref_id=ref_id,
                name=name,
                text=text,
                value=value,
                param_type_id=param_type_id,
                param_type=param_types.get(param_type_id),
            )
        )
    return parsed


# --- application-program entry points ---------------------------------------------


def extract_types(app: ApplicationProgram) -> dict[str, ParamType]:
    param_types: dict[str, ParamType] = {}
    for static in modules.iter_statics(app, modules.collect(app)):
        param_types.update(_types_from_static(static))
    return param_types


def extract(app: ApplicationProgram) -> list[Parameter]:
    param_types = extract_types(app)
    parameters: list[Parameter] = []
    for static in modules.iter_statics(app, modules.collect(app)):
        parameters.extend(_params_from_static(static, param_types))
    return parameters
