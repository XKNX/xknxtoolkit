"""Shared pytest fixtures for parser_v2 tests."""

from __future__ import annotations

import pytest

from xknxmono.models.intermediate import ApplicationProgram
from xknxmono.models.intermediate.application_program_static_t import (
    ApplicationProgramStatic,
)
from xknxmono.models.intermediate.application_program_type_t import (
    ApplicationProgramType,
)
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer


@pytest.fixture
def idx() -> ApplicationIndexer:
    """A minimal, empty ApplicationIndexer - for tests that need an EvalContext (idx
    is required) but don't exercise anything that actually reads from the indexer."""
    app = ApplicationProgram(
        id="APP",
        name="",
        application_number=1,
        application_version=1,
        program_type=ApplicationProgramType.APPLICATION_PROGRAM,
        mask_version="BV20",
        load_procedure_style=LoadProcedureStyle.DEFAULT_PROCEDURE,
        pei_type=0,
        default_language="en",
        dynamic_table_management=False,
        linkable=False,
        static=ApplicationProgramStatic(),
    )
    return ApplicationIndexer(app)
