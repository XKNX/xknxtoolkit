"""Unit test for hardware.py's module-level _hardware() generator that parse_hardware_xml
drives - a manufacturer without a Hardware section raises, and every manufacturer's
hardware is yielded when there are several."""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import ApplicationProgramRef, Hardware2Program
from xknxmono.models.intermediate.hardware_t import Hardware as IrHardware
from xknxmono.models.intermediate.knx import Knx
from xknxmono.models.intermediate.manufacturer_data_t import ManufacturerData
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer import (
    ManufacturerDataManufacturer,
)
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer_hardware import (
    ManufacturerDataManufacturerHardware,
)
from xknxmono.product.errors import ParseError
from xknxmono.product.hardware import (  # pyright: ignore[reportPrivateUsage]
    _application_ref_ids,
    _hardware,
)


def _hw(hw_id: str) -> IrHardware:
    return IrHardware(
        id=hw_id,
        name="",
        serial_number="",
        version_number=0,
        has_individual_address=False,
        has_application_program=False,
    )


def test_hardware_raises_when_no_manufacturer_data() -> None:
    knx = Knx(manufacturer_data=None)
    with pytest.raises(ParseError):
        list(_hardware(knx))


def test_hardware_raises_when_manufacturer_has_no_hardware_section() -> None:
    knx = Knx(
        manufacturer_data=ManufacturerData(
            manufacturer=[ManufacturerDataManufacturer(ref_id="M-0008")]
        )
    )
    with pytest.raises(ParseError, match="M-0008"):
        list(_hardware(knx))


def test_hardware_yields_across_multiple_manufacturers() -> None:
    hw1 = _hw("H1")
    hw2 = _hw("H2")
    knx = Knx(
        manufacturer_data=ManufacturerData(
            manufacturer=[
                ManufacturerDataManufacturer(
                    ref_id="M-0008",
                    hardware=ManufacturerDataManufacturerHardware(hardware=[hw1]),
                ),
                ManufacturerDataManufacturer(
                    ref_id="M-0009",
                    hardware=ManufacturerDataManufacturerHardware(hardware=[hw2]),
                ),
            ]
        )
    )
    assert list(_hardware(knx)) == [hw1, hw2]


def test_application_ref_ids_returns_ref_ids() -> None:
    h2p = Hardware2Program(
        id="H2P1",
        application_program_ref=[
            ApplicationProgramRef(ref_id="A1"),
            ApplicationProgramRef(ref_id="A2"),
        ],
    )
    assert _application_ref_ids(h2p) == ["A1", "A2"]


def test_application_ref_ids_raises_on_empty_ref_id() -> None:
    h2p = Hardware2Program(
        id="H2P1", application_program_ref=[ApplicationProgramRef(ref_id="")]
    )
    with pytest.raises(ParseError, match="H2P1"):
        _application_ref_ids(h2p)
