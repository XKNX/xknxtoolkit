from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import dynamic


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
    read_locked: bool = False
    write_locked: bool = False
    transmit_locked: bool = False
    update_locked: bool = False
    read_on_init_locked: bool = False


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
    id: str | None = None
    name: str | None = None
    text: str | None = None
    number: int | None = None
    header_param_ref_id: str | None = None
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
class LdCtrlStep:
    kind: str
    applies_to: str
    details: str


@dataclass
class LoadProcedure:
    steps: list[LdCtrlStep] = field(default_factory=list)


@dataclass
class LoadProcedures:
    style: str
    procedures: list[LoadProcedure] = field(default_factory=list)


@dataclass
class DeviceApplication:
    application_id: str
    name: str
    manufacturer_id: str
    com_objects: list[ComObject]
    parameters: list[Parameter]
    dynamic: DynamicElement | None = None
    load_procedures: LoadProcedures | None = None

    _cached_tree: list[dynamic.TreeNode] | None = None
    _cached_params_by_id: dict[str, Parameter] | None = None

    def _get_visible_tree(
        self, param_values: dict[str, str] | None = None
    ) -> list[dynamic.VisibleNode]:
        from . import dynamic as dy

        if self._cached_tree is None:
            self._cached_tree = dy.build_tree(self.dynamic)
            self._cached_params_by_id = {p.id: p for p in self.parameters}

        if param_values is None:
            param_values = {p.id: p.value for p in self.parameters}

        return dy.evaluate_tree_cached(
            self._cached_tree, param_values, self._cached_params_by_id or {}
        )

    def get_visible_tree(
        self, param_values: dict[str, str] | None = None
    ) -> list[dynamic.VisibleNode]:
        return self._get_visible_tree(param_values)

    def visible_parameters(
        self, param_values: dict[str, str] | None = None
    ) -> list[Parameter]:
        if self.dynamic is None:
            return self.parameters

        visible_ids = self._collect_visible_param_ids(param_values)
        return [p for p in self.parameters if p.id in visible_ids]

    def visible_com_objects(
        self, param_values: dict[str, str] | None = None
    ) -> list[ComObject]:
        from . import dynamic as dy

        if param_values is None:
            param_values = {p.id: p.value for p in self.parameters}

        return dy.filter_visible_com_objects(
            self.com_objects, self.dynamic, param_values
        )

    def _collect_visible_param_ids(
        self, param_values: dict[str, str] | None
    ) -> set[str]:
        if param_values is None:
            param_values = {p.id: p.value for p in self.parameters}

        from . import dynamic as dy

        if not self.dynamic:
            return set()

        params, _ = dy.collect_all_visible_refs(self.dynamic, param_values)
        return params
