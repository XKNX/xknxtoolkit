"""Unit tests for Application's resolution-facade properties and the module-level
_programs() generator that parse_application_xml drives."""

from __future__ import annotations

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_static_t_code import (
    ApplicationProgramStaticCode,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.knx import Knx
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.load_procedures_t import LoadProcedures
from xknxmono.models.intermediate.manufacturer_data_t import ManufacturerData
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer import (
    ManufacturerDataManufacturer,
)
from xknxmono.models.intermediate.manufacturer_data_t_manufacturer_application_programs import (
    ManufacturerDataManufacturerApplicationPrograms,
)
from xknxmono.product.application import (  # pyright: ignore[reportPrivateUsage]
    Application,
    _programs,
)


def _program(prog_id: str = "APP1") -> ApplicationProgram:
    return ApplicationProgram(
        id=prog_id,
        name="My App",
        application_number=1,
        application_version=1,
        program_type=ApplicationProgramType.APPLICATION_PROGRAM,
        mask_version="BV20",
        load_procedure_style=LoadProcedureStyle.DEFAULT_PROCEDURE,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=ApplicationProgramStatic(
            code=ApplicationProgramStaticCode(),
            load_procedures=LoadProcedures(),
        ),
    )


def test_id_property() -> None:
    app = Application(program=_program(), version="20", manufacturer_id="M-0008")
    assert app.id == "APP1"


def test_name_property_uses_program_name() -> None:
    app = Application(program=_program(), version="20", manufacturer_id="M-0008")
    assert app.name == "My App"


def test_code_property() -> None:
    program = _program()
    app = Application(program=program, version="20", manufacturer_id="M-0008")
    assert app.code is program.static.code


def test_load_procedures_property() -> None:
    program = _program()
    app = Application(program=program, version="20", manufacturer_id="M-0008")
    assert app.load_procedures is program.static.load_procedures


def test_load_procedure_style_property() -> None:
    app = Application(program=_program(), version="20", manufacturer_id="M-0008")
    assert app.load_procedure_style == LoadProcedureStyle.DEFAULT_PROCEDURE


def test_dynamic_ui_none_when_no_dynamic_section() -> None:
    app = Application(program=_program(), version="20", manufacturer_id="M-0008")
    assert app.dynamic_ui() is None


def test_programs_skips_manufacturer_without_application_programs() -> None:
    knx = Knx(
        manufacturer_data=ManufacturerData(
            manufacturer=[ManufacturerDataManufacturer(ref_id="M-0008")]
        )
    )
    assert list(_programs(knx)) == []


def test_programs_yields_across_multiple_manufacturers() -> None:
    p1 = _program("APP1")
    p2 = _program("APP2")
    knx = Knx(
        manufacturer_data=ManufacturerData(
            manufacturer=[
                ManufacturerDataManufacturer(
                    ref_id="M-0008",
                    application_programs=ManufacturerDataManufacturerApplicationPrograms(
                        application_program=[p1]
                    ),
                ),
                ManufacturerDataManufacturer(
                    ref_id="M-0009",
                    application_programs=ManufacturerDataManufacturerApplicationPrograms(
                        application_program=[p2]
                    ),
                ),
            ]
        )
    )
    assert list(_programs(knx)) == [p1, p2]


def test_programs_empty_when_no_manufacturer_data() -> None:
    knx = Knx(manufacturer_data=None)
    assert list(_programs(knx)) == []
