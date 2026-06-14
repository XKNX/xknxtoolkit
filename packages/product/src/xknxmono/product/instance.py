"""`ApplicationInstance` — a single device's live, module-instance-resolved configuration.

It composes the static `Application` (templates: params, com-objects, dynamic tree, module defs) with
the per-device values the user has set, over the per-instance model from `parser/instantiate.py`
(so channel K1 and K2 are genuinely independent). It owns the in-memory state the GUI renders,
validates edits, and persists through a single injected callback that receives the full non-default
snapshot — the caller decides how to store it.

Identity: every parameter / com-object is addressed by a stable ``uid`` = its instance ref id
(e.g. ``…_MD-1_M-100_MI-1_P-1_R-1``), which the persistence layer maps to ``(module_instance_path, ref_id)``
rows. App-level members have ``module_instance_path == ""`` and ``uid == ref_id``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace

from . import application as _app
from .parser import dynamic as dy
from .parser.com_objects import ComObject, ComObjectFlags
from .parser.instantiate import ComObjectInstance, ParamInstance, instantiate
from .parser.modules import fill_name
from .parser.parameters import Parameter, ParamTypeKind

# the six overridable com-object flags (mirror of the project ComObject columns)
COM_OBJECT_FLAGS = (
    "communication",
    "read",
    "write",
    "transmit",
    "update",
    "read_on_init",
)


@dataclass(frozen=True)
class PersistedParam:
    """A parameter value loaded from storage (keyed the way the DB keys it)."""

    module_instance_path: str
    ref_id: str  # base/template ref id
    value: str


@dataclass(frozen=True)
class PersistedComObject:
    module_instance_path: str
    ref_id: str
    flags: dict[str, bool]  # only the overridden flags
    channel_id: str | None = None


@dataclass(frozen=True)
class InstanceSnapshot:
    """The full persistable state of a device: every non-default param value + every flag override."""

    parameters: list[PersistedParam] = field(default_factory=list[PersistedParam])
    com_objects: list[PersistedComObject] = field(
        default_factory=list[PersistedComObject]
    )


@dataclass
class ComObjectView:
    """A resolved com-object instance for the GUI: stable uid, resolved name, effective flags."""

    uid: str
    module_instance_path: str
    ref_id: str  # base ref
    name: str
    number: int
    dpt_codes: list[str]
    flags: ComObjectFlags


class ValidationError(ValueError):
    """Raised when a `set_param` value is rejected; the change is not persisted."""


class ApplicationInstance:
    # The full internal data structure, made explicit. The instance bundles are the construction
    # source of truth: ApplicationInstance collects its working indexes from them, then drops them
    # (the per-instance grouping is re-derivable from each member's module_instance_path).
    __slots__ = (
        "_co_uid_by_key",  # (module_instance_path, base_ref) -> com-object uid
        "_coms",  # uid -> ComObjectInstance, collected across all instance bundles
        "_defaults",  # uid -> default value (complete, incl. non-displayable params)
        "_on_persist",  # full-snapshot persist callback (None = detached/in-memory)
        "_overrides",  # com-object uid -> {flag: bool} overrides
        "_params",  # uid -> ParamInstance, collected across all instance bundles
        "_tree",  # the one dynamic/visibility tree, computed over all instances
        "_uid_by_key",  # (module_instance_path, base_ref) -> param uid
        "_values",  # uid -> current parameter value (defaults overridden by persisted)
    )

    def __init__(
        self,
        app: _app.Application,
        param_values: list[PersistedParam] | None = None,
        com_objects: list[PersistedComObject] | None = None,
        on_persist: Callable[[InstanceSnapshot], None] | None = None,
    ) -> None:
        # Built fresh per ApplicationInstance — the instances belong here, not on the (static,
        # shared) Application. A module instance is just another bundle in the flat list (the "" one
        # is the application itself); we collect their members into uid-keyed working indexes.
        self._tree: dy.DynamicElement
        instances, self._tree = instantiate(app.program)
        self._on_persist = on_persist

        self._params: dict[str, ParamInstance] = {
            uid: pi for inst in instances for uid, pi in inst.parameters.items()
        }
        self._coms: dict[str, ComObjectInstance] = {
            uid: ci for inst in instances for uid, ci in inst.com_objects.items()
        }
        self._defaults: dict[str, str] = {}
        for inst in instances:
            self._defaults.update(inst.default_values)

        # (module_instance_path, base_ref) -> uid, to resolve persisted rows onto instances.
        self._uid_by_key: dict[tuple[str, str], str] = {
            (pi.module_instance_path, pi.base_ref_id): uid
            for uid, pi in self._params.items()
        }
        self._co_uid_by_key: dict[tuple[str, str], str] = {
            (ci.module_instance_path, ci.base_ref_id): uid
            for uid, ci in self._coms.items()
        }

        # live values: defaults overridden by persisted, keyed by uid.
        self._values: dict[str, str] = dict(self._defaults)
        for pp in param_values or []:
            uid = self._uid_by_key.get((pp.module_instance_path, pp.ref_id))
            if uid is not None:
                self._values[uid] = pp.value

        # com-object flag overrides keyed by uid.
        self._overrides: dict[str, dict[str, bool]] = {}
        for pc in com_objects or []:
            uid = self._co_uid_by_key.get((pc.module_instance_path, pc.ref_id))
            if uid is not None and pc.flags:
                self._overrides[uid] = dict(pc.flags)

    # --- reads ---------------------------------------------------------------
    def value(self, uid: str) -> str:
        return self._values.get(uid, "")

    def visible_tree(self) -> list[dy.VisibleNode]:
        params_by_id = {uid: pi.parameter for uid, pi in self._params.items()}
        return dy.evaluate_tree(self._tree, self._values, params_by_id)

    def visible_parameters(self) -> list[Parameter]:
        visible_ids, _ = dy.collect_all_visible_refs(self._tree, self._values)
        out: list[Parameter] = []
        for uid in visible_ids:
            pi = self._params.get(uid)
            if pi is not None:
                out.append(
                    replace(
                        pi.parameter, value=self._values.get(uid, pi.parameter.value)
                    )
                )
        return out

    def visible_com_objects(self) -> list[ComObjectView]:
        co_list = [ci.com_object for ci in self._coms.values()]
        visible = dy.filter_visible_com_objects(co_list, self._tree, self._values)
        return [self._view(co) for co in visible]

    def _view(self, co: ComObject) -> ComObjectView:
        ci = self._coms[co.id]
        name = co.name
        if co.name_param_ref_id:
            name = fill_name(
                co.name_template, self._values.get(co.name_param_ref_id, "")
            )
        return ComObjectView(
            uid=co.id,
            module_instance_path=ci.module_instance_path,
            ref_id=ci.base_ref_id,
            name=name,
            number=co.number,
            dpt_codes=co.dpt_codes,
            flags=self._effective_flags(co),
        )

    def _effective_flags(self, co: ComObject) -> ComObjectFlags:
        overrides = self._overrides.get(co.id)
        if not overrides:
            return co.flags
        return replace(co.flags, **{k: v for k, v in overrides.items()})

    # --- edits ---------------------------------------------------------------
    def set_param(self, uid: str, value: str) -> None:
        pi = self._params.get(uid)
        if pi is None:
            raise KeyError(uid)
        self._validate(pi.parameter, value)
        self._values[uid] = value
        self._persist()

    def set_com_object_flag(self, uid: str, flag: str, value: bool | None) -> None:
        if flag not in COM_OBJECT_FLAGS:
            raise ValueError(f"unknown com-object flag {flag!r}")
        overrides = self._overrides.setdefault(uid, {})
        if value is None:
            overrides.pop(flag, None)
            if not overrides:
                self._overrides.pop(uid, None)
        else:
            overrides[flag] = value
        self._persist()

    def _validate(self, param: Parameter, value: str) -> None:
        pt = param.param_type
        if pt is None:
            return
        if pt.kind is ParamTypeKind.ENUM:
            if value not in {o.value for o in pt.options}:
                raise ValidationError(f"{value!r} is not an option of {param.text!r}")
        elif pt.kind in (ParamTypeKind.NUMBER, ParamTypeKind.TIME):
            try:
                iv = int(value)
            except ValueError as e:
                raise ValidationError(f"{value!r} is not an integer") from e
            if pt.min_value is not None and iv < pt.min_value:
                raise ValidationError(f"{iv} < min {pt.min_value}")
            if pt.max_value is not None and iv > pt.max_value:
                raise ValidationError(f"{iv} > max {pt.max_value}")
        elif pt.kind is ParamTypeKind.CHECKBOX and value not in ("0", "1"):
            raise ValidationError(f"{value!r} is not 0/1")

    # --- persistence ---------------------------------------------------------
    def snapshot(self) -> InstanceSnapshot:
        params = [
            PersistedParam(pi.module_instance_path, pi.base_ref_id, self._values[uid])
            for uid, pi in self._params.items()
            if uid in self._values
            and self._values[uid] != self._defaults.get(uid, pi.parameter.value)
        ]
        coms = [
            PersistedComObject(
                self._coms[uid].module_instance_path,
                self._coms[uid].base_ref_id,
                dict(flags),
            )
            for uid, flags in self._overrides.items()
            if flags
        ]
        return InstanceSnapshot(parameters=params, com_objects=coms)

    def _persist(self) -> None:
        if self._on_persist is not None:
            self._on_persist(self.snapshot())
