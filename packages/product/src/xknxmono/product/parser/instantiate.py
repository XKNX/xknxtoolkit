"""Materialize an application into per-instance bundles.

The dynamic tree references module-def members by their *template* ids (e.g. ``…_MD-1_P-1_R-1``),
shared by every instance of that module. ETS expands each ``<Module>`` reference into a distinct
instance, encoding it as ``{module_ref_id}_MI-{k}`` and splicing that segment into every member ref:

    template  …_MD-1_P-1_R-1   →   instance  …_MD-1_M-100_MI-1_P-1_R-1   (channel K1)
                                              …_MD-1_M-200_MI-1_P-1_R-1   (channel K2)

`instantiate` returns a **flat list of `InstanceModel` bundles** (the ``""`` bundle is the
application itself; the rest are module instances) plus the one rewritten dynamic tree used for
visibility. Each bundle owns its parameters/com-objects; module nesting is encoded in
``module_instance_path`` (a prefix relationship), matching how ETS stores ``<ModuleInstances>`` flat.

Bundles are produced by factories — :func:`global_instance` and :func:`module_instance`. Module
arguments (the ``ObjNumberBase_*`` / ``ParamOffsBase_*`` substrate) are a *construction input* to the
module factory — consumed to substitute names and (task #15) resolve per-instance com-object numbers
and parameter offsets onto the members — not stored on the bundle.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from xknxmono.models.intermediate import ApplicationProgram

from . import com_objects as co_mod
from . import modules
from . import parameters as param_mod
from .com_objects import ComObject
from .dynamic import DynamicElement, build_app_dynamic_tree
from .modules import ModuleArgument
from .parameters import Parameter, ParamType


@dataclass
class ParamInstance:
    """A parameter materialized for one instance bundle (module instance or app-level)."""

    uid: str  # globally-unique instance ref id (== parameter.id)
    module_instance_path: (
        str  # "" for app-level, e.g. "MD-1_M-100_MI-1" for a module instance
    )
    base_ref_id: (
        str  # the template ref id this was expanded from (== uid when app-level)
    )
    parameter: Parameter


@dataclass
class ComObjectInstance:
    uid: str
    module_instance_path: str
    base_ref_id: str
    com_object: ComObject


@dataclass
class InstanceModel:
    """One instance bundle — the application (``module_instance_path == ""``) or a module instance.
    A pure ownership bundle: no dynamic tree (visibility is global), no arguments (construction-only).

    ``default_values`` is the *complete* default map for this bundle's refs, including non-displayable
    internal params (which ``parameters`` omits) — visibility conditions need those."""

    module_instance_path: str
    def_id: str | None
    parameters: dict[str, ParamInstance] = field(
        default_factory=dict[str, ParamInstance]
    )
    com_objects: dict[str, ComObjectInstance] = field(
        default_factory=dict[str, ComObjectInstance]
    )
    default_values: dict[str, str] = field(default_factory=dict[str, str])


class NoDynamicSectionError(ValueError):
    """Raised when an application has no ``<Dynamic>`` section — it cannot be instantiated."""


# --- ref rewriting (template id -> per-instance id) -------------------------------


def _subst(ref: str, def_id: str, instance_id: str) -> str:
    """Splice the instance segment in: ``{def_id}{rest}`` → ``{instance_id}{rest}`` (boundary-safe)."""
    if ref == def_id:
        return instance_id
    if ref.startswith(def_id + "_"):
        return instance_id + ref[len(def_id) :]
    return ref


def _rewrite_element(
    el: DynamicElement, def_id: str, instance_id: str, *, root: bool
) -> None:
    """Rewrite one element's refs (and, except at the instance root, its id) with the instance sub."""
    if root:
        el.id = instance_id
    elif el.id:
        el.id = _subst(el.id, def_id, instance_id)
    el.param_ref_ids = [_subst(r, def_id, instance_id) for r in el.param_ref_ids]
    el.com_object_ref_ids = [
        _subst(r, def_id, instance_id) for r in el.com_object_ref_ids
    ]
    if el.header_param_ref_id:
        el.header_param_ref_id = _subst(el.header_param_ref_id, def_id, instance_id)
    if el.name_param_ref_id:
        el.name_param_ref_id = _subst(el.name_param_ref_id, def_id, instance_id)
    if el.grid is not None:
        for cell in el.grid.cells:
            if cell.param_ref_id:
                cell.param_ref_id = _subst(cell.param_ref_id, def_id, instance_id)
    for choose in el.chooses:
        choose.param_ref_id = _subst(choose.param_ref_id, def_id, instance_id)
        for when in choose.conditions:
            if when.content is not None:
                _rewrite_element(when.content, def_id, instance_id, root=False)
    for child in el.children:
        _rewrite_element(child, def_id, instance_id, root=False)


@dataclass
class _Ref:
    """A located module-instance reference, after its subtree has been rewritten."""

    def_id: str
    instance_id: str
    arguments: list[ModuleArgument]


def _collect_refs(
    el: DynamicElement, counters: dict[str, int], out: list[_Ref]
) -> None:
    """Find module-instance roots, rewrite each subtree in place, and record the reference."""
    if el.module_def_id:
        def_id = el.module_def_id
        node_id = el.id or def_id
        k = counters.get(node_id, 0) + 1
        counters[node_id] = k
        instance_id = f"{node_id}_MI-{k}"
        _rewrite_element(el, def_id, instance_id, root=True)
        out.append(_Ref(def_id, instance_id, el.module_arguments or []))
    for child in el.children:
        _collect_refs(child, counters, out)
    for choose in el.chooses:
        for when in choose.conditions:
            if when.content is not None:
                _collect_refs(when.content, counters, out)


# --- factories --------------------------------------------------------------------


def _instance_text(text: str, text_args: dict[str, str]) -> str:
    return modules.substitute_template(text, None, text_args) if text_args else text


def global_instance(
    static: modules.Static, param_types: dict[str, ParamType]
) -> InstanceModel:
    """The application-level bundle: ``app.static`` members keep their template ids (no rewrite)."""
    params = {
        p.id: ParamInstance(p.id, "", p.id, p)
        for p in param_mod.params_from_static(static, param_types)
    }
    com_objects = {
        co.id: ComObjectInstance(co.id, "", co.id, co)
        for co in co_mod.from_static(static)
    }
    return InstanceModel(
        module_instance_path="",
        def_id=None,
        parameters=params,
        com_objects=com_objects,
        default_values=dict(param_mod.values_from_static(static)),
    )


def module_instance(
    static: modules.Static,
    param_types: dict[str, ParamType],
    app_id: str,
    def_id: str,
    instance_id: str,
    arguments: list[ModuleArgument],
) -> InstanceModel:
    """One module instance: the module-def static's members re-keyed under ``instance_id`` (the
    ``{def_id}`` prefix → ``{instance_id}``). Names are filled from the text args and the instance
    path is derived here — both fall out of ``instance_id`` + ``arguments``. Numeric arguments
    resolve numbers/offsets onto the members (task #15)."""
    module_instance_path = (
        instance_id[len(app_id) + 1 :]
        if instance_id.startswith(app_id + "_")
        else instance_id
    )
    text_args = modules.text_args_of(arguments)

    params: dict[str, ParamInstance] = {}
    for p in param_mod.params_from_static(static, param_types):
        uid = _subst(p.id, def_id, instance_id)
        clone = replace(p, id=uid, text=_instance_text(p.text, text_args))
        params[uid] = ParamInstance(uid, module_instance_path, p.id, clone)

    defaults = {
        _subst(ref_id, def_id, instance_id): value
        for ref_id, value in param_mod.values_from_static(static).items()
    }

    com_objects: dict[str, ComObjectInstance] = {}
    for co in co_mod.from_static(static, text_args):
        uid = _subst(co.id, def_id, instance_id)
        name_param = (
            _subst(co.name_param_ref_id, def_id, instance_id)
            if co.name_param_ref_id
            else None
        )
        clone = replace(co, id=uid, name_param_ref_id=name_param)
        com_objects[uid] = ComObjectInstance(uid, module_instance_path, co.id, clone)

    _resolve_numbering(com_objects, params, arguments)
    return InstanceModel(
        module_instance_path=module_instance_path,
        def_id=def_id,
        parameters=params,
        com_objects=com_objects,
        default_values=defaults,
    )


def _resolve_numbering(
    com_objects: dict[str, ComObjectInstance],
    params: dict[str, ParamInstance],
    arguments: list[ModuleArgument],
) -> None:
    """Resolve per-instance com-object numbers and parameter memory offsets from the numeric
    arguments (``ObjNumberBase_*`` / ``ParamOffsBase_*`` …). Task #15 — wired but not yet applied;
    the exact arithmetic is validated against an ETS ``.knxproj`` export."""
    return


def instantiate(app: ApplicationProgram) -> tuple[list[InstanceModel], DynamicElement]:
    """Resolve an application into its flat instance bundles + the one rewritten dynamic tree."""
    mods = modules.collect(app)
    tree = build_app_dynamic_tree(app)
    if tree is None:
        raise NoDynamicSectionError(app.id)
    param_types = param_mod.extract_types(app)

    refs: list[_Ref] = []
    _collect_refs(tree, {}, refs)

    instances: list[InstanceModel] = [global_instance(app.static, param_types)]
    for ref in refs:
        module_def = mods.defs.get(ref.def_id)
        if module_def is None:
            continue
        instances.append(
            module_instance(
                module_def.static,
                param_types,
                app.id,
                ref.def_id,
                ref.instance_id,
                ref.arguments,
            )
        )
    return instances, tree
