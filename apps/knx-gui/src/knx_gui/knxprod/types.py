from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


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
    options: list[EnumOption] = field(default_factory=list)
    min_value: int | None = None
    max_value: int | None = None
    size_bits: int | None = None


@dataclass
class ComObjectFlags:
    communication: bool = True
    read: bool = False
    write: bool = False
    transmit: bool = False
    update: bool = False
    read_on_init: bool = False


@dataclass
class ComObject:
    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: ComObjectFlags


@dataclass
class Parameter:
    id: str
    ref_id: str
    name: str
    text: str
    value: str
    param_type_id: str
    param_type: ParamType | None = None


@dataclass
class DynamicElement:
    param_ref_ids: list[str] = field(default_factory=list)
    com_object_ref_ids: list[str] = field(default_factory=list)
    children: list[DynamicElement] = field(default_factory=list)
    chooses: list[DynamicChoose] = field(default_factory=list)


@dataclass
class DynamicWhen:
    test_values: list[str] = field(default_factory=list)
    is_default: bool = False
    content: DynamicElement | None = None


@dataclass
class DynamicChoose:
    param_ref_id: str
    conditions: list[DynamicWhen] = field(default_factory=list)


@dataclass
class DeviceApplication:
    application_id: str
    name: str
    manufacturer_id: str
    com_objects: list[ComObject]
    parameters: list[Parameter]
    dynamic: DynamicElement | None = None

    def visible_parameters(self, param_values: dict[str, str] | None = None) -> list[Parameter]:
        if self.dynamic is None:
            return self.parameters

        if param_values is None:
            param_values = {p.id: p.value for p in self.parameters}

        visible_ids = self._collect_visible_param_refs(self.dynamic, param_values)
        return [p for p in self.parameters if p.id in visible_ids]

    def visible_com_objects(self, param_values: dict[str, str] | None = None) -> list[ComObject]:
        if self.dynamic is None:
            return self.com_objects

        if param_values is None:
            param_values = {p.id: p.value for p in self.parameters}

        visible_ids = self._collect_visible_co_refs(self.dynamic, param_values)
        return [co for co in self.com_objects if co.id in visible_ids]

    def _collect_visible_param_refs(self, element: DynamicElement, param_values: dict[str, str]) -> set[str]:
        visible: set[str] = set(element.param_ref_ids)

        for child in element.children:
            visible |= self._collect_visible_param_refs(child, param_values)

        for choose in element.chooses:
            matched = self._find_matching_when(choose, param_values)
            if matched and matched.content:
                visible |= self._collect_visible_param_refs(matched.content, param_values)

        return visible

    def _collect_visible_co_refs(self, element: DynamicElement, param_values: dict[str, str]) -> set[str]:
        visible: set[str] = set(element.com_object_ref_ids)

        for child in element.children:
            visible |= self._collect_visible_co_refs(child, param_values)

        for choose in element.chooses:
            matched = self._find_matching_when(choose, param_values)
            if matched and matched.content:
                visible |= self._collect_visible_co_refs(matched.content, param_values)

        return visible

    def _find_matching_when(self, choose: DynamicChoose, param_values: dict[str, str]) -> DynamicWhen | None:
        current_value = param_values.get(choose.param_ref_id, "")

        for when in choose.conditions:
            if current_value in when.test_values:
                return when

        for when in choose.conditions:
            if when.is_default:
                return when

        return None
