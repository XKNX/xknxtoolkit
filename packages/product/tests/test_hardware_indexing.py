"""Unit test for hardware.py's module-level _hardware() generator that parse_hardware_xml
drives - a manufacturer without a Hardware section is skipped, and every manufacturer's
hardware is yielded when there are several."""

from __future__ import annotations

from xknxmono.models.intermediate.hardware_t import Hardware as IrHardware
from xknxmono.models.intermediate.knx import Knx
from xknxmono.models.intermediate.manufacturer_data_t import ManufacturerData
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer import (
    ManufacturerDataManufacturer,
)
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer_hardware import (
    ManufacturerDataManufacturerHardware,
)
from xknxmono.product.hardware import _hardware  # pyright: ignore[reportPrivateUsage]


def _hw(hw_id: str) -> IrHardware:
    return IrHardware(
        id=hw_id,
        name="",
        serial_number="",
        version_number=0,
        has_individual_address=False,
        has_application_program=False,
    )


def test_hardware_empty_when_no_manufacturer_data() -> None:
    knx = Knx(manufacturer_data=None)
    assert list(_hardware(knx)) == []


def test_hardware_skips_manufacturer_without_hardware_section() -> None:
    knx = Knx(
        manufacturer_data=ManufacturerData(
            manufacturer=[ManufacturerDataManufacturer(ref_id="M-0008")]
        )
    )
    assert list(_hardware(knx)) == []


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
