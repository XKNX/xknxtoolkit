"""Convert per-version `files.vXX` model instances into the unified `intermediate` model.

The engine is a reflective field-copy: for each target field it copies the same-named source
field, recursing into nested dataclasses and lists. xsdata names fields identically across
versions, so this handles the bulk automatically. Genuine divergences — captured from analysing
the schemas — are handled by per-type override functions registered in OVERRIDES, plus a
universal rule that synthesises a PUID where the unified model requires one but the source
version predates it.

Nothing here changes the intermediate model; every version-specific quirk lives in an override.
"""

from __future__ import annotations

import dataclasses
import types
import typing
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Callable, get_args, get_origin


class ConversionError(Exception):
    """Raised when a source value cannot be honestly mapped into the unified model."""


@dataclass(slots=True)
class PuidAllocator:
    """Hands out synthetic PUIDs for pre-v12 projects, which have no PUID of their own.

    Values are sequential per conversion. They are fabricated — a v10/v11 file carries no real
    PUIDs, so within one converted project every PUID here is synthetic and internally unique.
    """

    _next: int = 1

    def allocate(self) -> int:
        value = self._next
        self._next += 1
        return value


@dataclass(slots=True)
class Context:
    version: str
    puid: PuidAllocator = field(default_factory=PuidAllocator)


# type key (Meta.name, else class name) -> override producing {field_name: value}. Overrides run
# BEFORE the generic copy and OWN the fields they return (the generic pass skips those fields).
OverrideFn = Callable[[Any, Context], dict[str, Any]]
OVERRIDES: dict[str, OverrideFn] = {}


def override(type_key: str) -> Callable[[OverrideFn], OverrideFn]:
    def register(fn: OverrideFn) -> OverrideFn:
        OVERRIDES[type_key] = fn
        return fn
    return register


def type_key(cls: type) -> str:
    meta = getattr(cls, "Meta", None)
    return (getattr(meta, "name", None) if meta else None) or cls.__name__


# Field renames between the version models and the unified model: target_type_key ->
# {target_field: source_field}. The generic copy consults this when a same-named source field is
# absent, then converts the value with the correct target type — so renames of both scalars and
# nested dataclasses are handled uniformly. (Old versions used capital-'In' casing: AddInData,
# AddInId; the unified model uses the v12+ lowercase forms.)
ALIASES: dict[str, dict[str, str]] = {
    "Project_t": {"addin_data": "add_in_data"},
    "ProjectAddinData": {"addin_data": "add_in_data"},
    "AddinData_t": {"addin_id": "add_in_id"},
    # v13→v14 renames (old versions used the left-hand source names):
    "ProjectInstallationsInstallation": {"locations": "buildings"},  # Buildings → Locations
    "Locations_t": {"space": "building_part"},                       # BuildingPart → Space
    "Space_t": {"space": "building_part"},                           # recursive Space child
}


# --- type-hint resolution -------------------------------------------------

_hints_cache: dict[type, dict[str, Any]] = {}


def _hints(cls: type) -> dict[str, Any]:
    if cls not in _hints_cache:
        _hints_cache[cls] = typing.get_type_hints(cls)
    return _hints_cache[cls]


def _unwrap(hint: Any) -> tuple[bool, Any]:
    """Return (is_list, base_type) with Optional/Union[..., None] stripped."""
    def strip_optional(h: Any) -> Any:
        if get_origin(h) in (typing.Union, types.UnionType):
            args = [a for a in get_args(h) if a is not type(None)]
            if len(args) == 1:
                return args[0]
        return h

    hint = strip_optional(hint)
    if get_origin(hint) is list:
        (arg,) = get_args(hint)
        return True, strip_optional(arg)
    return False, hint


# --- core converter -------------------------------------------------------

def convert(src: Any, target_cls: type, ctx: Context) -> Any:
    """Build a `target_cls` instance from `src`: overrides first, then copy same-named fields."""
    hints = _hints(target_cls)
    key = type_key(target_cls)
    ov = OVERRIDES.get(key)
    kwargs: dict[str, Any] = dict(ov(src, ctx)) if ov is not None else {}
    aliases = ALIASES.get(key, {})

    for f in fields(target_cls):
        if f.name in kwargs:          # owned by an override
            continue
        src_name = f.name if hasattr(src, f.name) else aliases.get(f.name)
        if src_name is None or not hasattr(src, src_name):  # target-only; default / puid rule
            continue
        src_val = getattr(src, src_name)
        if src_val is None:
            continue
        is_list, base = _unwrap(hints.get(f.name, f.type))
        if is_dataclass(base):
            kwargs[f.name] = (
                [convert(v, base, ctx) for v in src_val] if is_list else convert(src_val, base, ctx)
            )
        else:
            kwargs[f.name] = src_val

    # Universal: synthesise a PUID where the unified model requires one but the source lacked it.
    if any(f.name == "puid" for f in fields(target_cls)) and kwargs.get("puid") is None:
        kwargs["puid"] = ctx.puid.allocate()

    return target_cls(**kwargs)


# --- captured overrides (one per real divergence found while analysing the schemas) ---

@override("GroupAddress_t")
def _group_address(src: Any, ctx: Context) -> dict[str, Any]:
    """v10–v12 stored DatapointType as a list (IDREFS); the unified model is a single ref.
    Accept 0/1 entries; reject genuine multi-DPT records rather than silently dropping data."""
    dpt = getattr(src, "datapoint_type", None)
    if isinstance(dpt, list):
        if len(dpt) > 1:
            raise ConversionError(
                f"GroupAddress {getattr(src, 'id', '?')}: {len(dpt)} DatapointType refs {dpt}; "
                "unified model allows one"
            )
        return {"datapoint_type": dpt[0] if dpt else None}
    return {}


@override("DeviceInstanceAdditionalAddresses")
def _additional_addresses(src: Any, ctx: Context) -> dict[str, Any]:
    """v10/v11 stored each additional address as element text (list[int]); v12+ wrap it in an
    <Address> element with an 'Address' attribute. Wrap the raw ints into the unified objects."""
    from xknxmono.models.intermediate.device_instance_t_additional_addresses_address import (
        DeviceInstanceAdditionalAddressesAddress as Addr,
    )
    vals = getattr(src, "address", None) or []
    if vals and all(isinstance(v, int) for v in vals):
        return {"address": [Addr(address=v) for v in vals]}
    return {}  # already in object form (v12+) — let the generic pass handle it


@override("DeviceInstanceBinaryDataBinaryData")
def _binary_data(src: Any, ctx: Context) -> dict[str, Any]:
    """v20 had AutoCopy (default false); v21+ renamed it to DoNotCopy with inverted polarity.
    Map the old flag across: DoNotCopy = not AutoCopy."""
    if hasattr(src, "auto_copy"):
        return {"do_not_copy": not bool(getattr(src, "auto_copy"))}
    return {}


def fake_hash(value: Any) -> bytes:
    """Placeholder for the KNX loaded-credential hashing algorithm, which we haven't identified.
    Raises so conversions that would need it fail loudly rather than fabricate a wrong hash."""
    raise NotImplementedError(
        f"loaded-credential hashing algorithm unknown; cannot hash {value!r}"
    )


@override("ParameterSeparator_t")
def _parameter_separator(src: Any, ctx: Context) -> dict[str, Any]:
    """≤v13 had a boolean HorizontalRuler; v14+ replaced it with the richer UIHint enum (which has
    a 'HorizontalRuler' value). Map a set ruler flag onto the enum."""
    if getattr(src, "horizontal_ruler", None) and getattr(src, "uihint", None) is None:
        from xknxmono.models.intermediate.parameter_separator_t_uihint import ParameterSeparatorUihint
        return {"uihint": ParameterSeparatorUihint.HORIZONTAL_RULER}
    return {}


@override("Security_t")
def _security(src: Any, ctx: Context) -> dict[str, Any]:
    """v14 replaced the plaintext Loaded* credentials with hashed forms. We keep both in the IR;
    when only the plaintext is present (≤v13), derive the hash. The algorithm is unknown, so this
    raises until it's identified rather than storing a bogus hash. The plaintext itself is kept
    (copied by the generic pass)."""
    out: dict[str, Any] = {}
    for plain, hashed in (
        ("loaded_device_authentication_code", "loaded_device_authentication_code_hash"),
        ("loaded_device_management_password", "loaded_device_management_password_hash"),
    ):
        pv = getattr(src, plain, None)
        if pv is not None and getattr(src, hashed, None) is None:
            out[hashed] = fake_hash(pv)
    return out


@override("TopologyAreaLine")
def _line(src: Any, ctx: Context) -> dict[str, Any]:
    """v21 introduced a Segment layer: devices + medium attrs moved from the flat line onto a
    Segment child. For pre-v21 flat lines, wrap that content into a single synthesized Segment so
    it lands at the modern location. (Line-level attrs stay on the line via the generic copy.)"""
    if getattr(src, "segment", None):
        return {}  # v21+ already segmented — generic copy handles it
    from xknxmono.models.intermediate.topology_t_area_line_segment import TopologyAreaLineSegment as Seg

    hints = _hints(Seg)
    seg_kwargs: dict[str, Any] = {}
    for fname in ("device_instance", "bus_access", "additional_group_addresses",
                  "medium_type_ref_id", "domain_address"):
        val = getattr(src, fname, None)
        if val is None or val == []:
            continue
        is_list, base = _unwrap(hints[fname])
        if is_dataclass(base):
            seg_kwargs[fname] = [convert(v, base, ctx) for v in val] if is_list else convert(val, base, ctx)
        else:
            seg_kwargs[fname] = val
    # Synthesize the segment's own identity (distinct from the line's Id)
    seg_kwargs["id"] = f"{getattr(src, 'id', 'L')}-S1"
    seg_kwargs["number"] = 1
    seg_kwargs["puid"] = ctx.puid.allocate()
    return {"segment": [Seg(**seg_kwargs)]}


@override("ProjectInstallationsInstallation")
def _installation(src: Any, ctx: Context) -> dict[str, Any]:
    """MulticastTTL moved from per-Line (v10/v11: Topology>Area>Line) to per-Installation (v14+).
    When the source lacks the installation-level value, lift it from the first line that has one."""
    if getattr(src, "multicast_ttl", None) is not None:
        return {}  # already at installation level (v14+) — generic copy handles it
    topo = getattr(src, "topology", None)
    for area in (getattr(topo, "area", None) or []):
        for line in (getattr(area, "line", None) or []):
            ttl = getattr(line, "multicast_ttl", None)
            if ttl is not None:
                return {"multicast_ttl": ttl}
    return {}
