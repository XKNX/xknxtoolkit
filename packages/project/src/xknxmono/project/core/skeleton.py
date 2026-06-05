"""Seed a new project's baseline state, mirroring what ETS6 creates for a fresh project.

The baseline is *not* undoable, so it's inserted directly (no event): a ``Project`` row
(``ThreeLevel`` group-address style) and installation 0 with a default *backbone* topology
(Area 0 / Line 0 / Segment on the IP medium) and an empty group-address tree.
"""

from sqlalchemy.orm import Session

from xknxmono.project.models import Area, Installation, Line, Project, Segment

MEDIUM_IP = "MT-5"
MEDIUM_TP = "MT-0"

DEFAULT_INSTALLATION = 0


def three_level_ranges(address: int) -> tuple[int, int, int, int]:
    """ETS ThreeLevel main/middle group ranges for a group address.

    Returns ``(main_start, main_end, middle_start, middle_end)``; address 0 is reserved, so the
    first range starts at 1 (matching ETS's ``RangeStart="1"``)."""
    main = address // 2048
    middle = (address % 2048) // 256
    main_base = main * 2048
    middle_base = main_base + middle * 256
    return max(1, main_base), main_base + 2047, max(1, middle_base), middle_base + 255


def seed_new_project(session: Session, project_id: str, name: str) -> None:
    """Insert the baseline project + installation 0 with its backbone (Area 0 / Line 0 / IP Segment)."""
    session.add(Project(id=project_id, name=name, group_address_style="ThreeLevel"))
    installation = Installation(index=DEFAULT_INSTALLATION, name="")
    installation.areas.append(
        Area(
            address=0,
            lines=[
                Line(
                    address=0,
                    segments=[Segment(number=0, medium_type=MEDIUM_IP)],
                )
            ],
        )
    )
    session.add(installation)
    session.commit()
