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
    ModuleTextArg,
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


def text_args(module: Module, modules: Modules) -> dict[str, str]:
    """Resolve a module reference's text/numeric args to {module-def arg name: value}."""
    names = modules.arg_names.get(module.ref_id or "", {})
    out: dict[str, str] = {}
    for arg in module.choice:
        ref_id = arg.ref_id or ""
        value = arg.value
        if not ref_id or value is None:
            continue
        if name := names.get(ref_id):
            out[name] = str(value)
        elif isinstance(arg, ModuleTextArg) and "_A-" not in ref_id:
            out[ref_id] = str(value)
    return out


def substitute_template(
    text: str, function_text: object, text_args: dict[str, str]
) -> str:
    """Fill a {{0}} (function text) / {{ArgName}} (module text-arg) template; drop the rest."""
    result = text
    if function_text:
        result = result.replace("{{0}}", str(function_text))
    for arg_name, arg_value in text_args.items():
        result = result.replace(f"{{{{{arg_name}}}}}", arg_value)
    result = re.sub(r"\{\{[^}]+\}\}", "", result)
    result = re.sub(r"\s+", " ", result)
    return result.strip()


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
