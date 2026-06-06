"""Resolve IR ComObjectRefs against their base ComObjects into the resolved `ComObject` type."""

from __future__ import annotations

from dataclasses import dataclass

from xknxmono.models import intermediate as ir

from . import modules


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
    """A communication object resolved from a ComObjectRef merged with its base ComObject."""

    id: str
    name: str
    number: int
    dpt_codes: list[str]
    flags: ComObjectFlags
    # The name template with module args applied but the ``{{0}}`` placeholder intact, plus the
    # parameter whose value fills it — so the displayed name tracks the channel name the user types.
    name_template: str = ""
    name_param_ref_id: str | None = None


def _first(*values: object) -> object | None:
    """First non-None value (ref overrides base)."""
    for v in values:
        if v is not None:
            return v
    return None


def _flag(*values: object) -> bool:
    """True when the first present Enable-style enum resolves to 'Enabled'."""
    value = _first(*values)
    return value is not None and str(value).split(".")[-1].lower() == "enabled"


def _dpt_codes(*values: list[str] | None) -> list[str]:
    """Parse the first present DPT field (e.g. 'DPST-1-1' / 'DPT-1') into 'major.minor' codes."""
    for value in values:
        if not value:
            continue
        codes: list[str] = []
        for token in value:
            parts = token.split("-")
            if len(parts) < 2 or parts[0] not in {"DPT", "DPST"}:
                continue
            try:
                major = int(parts[1])
                minor = int(parts[2]) if len(parts) >= 3 else 0
            except ValueError:
                continue
            codes.append(f"{major}.{minor}")
        if codes:
            return codes
    return []


def _parse(
    base: ir.ComObject | None,
    ref: ir.ComObjectRef | None,
    text_args: dict[str, str] | None = None,
) -> ComObject:
    raw_name = (
        _first(ref.text if ref else None, base.text if base else None)
        or _first(ref.name if ref else None, base.name if base else None)
        or "Unnamed"
    )
    name_param_ref_id = _first(
        ref.text_parameter_ref_id if ref else None,
        getattr(base, "text_parameter_ref_id", None) if base else None,
    )
    # Apply module args now, keep the {{0}} name placeholder; the name itself is filled later from
    # the value of ``name_param_ref_id`` (so it follows the channel name the user enters).
    name_template = modules.apply_text_args(str(raw_name), text_args or {})
    name = modules.fill_name(name_template, "")

    rb = ref, base
    return ComObject(
        id=(ref.id if ref else None) or (base.id if base else None) or "",
        name=name,
        name_template=name_template,
        name_param_ref_id=str(name_param_ref_id) if name_param_ref_id else None,
        number=int((base.number if base else None) or 0),
        dpt_codes=_dpt_codes(
            ref.datapoint_type if ref else None,
            base.datapoint_type if base else None,
        ),
        flags=ComObjectFlags(
            communication=_flag(*(o.communication_flag if o else None for o in rb)),
            read=_flag(*(o.read_flag if o else None for o in rb)),
            write=_flag(*(o.write_flag if o else None for o in rb)),
            transmit=_flag(*(o.transmit_flag if o else None for o in rb)),
            update=_flag(*(o.update_flag if o else None for o in rb)),
            read_on_init=_flag(*(o.read_on_init_flag if o else None for o in rb)),
            read_locked=bool(base.read_flag_locked) if base else False,
            write_locked=bool(base.write_flag_locked) if base else False,
            transmit_locked=bool(base.transmit_flag_locked) if base else False,
            update_locked=bool(base.update_flag_locked) if base else False,
            read_on_init_locked=bool(base.read_on_init_flag_locked) if base else False,
        ),
    )


def from_static(
    static: modules.Static, text_args: dict[str, str] | None = None
) -> list[ComObject]:
    table = (
        static.com_object_table
        if isinstance(static, ir.ApplicationProgramStatic)
        else None
    )
    bases: list[ir.ComObject] = table.com_object if table else []
    base_by_id = {co.id: co for co in bases if co.id}

    refs_container = static.com_object_refs
    refs: list[ir.ComObjectRef] = (
        refs_container.com_object_ref if refs_container else []
    )

    if refs:
        parsed = [
            _parse(base_by_id.get(r.ref_id) if r.ref_id else None, r, text_args)
            for r in refs
        ]
    else:
        parsed = [_parse(co, None, text_args) for co in bases]

    parsed.sort(key=lambda c: c.number)
    return parsed


def extract(app: ir.ApplicationProgram) -> list[ComObject]:
    mods = modules.collect(app)
    com_objects = from_static(app.static)

    instantiated: set[str] = set()
    if app.dynamic is not None:
        for instance in modules.instances(app.dynamic, mods):
            instantiated.add(instance.ref_id)
            md = mods.defs.get(instance.ref_id)
            if md is not None:
                com_objects.extend(from_static(md.static, instance.text_args))

    for md_id, md in mods.defs.items():
        if md_id not in instantiated:
            com_objects.extend(from_static(md.static))
    return com_objects
