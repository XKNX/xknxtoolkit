"""Module-def / module-instance handling, shared by com-object resolution and the dynamic tree.

xsdata represents every xs:choice content model as a single ordered `choice` list of typed
union members, so the dispatch sets and the small structural Protocols used to walk those trees
live here too.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from xknxmono.models.intermediate import (
    ApplicationProgram,
    ApplicationProgramChannel,
    ApplicationProgramStatic,
    ChannelChoose,
    ChannelIndependentBlock,
    ComObjectParameterBlock,
    ComObjectParameterChoose,
    DependentChannelChoose,
    Module,
    ModuleDef,
    ModuleDefStatic,
    ModuleNumericArg,
    Repeat,
)

# An application-program static or a module-def static (overlapping but not identical shapes).
Static = ApplicationProgramStatic | ModuleDefStatic

# Dispatch sets for the dynamic xs:choice members.
CHOOSE_TYPES = (ComObjectParameterChoose, ChannelChoose, DependentChannelChoose)
CONTAINER_TYPES = (
    ComObjectParameterBlock,
    ApplicationProgramChannel,
    ChannelIndependentBlock,
    Repeat,
)


class ChoiceContainer(Protocol):
    """Any dynamic node carrying an xs:choice content model (dynamic root, container, or when).

    The members are declared as read-only properties (not attributes) so the protocol is covariant:
    a concrete IR node whose `choice` is `list[SpecificUnion]` then satisfies `Sequence[object]`
    (a protocol *attribute* would be invariant and reject it)."""

    @property
    def choice(self) -> Sequence[object]: ...


class When(Protocol):
    @property
    def test(self) -> object: ...
    @property
    def default(self) -> object: ...
    @property
    def choice(self) -> Sequence[object]: ...


class Choose(Protocol):
    @property
    def param_ref_id(self) -> str | None: ...
    @property
    def when(self) -> Sequence[When]: ...


# module-def id -> {argument id -> argument name}
ArgNames = dict[str, dict[str, str]]


@dataclass(frozen=True)
class Modules:
    """An application program's module defs plus the per-def argument-name maps."""

    defs: dict[str, ModuleDef]
    arg_names: ArgNames


@dataclass
class ModuleInstance:
    ref_id: str
    text_args: dict[str, str]


def collect(app: ApplicationProgram) -> Modules:
    defs: dict[str, ModuleDef] = {}
    arg_names: ArgNames = {}
    if app.module_defs is not None:
        for md in app.module_defs.module_def:
            if md.id:
                defs[md.id] = md
                arg_names[md.id] = (
                    {a.id: a.name for a in md.arguments.argument if a.id and a.name}
                    if md.arguments is not None
                    else {}
                )
    return Modules(defs=defs, arg_names=arg_names)


def iter_statics(app: ApplicationProgram, modules: Modules) -> list[Static]:
    """The application static plus every module-def static (all share the extraction logic)."""
    statics: list[Static] = [app.static]
    statics.extend(md.static for md in modules.defs.values())
    return statics


@dataclass(frozen=True)
class ModuleArgument:
    """A resolved argument of a ``<Module>`` instance: the def-side metadata (name, kind,
    ``allocates`` allocator ref, ``alignment``) joined with the instance's value. The numeric ones
    (``ObjNumberBase_*`` / ``ParamOffsBase_*`` …) are the per-instance numbering/memory substrate;
    they are a *construction input* (resolved onto com-objects/params), not parameters."""

    id: str
    name: str
    is_numeric: bool
    value: str
    allocates: str | None = None
    alignment: str | None = None


def module_arguments(module: Module, modules: Modules) -> list[ModuleArgument]:
    """Resolve a module reference's arguments, joining each value with its def-side metadata."""
    mod_def = modules.defs.get(module.ref_id or "")
    meta = (
        {a.id: a for a in mod_def.arguments.argument if a.id}
        if mod_def is not None and mod_def.arguments is not None
        else {}
    )
    out: list[ModuleArgument] = []
    for arg in module.choice:
        ref_id = arg.ref_id or ""
        d = meta.get(ref_id)
        out.append(
            ModuleArgument(
                id=ref_id,
                name=d.name if d and d.name else "",
                is_numeric=isinstance(arg, ModuleNumericArg),
                value=str(arg.value) if arg.value is not None else "",
                allocates=str(d.allocates) if d and d.allocates is not None else None,
                alignment=str(d.alignment.value) if d else None,
            )
        )
    return out


def text_args_of(arguments: list[ModuleArgument]) -> dict[str, str]:
    """The ``{{ArgName}}`` substitution map derived from resolved arguments: keyed by the def-side
    arg name, falling back to the ref id for an un-named text arg (nested-module passthrough).
    This is what name templates substitute against — derivable from the full argument list, so the
    module factory takes only ``arguments`` and computes this itself."""
    out: dict[str, str] = {}
    for a in arguments:
        if not a.value:
            continue
        if a.name:
            out[a.name] = a.value
        elif not a.is_numeric and "_A-" not in a.id:
            out[a.id] = a.value
    return out


def text_args(module: Module, modules: Modules) -> dict[str, str]:
    """Resolve a module reference's text/numeric args to {module-def arg name: value}."""
    return text_args_of(module_arguments(module, modules))


_NAME_PLACEHOLDER = re.compile(r"\{\{0(?::[^}]*)?\}\}")


def apply_text_args(text: str, text_args: dict[str, str]) -> str:
    """Substitute the module ``{{ArgName}}`` / ``{{ArgName:fmt}}`` text-args. The ``{{0}}`` name
    placeholder (and any other tokens) are left in place for :func:`fill_name` to resolve later,
    against live parameter values — that's the channel/object name the user types."""
    for arg_name, arg_value in text_args.items():
        text = re.sub(
            r"\{\{" + re.escape(arg_name) + r"(?::[^}]*)?\}\}", arg_value, text
        )
    return text


def fill_name(template: str, name_value: str) -> str:
    """Fill the ``{{0}}`` / ``{{0:fmt}}`` name placeholder, drop any remaining ``{{...}}`` tokens,
    and tidy whitespace. With an empty name this leaves the bare ``()`` ETS shows by default."""
    text = _NAME_PLACEHOLDER.sub(name_value, template)
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def substitute_template(
    text: str, function_text: object, text_args: dict[str, str]
) -> str:
    """Fill a ``{{ArgName}}`` template and drop the rest (for static labels with no name value)."""
    return fill_name(apply_text_args(text, text_args), "")


def instances(node: ChoiceContainer, modules: Modules) -> list[ModuleInstance]:
    """Walk the dynamic xs:choice tree collecting module instantiations."""
    out: list[ModuleInstance] = []
    for item in node.choice:
        if isinstance(item, Module):
            out.append(ModuleInstance(item.ref_id or "", text_args(item, modules)))
        elif isinstance(item, CHOOSE_TYPES):
            for when in item.when:
                out.extend(instances(when, modules))
        elif isinstance(item, CONTAINER_TYPES):
            out.extend(instances(item, modules))
    return out
