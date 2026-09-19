"""Tests for :func:`xknxmono.catalog.core.hardware.list_hardware` and :class:`HardwareFilters`.

These guard the cross-program filter contract: program-level filters
(``medium_type``, ``is_secure_enabled``, ``mask_version``, the ``registration_*``
fields, ``section_id``) are ANDed at the Hardware level - each can be satisfied
by a *different* ``HardwareProgram`` - rather than onto a single shared joined
program row. A multi-program device (e.g. a TP/IP coupler whose TP program is
non-secure and whose IP program is secure) must match a combination like
``medium_type=TP & is_secure_enabled=true`` even though no single program
satisfies both predicates.

The fixture mirrors that structure: ``H1`` is a two-program TP/IP coupler
(TP+non-secure+Registered via P1, IP+secure+Planned via P2), ``H2`` is a
single-program secure TP actuator (everything on P3), and ``H3`` is an RF
sensor whose program has no application program at all.
"""

from __future__ import annotations

import datetime
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from xknxmono.catalog.core.hardware import HardwareFilters, list_hardware
from xknxmono.catalog.db import make_engine
from xknxmono.catalog.models import (
    Application,
    CatalogSection,
    CatalogSectionProduct,
    Hardware,
    HardwareProgram,
    HardwareProgramMediumType,
    Manufacturer,
)

_MFR = "M-0001"


def _seed(url: str) -> Engine:
    """Build a catalog engine at ``url`` and seed it with H1, H2, and H3."""
    engine = make_engine(url)
    with Session(engine) as db:
        db.add(Manufacturer(id=_MFR, name="Acme"))
        db.flush()

        # H1: TP/IP coupler - program attributes split across P1 (TP) and P2 (IP).
        db.add(
            Hardware(
                id="H1",
                manufacturer_id=_MFR,
                name="TP/IP Secure Coupler",
                order_number="MDT-SCN",
                has_application_program=True,
                is_rail_mounted=True,
                is_coupler=True,
                is_ip_enabled=True,
            )
        )
        # H2: single-program secure TP actuator (all attributes on P3).
        db.add(
            Hardware(
                id="H2",
                manufacturer_id=_MFR,
                name="Secure TP Actuator",
                order_number="ACT-TP",
                has_application_program=True,
                is_rail_mounted=False,
                is_ip_enabled=False,
            )
        )
        # H3: RF sensor whose program has no linked application program.
        db.add(
            Hardware(
                id="H3",
                manufacturer_id=_MFR,
                name="RF Sensor",
                order_number="RF-SEN",
                has_application_program=False,
                is_ip_enabled=False,
            )
        )
        db.flush()

        db.add(
            Application(
                id="A1", name="App1", is_secure_enabled=False, mask_version="M0000"
            )
        )
        db.add(
            Application(
                id="A2", name="App2", is_secure_enabled=True, mask_version="M0700"
            )
        )
        db.add(
            Application(
                id="A3", name="App3", is_secure_enabled=True, mask_version="M0700"
            )
        )
        db.flush()

        db.add(
            HardwareProgram(
                id="P1",
                hardware_id="H1",
                application_id="A1",
                knxprod_path="p1.knxprod",
                registration_status="Registered",
                registration_number="R-0001",
                registration_date=datetime.date(2024, 1, 15),
            )
        )
        db.add(
            HardwareProgram(
                id="P2",
                hardware_id="H1",
                application_id="A2",
                knxprod_path="p2.knxprod",
                registration_status="Planned",
                registration_number="R-0002",
                registration_date=datetime.date(2024, 6, 20),
            )
        )
        db.add(
            HardwareProgram(
                id="P3",
                hardware_id="H2",
                application_id="A3",
                knxprod_path="p3.knxprod",
                registration_status="Registered",
                registration_number="R-0003",
                registration_date=datetime.date(2024, 3, 10),
            )
        )
        db.add(
            HardwareProgram(
                id="P4",
                hardware_id="H3",
                application_id=None,
                knxprod_path="p4.knxprod",
            )
        )
        db.flush()

        db.add(HardwareProgramMediumType(hardware_program_id="P1", medium_type="TP"))
        db.add(HardwareProgramMediumType(hardware_program_id="P2", medium_type="IP"))
        db.add(HardwareProgramMediumType(hardware_program_id="P3", medium_type="TP"))
        db.add(HardwareProgramMediumType(hardware_program_id="P4", medium_type="RF"))

        db.add(
            CatalogSection(
                id="CS-ROOT", manufacturer_id=_MFR, parent_id=None, name="Root"
            )
        )
        db.add(
            CatalogSection(
                id="CS-1", manufacturer_id=_MFR, parent_id="CS-ROOT", name="Sec1"
            )
        )
        db.add(
            CatalogSection(
                id="CS-2", manufacturer_id=_MFR, parent_id="CS-ROOT", name="Sec2"
            )
        )
        db.flush()
        db.add(
            CatalogSectionProduct(
                id="CSP1", section_id="CS-1", hardware_program_id="P2", name="Coupler"
            )
        )
        db.add(
            CatalogSectionProduct(
                id="CSP2", section_id="CS-2", hardware_program_id="P3", name="Actuator"
            )
        )
        db.commit()
    return engine


def _ids(filters: HardwareFilters | None = None) -> list[str]:
    """Run ``list_hardware`` against a fresh seeded in-memory engine and return hardware ids."""
    engine = _seed("sqlite:///:memory:")
    with Session(engine) as db:
        result = [hw.id for hw in list_hardware(db, filters)]
    engine.dispose()
    return result


# --- Baseline / no-regression -------------------------------------------------


def test_no_filters_returns_all_hardware() -> None:
    assert set(_ids()) == {"H1", "H2", "H3"}


def test_medium_type_single_matches_any_program() -> None:
    assert set(_ids(HardwareFilters(medium_type=["TP"]))) == {"H1", "H2"}
    assert set(_ids(HardwareFilters(medium_type=["IP"]))) == {"H1"}
    assert set(_ids(HardwareFilters(medium_type=["RF"]))) == {"H3"}


def test_is_secure_enabled_excludes_hardware_without_application() -> None:
    # A program with no linked application (H3/P4) must satisfy neither
    # is_secure_enabled branch; only H1 (non-secure P1) and H2 (secure P3) match.
    assert set(_ids(HardwareFilters(is_secure_enabled=False))) == {"H1"}
    assert set(_ids(HardwareFilters(is_secure_enabled=True))) == {"H1", "H2"}


def test_medium_type_does_not_duplicate_hardware_matching_multiple_programs() -> None:
    # H1 matches both TP (P1) and IP (P2); it must appear exactly once. Guards
    # against row multiplication now that the shared join + distinct() path is
    # gone.
    ids = _ids(HardwareFilters(medium_type=["TP", "IP"]))
    assert ids.count("H1") == 1
    assert set(ids) == {"H1", "H2"}


def test_section_id_includes_descendants() -> None:
    # CS-ROOT lists H1 (via P2 in CS-1) and H2 (via P3 in CS-2); both are
    # descendants, so the root must return both.
    assert set(_ids(HardwareFilters(section_id="CS-ROOT"))) == {"H1", "H2"}
    assert set(_ids(HardwareFilters(section_id="CS-1"))) == {"H1"}


# --- Cross-program AND (the contract the fix establishes) ---------------------
# Each program-level filter is a separate code block; one guard per block
# prevents a future refactor from reintroducing the single-shared-join collapse
# in any one of them. H1 splits every pair across P1 and P2, so a shared-join
# query would drop it.


def test_medium_type_and_is_secure_enabled_satisfied_by_different_programs() -> None:
    # H1: TP via P1 (non-secure), secure via P2 (IP); H2 satisfies both on P3.
    assert set(_ids(HardwareFilters(medium_type=["TP"], is_secure_enabled=True))) == {
        "H1",
        "H2",
    }


def test_medium_type_and_mask_version_satisfied_by_different_programs() -> None:
    # H1: TP via P1, mask M0700 via P2 (different programs); H2: both on P3.
    assert set(_ids(HardwareFilters(mask_version="M0700", medium_type=["TP"]))) == {
        "H1",
        "H2",
    }


def test_registration_status_and_medium_type_satisfied_by_different_programs() -> None:
    # H1: Registered via P1, IP via P2 (different programs).
    assert set(
        _ids(HardwareFilters(registration_status="Registered", medium_type=["IP"]))
    ) == {"H1"}


def test_registration_number_and_medium_type_satisfied_by_different_programs() -> None:
    # H1: R-0002 via P2 (IP), TP via P1 (different programs).
    assert set(
        _ids(HardwareFilters(registration_number="R-0002", medium_type=["TP"]))
    ) == {"H1"}


def test_registration_date_and_medium_type_satisfied_by_different_programs() -> None:
    # H1: reg_date 2024-01-15 via P1 (TP) satisfies an early `to` bound; IP via P2
    # (whose reg_date 2024-06-20 does NOT satisfy the bound) - different programs.
    assert set(
        _ids(
            HardwareFilters(
                registration_date_to=datetime.date(2024, 2, 1), medium_type=["IP"]
            )
        )
    ) == {"H1"}


def test_section_id_and_medium_type_satisfied_by_different_programs() -> None:
    # H1: listed in CS-1 via P2 (IP), supports TP via P1 (different programs).
    assert set(_ids(HardwareFilters(section_id="CS-1", medium_type=["TP"]))) == {"H1"}


# --- Eager loading is preserved ----------------------------------------------


def test_returned_hardware_has_programs_and_medium_types_loaded() -> None:
    engine = _seed("sqlite:///:memory:")
    with Session(engine) as db:
        hw = list_hardware(db, HardwareFilters(medium_type=["IP"]))[0]
        mediums = sorted(
            mt.medium_type for prog in hw.programs for mt in prog.medium_types
        )
        secure = any(
            prog.application is not None and prog.application.is_secure_enabled
            for prog in hw.programs
        )
    engine.dispose()
    assert hw.id == "H1"
    assert mediums == ["IP", "TP"]
    assert secure is True


# --- End-to-end through the FastAPI HTTP layer --------------------------------


def test_http_endpoint_combines_cross_program_filters(tmp_path: Path) -> None:
    """``GET /hardware?medium_type=TP&is_secure_enabled=true`` must return a
    multi-program device whose programs satisfy the two filters independently.

    Exercises the real ``Annotated[HardwareFilters, Query()]`` binding and the
    ``HardwareResponse`` serialization in addition to ``list_hardware`` - the
    HTTP layer is a pass-through, so this is the user-facing path the bug report
    is about. A minimal app with only the hardware router avoids the default
    service/lifespan side effects of the full application factory.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from xknxmono.catalog.core.service import CatalogService
    from xknxmono.catalog.http.deps import get_service
    from xknxmono.catalog.http.routers import hardware as hardware_router

    db_path = tmp_path / "http.db"
    seeder = _seed(f"sqlite:///{db_path}")
    seeder.dispose()
    service = CatalogService(db_path)

    app = FastAPI()
    app.include_router(hardware_router.router)
    app.dependency_overrides[get_service] = lambda: service
    try:
        with TestClient(app) as client:
            combined = client.get(
                "/hardware",
                params=[("medium_type", "TP"), ("is_secure_enabled", "true")],
            )
            only_medium = client.get("/hardware", params={"medium_type": "TP"})
            only_secure = client.get("/hardware", params={"is_secure_enabled": "true"})
    finally:
        app.dependency_overrides.clear()

    assert combined.status_code == 200
    assert {h["id"] for h in combined.json()} == {"H1", "H2"}
    # The single-filter responses include H1 too, confirming the combined
    # result is not empty due to some other regression.
    assert only_medium.status_code == 200
    assert "H1" in {h["id"] for h in only_medium.json()}
    assert only_secure.status_code == 200
    assert "H1" in {h["id"] for h in only_secure.json()}
