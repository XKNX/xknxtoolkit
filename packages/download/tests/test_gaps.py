"""Tests for the implementation-gap registry and its diagnostic messages."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest

from xknxmono.download import gaps
from xknxmono.download.errors import UnsupportedProcedureError
from xknxmono.download.image import DownloadImage
from xknxmono.download.procedure import LoadProcedureRunner
from xknxmono.download.programmer import DeviceProgrammer

from .conftest import FakeDevice

if True:  # keep import used for typing without a runtime dependency cycle
    from xknxmono.product import Application


def test_known_gap_message_names_standard_service() -> None:
    message = gaps.describe_missing("LdCtrlClearLCFilterTable")
    assert "LdCtrlClearLCFilterTable" in message
    assert "line coupler filter table" in message
    assert "KNX Standard v3.0.0" in message


def test_unknown_control_message_flags_registry() -> None:
    message = gaps.describe_missing("LdCtrlSomethingBrandNew")
    assert "not recognised" in message
    assert "gaps.py" in message


def test_known_gaps_are_never_silently_skipped_in_preflight() -> None:
    # A control that is a known implementation gap must not also be in the
    # no-write set, otherwise preflight would hide it instead of logging it.
    assert gaps.KNOWN_GAPS.keys().isdisjoint(gaps.PREFLIGHT_NO_WRITE)


def test_registry_excludes_implemented_controls() -> None:
    # Controls the runner executes must not be listed as gaps.
    for implemented in ("LdCtrlWriteMem", "LdCtrlWriteProp", "LdCtrlLoad"):
        assert implemented not in gaps.KNOWN_GAPS


def _application(*controls: object) -> Application:
    fake = SimpleNamespace(
        load_procedures=None,
        manufacturer_id="M-0072",
        program=SimpleNamespace(
            pei_type=1, application_number=1, application_version=1
        ),
    )
    return cast("Application", fake)


async def test_unsupported_control_error_is_diagnostic() -> None:
    class LdCtrlBrandNew:  # a control the runner does not handle
        pass

    application = _application()
    runner = LoadProcedureRunner(
        application,
        DownloadImage(segments=(), properties=()),
        DeviceProgrammer(FakeDevice()),
        controls=[LdCtrlBrandNew()],
    )

    with pytest.raises(UnsupportedProcedureError) as excinfo:
        await runner.run()

    message = str(excinfo.value)
    assert "LdCtrlBrandNew" in message
    assert "in-scope load control 1/1" in message
    assert "bug report" in message
    assert "app=" in message
