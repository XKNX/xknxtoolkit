"""Export a project SQLite document to a simple ETS ``.knxproj`` archive.

This is a *simple* export: it writes the project structure (topology, devices with their
com-object → group-address links, the group-address tree, and the locations tree of spaces with
their device/function assignments) plus project metadata, in the ETS project XML shape
(schema ``project/20``) so it round-trips back through :func:`import_knxproj`.

Manufacturer/application data (Hardware/Catalog/application program XMLs) is **not** read from a
catalog here — this package is catalog-free. Callers that have the catalog can pass those raw
archive members via ``extra_files`` (and a merged ``knx_master.xml`` via ``master_xml``) so the
resulting archive is self-contained and applications resolve. The **project-level**
``{pid}.signature`` is generated with a valid signature (see :mod:`knxproj_signing`);
manufacturer ``M-XXXX.signature`` files, when needed, come from the catalog via ``extra_files``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Mapping
from pathlib import Path

from sqlalchemy.orm import Session

from xknxmono.project.core.knxproj_signing import directory_signature
from xknxmono.project.db import make_engine, url_for
from xknxmono.project.models import (
    Device,
    GroupRange,
    Installation,
    Project,
    Space,
)

_NS = "http://knx.org/xml/project/20"
_SCHEMA = "20"


def export_knxproj(
    source: Path | str,
    dest: Path | str,
    *,
    extra_files: Mapping[str, bytes] | None = None,
    master_xml: bytes | None = None,
) -> None:
    """Read the project at ``source`` (a ``.xknx``) and write a ``.knxproj`` archive to ``dest``.

    Args:
      source: Path to the ``.xknx`` project document.
      dest: Path to write the ``.knxproj`` archive to.
      extra_files: Optional raw archive members to add verbatim (e.g. manufacturer ``M-XXXX/``
        trees and their ``M-XXXX.signature`` files, supplied by a caller that has the catalog).
        Keys colliding with the export's own paths are ignored.
      master_xml: Optional ``knx_master.xml`` bytes to write instead of the minimal generated one.
    """
    engine = make_engine(url_for(Path(source)))
    try:
        with Session(engine) as session:
            project = session.query(Project).first()
            if project is None:
                raise ValueError(f"{source} is not a project (no project row)")
            installation = (
                session.query(Installation).order_by(Installation.index).first()
            )
            _write_archive(Path(dest), project, installation, extra_files, master_xml)
    finally:
        engine.dispose()


def _el(parent: ET.Element, tag: str, **attrs: object) -> ET.Element:
    child = ET.SubElement(parent, f"{{{_NS}}}{tag}")
    for key, value in attrs.items():
        if value is not None:
            child.set(key, str(value))
    return child


def _root() -> ET.Element:
    return ET.Element(f"{{{_NS}}}KNX")


def _write_archive(
    dest: Path,
    project: Project,
    installation: Installation | None,
    extra_files: Mapping[str, bytes] | None,
    master_xml: bytes | None,
) -> None:
    pid = project.id
    ga_link_id, di_id = _assign_ids(pid, installation)

    if master_xml is None:
        master = _root()
        _el(master, "MasterData", Version="1", Signature="")
        master_xml = _serialize(master)

    proj_xml = _root()
    p = _el(proj_xml, "Project", Id=pid)
    _el(
        p,
        "ProjectInformation",
        Name=project.name,
        GroupAddressStyle=project.group_address_style,
        Guid=project.guid or None,
        LastModified=project.last_modified or None,
    )

    zero_xml = _build_project_xml(pid, project, installation, ga_link_id, di_id)

    own_paths = {
        "knx_master.xml",
        f"{pid}.signature",
        f"{pid}/project.xml",
        f"{pid}/0.xml",
    }
    project_xml = _serialize(proj_xml)
    zero = _serialize(zero_xml)
    # Sign the project folder so a strict import accepts it (see knxproj_signing).
    # The reference tooling writes the .signature file as UTF-8 with a BOM.
    project_signature = b"\xef\xbb\xbf" + directory_signature(
        {"project.xml": project_xml, "0.xml": zero}
    )
    dest.unlink(missing_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("knx_master.xml", master_xml)
        zf.writestr(f"{pid}.signature", project_signature)
        zf.writestr(f"{pid}/project.xml", project_xml)
        zf.writestr(f"{pid}/0.xml", zero)
        for path, data in (extra_files or {}).items():
            if path not in own_paths:
                zf.writestr(path, data)


def _assign_ids(
    pid: str, installation: Installation | None
) -> tuple[dict[int, str], dict[int, str]]:
    """Assign the stable element ids ETS uses: GA link tokens (``GA-n``) and device ids."""
    ga_link_id: dict[int, str] = {}
    di_id: dict[int, str] = {}
    if installation is None:
        return ga_link_id, di_id
    ga_seq = 0
    for group_range in installation.group_ranges:
        for ga in group_range.group_addresses:
            ga_seq += 1
            ga_link_id[ga.id] = f"GA-{ga_seq}"
    di_seq = 0
    for area in installation.areas:
        for line in area.lines:
            for segment in line.segments:
                for device in segment.devices:
                    di_seq += 1
                    di_id[device.id] = f"{pid}-0_DI-{di_seq}"
    return ga_link_id, di_id


def _build_project_xml(
    pid: str,
    project: Project,
    installation: Installation | None,
    ga_link_id: dict[int, str],
    di_id: dict[int, str],
) -> ET.Element:
    root = _root()
    p = _el(root, "Project", Id=pid)
    insts = _el(p, "Installations")
    if installation is None:
        return root
    inst = _el(insts, "Installation", Name=installation.name)

    topo = _el(inst, "Topology")
    l_seq = 0
    for a_seq, area in enumerate(
        sorted(installation.areas, key=lambda x: x.address), start=1
    ):
        area_el = _el(
            topo,
            "Area",
            Id=f"{pid}-0_A-{a_seq}",
            Address=area.address,
            Name=area.name,
        )
        for line in sorted(area.lines, key=lambda x: x.address):
            l_seq += 1
            medium = line.segments[0].medium_type if line.segments else "MT-0"
            line_el = _el(
                area_el,
                "Line",
                Id=f"{pid}-0_L-{l_seq}",
                Address=line.address,
                Name=line.name,
                MediumTypeRefId=medium,
            )
            for segment in line.segments:
                for device in segment.devices:
                    _build_device(line_el, device, di_id[device.id], ga_link_id)

    _build_locations(inst, installation, pid, di_id, ga_link_id)

    gas = _el(inst, "GroupAddresses")
    ranges = _el(gas, "GroupRanges")
    gr_seq = 0
    roots = [gr for gr in installation.group_ranges if gr.parent_id is None]
    for group_range in sorted(roots, key=lambda x: x.range_start):
        gr_seq = _build_range(ranges, group_range, pid, gr_seq, ga_link_id)
    return root


def _build_locations(
    inst_el: ET.Element,
    installation: Installation,
    pid: str,
    di_id: dict[int, str],
    ga_link_id: dict[int, str],
) -> None:
    roots = [s for s in installation.spaces if s.parent_id is None]
    if not roots:
        return
    locs = _el(inst_el, "Locations")
    counters = {"sp": 0, "f": 0, "gar": 0}
    for space in sorted(roots, key=lambda s: (s.order, s.id)):
        _build_space(locs, space, pid, di_id, ga_link_id, counters)


def _build_space(
    parent: ET.Element,
    space: Space,
    pid: str,
    di_id: dict[int, str],
    ga_link_id: dict[int, str],
    counters: dict[str, int],
) -> None:
    counters["sp"] += 1
    sp = _el(
        parent,
        "Space",
        Type=space.space_type or "Room",
        Id=f"{pid}-0_BP-{counters['sp']}",
        Name=space.name,
        Number=space.number or None,
    )
    for device in space.devices:
        if device.id in di_id:
            _el(sp, "DeviceInstanceRef", RefId=di_id[device.id])
    for fn in sorted(space.functions, key=lambda f: (f.order, f.id)):
        counters["f"] += 1
        fn_el = _el(
            sp,
            "Function",
            Id=f"{pid}-0_F-{counters['f']}",
            Name=fn.name,
            Type=fn.function_type or None,
        )
        for fga in fn.group_addresses:
            if fga.group_address_id not in ga_link_id:
                continue
            counters["gar"] += 1
            _el(
                fn_el,
                "GroupAddressRef",
                Id=f"{pid}-0_GAR-{counters['gar']}",
                RefId=f"{pid}-0_{ga_link_id[fga.group_address_id]}",
                Role=fga.role or None,
            )
    for child in sorted(space.children, key=lambda s: (s.order, s.id)):
        _build_space(sp, child, pid, di_id, ga_link_id, counters)


def _build_device(
    line_el: ET.Element,
    device: Device,
    device_id: str,
    ga_link_id: dict[int, str],
) -> None:
    di = _el(
        line_el,
        "DeviceInstance",
        Id=device_id,
        Address=device.address,
        Name=device.name,
        ProductRefId=device.product_ref_id,
        Hardware2ProgramRefId=device.hardware2program_ref_id,
    )
    refs = _el(di, "ComObjectInstanceRefs")
    for co in device.com_objects:
        # ETS orders the sending link first; our ComObjectLink.is_sending marks it.
        ordered = sorted(co.links, key=lambda link: not link.is_sending)
        links = " ".join(
            ga_link_id[link.group_address_id]
            for link in ordered
            if link.group_address_id in ga_link_id
        )
        if not links:
            continue  # xknxproject only keeps linked com-object instance refs
        _el(refs, "ComObjectInstanceRef", RefId=co.ref_id, Links=links)


def _build_range(
    parent: ET.Element,
    group_range: GroupRange,
    pid: str,
    seq: int,
    ga_link_id: dict[int, str],
) -> int:
    seq += 1
    gr_el = _el(
        parent,
        "GroupRange",
        Id=f"{pid}-0_GR-{seq}",
        RangeStart=group_range.range_start,
        RangeEnd=group_range.range_end,
        Name=group_range.name,
    )
    for ga in sorted(group_range.group_addresses, key=lambda x: x.address):
        _el(
            gr_el,
            "GroupAddress",
            Id=f"{pid}-0_{ga_link_id[ga.id]}",
            Address=ga.address,
            Name=ga.name,
            DatapointType=ga.datapoint_type,
        )
    for child in sorted(group_range.children, key=lambda x: x.range_start):
        seq = _build_range(gr_el, child, pid, seq, ga_link_id)
    return seq


def _serialize(root: ET.Element) -> bytes:
    ET.register_namespace("", _NS)
    return b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(
        root, encoding="unicode"
    ).encode("utf-8")
