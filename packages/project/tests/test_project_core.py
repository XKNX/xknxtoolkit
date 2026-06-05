from pathlib import Path

import pytest

from xknxmono.project import ProjectService

PRODUCT = "M-0001_H-x-1_P-1"


def _backbone_segment(svc: ProjectService, pid: str) -> int:
    """The default backbone segment (Area 0 / Line 0) the skeleton ships with."""
    return svc.topology(pid, 0).areas[0].lines[0].segments[0].id


def _new(
    tmp_path: Path, name: str = "p", project_id: str = "P-0001"
) -> tuple[ProjectService, str]:
    svc = ProjectService()
    pid = svc.create(tmp_path / f"{name}.xknxproj", project_id)
    return svc, pid


def test_skeleton_mirrors_ets(tmp_path: Path):
    svc, pid = _new(tmp_path)
    # one installation (index 0) with a backbone area on the IP medium, empty group addresses
    assert [i.index for i in svc.installations(pid)] == [0]
    topo = svc.topology(pid, 0)
    assert topo.areas[0].address == 0
    assert topo.areas[0].lines[0].address == 0
    assert topo.areas[0].lines[0].segments[0].medium_type == "MT-5"
    assert svc.group_addresses(pid) == []
    project = svc.project(pid)
    assert project.name == "New project"
    assert project.group_address_style == "ThreeLevel"


def test_topology_edits(tmp_path: Path):
    svc, pid = _new(tmp_path)
    area = svc.create_area(pid, 0, 1, "Area")
    svc.create_line(pid, area, 0, "Line")
    seg = svc.topology(pid, 0).areas[1].lines[0].segments[0].id
    dev = svc.add_device(pid, seg, PRODUCT, address=1, name="D")
    ga = svc.create_group_address(pid, 0, 1, "GA")
    # the user-created area is a sibling of the backbone area
    assert [a.address for a in svc.topology(pid, 0).areas] == [0, 1]
    assert [d.id for d in svc.devices(pid)] == [dev]
    assert [g.id for g in svc.group_addresses(pid)] == [ga]


def test_duplicate_individual_address_rejected(tmp_path: Path):
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=5, name="A")
    with pytest.raises(ValueError, match="already used"):
        svc.add_device(pid, seg, PRODUCT, address=5, name="B")


def test_three_level_group_addresses(tmp_path: Path):
    svc, pid = _new(tmp_path)
    g1 = svc.create_group_address(pid, 0, 1, "Switching")  # main 0 / middle 0
    g2 = svc.create_group_address(pid, 0, 2, "Status")  # same ranges -> reused
    g3 = svc.create_group_address(
        pid, 0, 256, "Other"
    )  # main 0 / middle 1 -> new middle
    assert [g.id for g in svc.group_addresses(pid)] == [g1, g2, g3]

    mains = [r for r in svc.topology(pid, 0).group_ranges if r.parent_id is None]
    assert len(mains) == 1
    assert mains[0].name == "New main group"
    middles = mains[0].children
    assert len(middles) == 2
    assert sorted(len(m.group_addresses) for m in middles) == [1, 2]

    # undoing the GA that created the second middle also removes that middle
    svc.undo(pid)
    main = next(r for r in svc.topology(pid, 0).group_ranges if r.parent_id is None)
    assert len(main.children) == 1


def test_add_undo_redo(tmp_path: Path):
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)

    dev = svc.add_device(pid, seg, PRODUCT, address=5, name="Switch")
    svc.set_parameter(pid, dev, "P-1", "42")
    assert [d.id for d in svc.devices(pid)] == [dev]

    assert svc.undo(pid)  # undo set_parameter
    assert svc.undo(pid)  # undo add_device
    assert svc.devices(pid) == []

    assert svc.redo(pid)  # redo add_device
    assert [d.id for d in svc.devices(pid)] == [dev]
    assert svc.redo(pid)  # redo set_parameter
    assert svc.redo(pid) is False


def test_set_parameter_undo_restores_old_value(tmp_path: Path):
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    dev = svc.add_device(pid, seg, PRODUCT, address=1, name="D")
    svc.set_parameter(pid, dev, "P-1", "1")
    svc.set_parameter(pid, dev, "P-1", "2")

    def value() -> str:
        return svc.devices(pid)[0].parameters[0].value

    assert value() == "2"
    svc.undo(pid)
    assert value() == "1"  # restored, not deleted
    svc.undo(pid)  # undo the create -> parameter row gone
    assert svc.devices(pid)[0].parameters == []


def test_link_com_object(tmp_path: Path):
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="D", com_object_refs=["O-1_R-1"])
    ga = svc.create_group_address(pid, 0, 1, "GA")
    co = svc.devices(pid)[0].com_objects[0]
    link = svc.link_com_object(pid, co.id, ga)
    assert [link_.group_address_id for link_ in co.links] == [ga]
    svc.undo(pid)
    assert co.links == []
    assert link is not None


def test_undo_truncates_redo(tmp_path: Path):
    svc, pid = _new(tmp_path)
    seg = _backbone_segment(svc, pid)
    svc.add_device(pid, seg, PRODUCT, address=1, name="A")
    svc.undo(pid)
    d2 = svc.add_device(pid, seg, PRODUCT, address=2, name="B")
    assert not svc.redo(pid)
    assert [d.id for d in svc.devices(pid)] == [d2]


def test_save_and_reopen(tmp_path: Path):
    path = tmp_path / "project.xknxproj"
    svc = ProjectService()
    pid = svc.create(path, "P-0001")
    seg = _backbone_segment(svc, pid)
    dev = svc.add_device(pid, seg, PRODUCT, address=5, name="Switch")
    svc.set_parameter(pid, dev, "P-1", "7")
    svc.create_group_address(pid, 0, 1, "GA")
    svc.close(pid)

    reopened = ProjectService()
    pid2 = reopened.open(path)
    assert pid2 == pid
    # live state is read straight from the tables (no replay)
    assert [d.name for d in reopened.devices(pid2)] == ["Switch"]
    assert [g.name for g in reopened.group_addresses(pid2)] == ["GA"]
    # the events history still drives undo across the reopen
    assert reopened.undo(pid2)  # undo create_group_address
    assert reopened.group_addresses(pid2) == []


def test_multiple_installations(tmp_path: Path):
    svc, pid = _new(tmp_path)
    assert [i.index for i in svc.installations(pid)] == [0]

    inst1 = svc.add_installation(pid, "Installation 1")
    assert inst1 == 1
    assert [i.index for i in svc.installations(pid)] == [0, 1]
    assert [a.address for a in svc.topology(pid, 1).areas] == [0]  # its own backbone

    svc.create_area(pid, 0, 1, "A in 0")
    svc.create_area(pid, 1, 7, "A in 1")
    assert [a.address for a in svc.topology(pid, 0).areas] == [0, 1]
    assert [a.address for a in svc.topology(pid, 1).areas] == [0, 7]

    svc.create_group_address(pid, 0, 1, "GA in 0")
    svc.create_group_address(pid, 1, 2, "GA in 1")
    assert {g.name for g in svc.group_addresses(pid)} == {"GA in 0", "GA in 1"}

    while svc.undo(pid):
        pass
    assert [i.index for i in svc.installations(pid)] == [0]


def test_multiple_concurrent_projects(tmp_path: Path):
    svc = ProjectService()
    a = svc.create(tmp_path / "a.xknxproj", "P-000A")
    b = svc.create(tmp_path / "b.xknxproj", "P-000B")
    dev = svc.add_device(
        svc.list()[0], _backbone_segment(svc, a), PRODUCT, address=1, name="A"
    )
    assert [d.id for d in svc.devices(a)] == [dev]
    assert svc.devices(b) == []  # isolated
    assert set(svc.list()) == {a, b}
