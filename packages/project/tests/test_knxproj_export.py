"""Round-trip test for the simple .knxproj export: build a project via the core API, export it to
a ``.knxproj``, then re-import it (real xknxproject parse) and check topology/GAs/links survive."""

import zipfile
from pathlib import Path

from sqlalchemy.orm import Session

from xknxmono.project import ProjectService, export_knxproj, import_knxproj
from xknxmono.project.db import make_engine, url_for
from xknxmono.project.models import (
    Device,
    Function,
    FunctionGroupAddress,
    Installation,
    Space,
)


def test_export_import_round_trip(tmp_path: Path) -> None:
    src = tmp_path / "src.xknx"
    svc = ProjectService()
    pid = svc.create(src, "P-RT")

    area_id = svc.create_area(pid, 0, 1, "Area 1")
    line_id = svc.create_line(pid, area_id, 1, "Line 1")
    segment_id = next(
        line.segments[0].id
        for area in svc.topology(pid, 0).areas
        if area.id == area_id
        for line in area.lines
        if line.id == line_id
    )
    device_id = svc.add_device(
        pid,
        segment_id,
        "M-1_H-1_P-1",
        address=5,
        name="Dev",
        hardware2program_ref_id="M-1_H-1_HP-1",
        com_objects=[("M-1_A-1_O-1_R-1", None)],
    )
    ga_id = svc.create_group_address(pid, 0, 0x0801, "GA One")  # 1/0/1
    svc.set_group_address_datapoint_type(pid, ga_id, "DPST-1-1")
    co_id = next(
        co.id for d in svc.devices(pid) if d.id == device_id for co in d.com_objects
    )
    svc.link_com_object(pid, co_id, ga_id, sending=True)
    svc.close(pid)

    # The core API has no space/function commands yet; seed a location tree via ORM so the
    # export's Locations round-trip is covered too.
    engine = make_engine(url_for(src))
    with Session(engine) as session:
        inst = session.query(Installation).one()
        room = Space(
            installation_id=inst.id,
            parent_id=None,
            space_type="Room",
            name="Room 1",
            number="1",
            order=0,
        )
        session.add(room)
        session.flush()
        device = session.query(Device).filter(Device.id == device_id).one()
        device.space_id = room.id
        fn = Function(space_id=room.id, function_type="FT-1", name="Light", order=0)
        session.add(fn)
        session.flush()
        session.add(
            FunctionGroupAddress(function_id=fn.id, group_address_id=ga_id, role="role")
        )
        session.commit()
    engine.dispose()

    out = tmp_path / "out.knxproj"
    export_knxproj(src, out)
    assert out.exists() and out.stat().st_size > 0

    round_path = tmp_path / "round.xknx"
    rpid = import_knxproj(out, round_path)
    rsvc = ProjectService()
    rsvc.open(round_path)

    inst = rsvc.topology(rpid, 0)
    addresses = {a.address for a in inst.areas}
    assert 1 in addresses  # our Area 1 survived (Area 0 backbone also present)
    gas = {g.text: g for g in rsvc.group_addresses(rpid)}
    assert "1/0/1" in gas
    assert gas["1/0/1"].name == "GA One"
    assert gas["1/0/1"].datapoint_type == "DPST-1-1"
    # the device and its sending link survived
    devices = rsvc.devices(rpid)
    assert any(d.product_ref_id == "M-1_H-1_P-1" for d in devices)
    links = rsvc.group_address_links(rpid, gas["1/0/1"].id)
    assert len(links) == 1
    assert links[0].is_sending

    # the location tree (space + its device + function) survived
    with Session(make_engine(url_for(round_path))) as session:
        rooms = session.query(Space).filter(Space.name == "Room 1").all()
        assert len(rooms) == 1
        assert session.query(Device).filter(Device.space_id == rooms[0].id).count() == 1
        funcs = session.query(Function).filter(Function.space_id == rooms[0].id).all()
        assert len(funcs) == 1
        assert funcs[0].name == "Light"
        assert (
            session.query(FunctionGroupAddress)
            .filter(FunctionGroupAddress.function_id == funcs[0].id)
            .count()
            == 1
        )


def test_export_bundles_extra_files_and_master(tmp_path: Path) -> None:
    src = tmp_path / "src.xknx"
    svc = ProjectService()
    pid = svc.create(src, "P-MFR")
    svc.close(pid)

    out = tmp_path / "out.knxproj"
    master = b'<?xml version="1.0"?>\n<KNX><MasterData Merged="1"/></KNX>'
    hardware = b"<Hardware/>"
    export_knxproj(
        src,
        out,
        extra_files={
            "M-9999/Hardware.xml": hardware,
            "M-9999.signature": b"sig",
            # colliding with an own path must be ignored, not overwrite our master
            "knx_master.xml": b"IGNORED",
        },
        master_xml=master,
    )

    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        assert "M-9999/Hardware.xml" in names
        assert "M-9999.signature" in names
        assert zf.read("M-9999/Hardware.xml") == hardware
        # the colliding "knx_master.xml" key is ignored: only our master, written once
        assert names.count("knx_master.xml") == 1
        assert zf.read("knx_master.xml") == master
