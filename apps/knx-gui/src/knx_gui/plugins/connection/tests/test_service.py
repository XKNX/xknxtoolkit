"""Unit tests for ConnectionService's `Future | None` contract.

Pure-Python tests (no asyncio loop running, no xknx I/O) of the early-return /
dispatch logic of `ConnectionService`, modeled on
`plugins/tasks/tests/test_service.py`: direct instantiation, no fixtures, plain
`def test_...()` functions (pyright strict).

Background - why these tests exist in the connection plugin rather than only
in `test_configure_panel.py`:

`ProgramSection._start` treats `None` from `on_program` as the "not connected"
sentinel and reports `S.PROGRAM_LOG_NOT_CONNECTED` ("Not connected - nothing
was sent"). That contract originates in this service: every
`assign_individual_address*()` (and `restart_device`,
`read_programming_devices`) returns `None` *specifically* when the service is
disconnected (`self._xknx is None`) - the documented convention
`project/plugin.py::_handle_program_device` names ("None is what
assign_individual_address*() returns specifically for that").

`assign_individual_address_for_device` is the lone exception: it also returns
`None` when `device.individual_address` is empty, *before* `self._xknx` is
consulted - flattening "no IA" and "disconnected" into the single sentinel the
rest of the app reads as disconnected. The user-facing fix for the misleading
"Not connected" that produces lives in `ProgramSection` (which disables the
Program button when the IA scope is active and `device.individual_address` is
empty, mirroring `RestartSection`'s Reset button guard). These tests
characterize the service-level behavior the UI guard works around, so a future
refactor here (e.g. routing the empty-IA branch off the `None` sentinel) has a
record of the contract it would still need to honor; they don't themselves
assert the empty-IA branch returns anything other than `None` - that is
precisely the collision the UI fix renders unreachable.
"""

from __future__ import annotations

from collections.abc import Coroutine
from concurrent.futures import Future
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from knx_gui.device import Device
from knx_gui.plugins.connection.service import ConnectionService


def _service(connected: bool = False) -> ConnectionService:
    """A `ConnectionService` wired with a stub `Logger`.

    `connected=True` shuts the `self._xknx is None` guard with a MagicMock
    xknx (so the `assign_*` early-returns are skipped past the disconnect
    check). The event loop is left `None`: the disconnected and empty-IA cases
    return `None` before `run_async` is ever reached, and the "schedules a
    write" tests stub `run_async` - so a real loop would never be run and would
    just leak without adding any coverage.
    """
    cs = ConnectionService()
    cs.set_logger(MagicMock())
    if connected:
        cs.set_connection(MagicMock(name="xknx"), None)
    return cs


def _stub_run_async(
    cs: ConnectionService, monkeypatch: pytest.MonkeyPatch
) -> list[Coroutine[Any, Any, Any]]:
    """Replace `cs.run_async` with a version that records the coroutine, closes
    it (so the MagicMock-xknx coroutine built by the `assign_*` methods is never
    awaited on a loop that doesn't run), and returns a fresh unresolved Future.

    Returns the list the closed coroutines are appended to, so a caller can
    assert "exactly one write was scheduled".
    """
    captured: list[Coroutine[Any, Any, Any]] = []

    def close_and_stub(coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        captured.append(coro)
        coro.close()
        future: Future[Any] = Future()
        return future

    monkeypatch.setattr(cs, "run_async", close_and_stub)
    return captured


def test_disconnected_returns_none_across_assign_family_and_restart() -> None:
    """When the service is disconnected, every method `ProgramSection`,
    `RestartSection` and the Configure panel rely on returns `None` - the
    documented "not connected" sentinel `ProgramSection._start` flips into
    `S.PROGRAM_LOG_NOT_CONNECTED`. This is the contract the rest of the
    `assign_individual_address*()` family is supposed to honor *exclusively*
    for the disconnected case."""
    cs = _service(connected=False)
    device = cast(Device, SimpleNamespace(name="Dev", individual_address="1.1.1"))

    assert cs.assign_individual_address("1.1.1") is None
    assert cs.assign_individual_address_by_serial(b"\x00" * 6, "1.1.1") is None
    assert cs.assign_individual_address_for_device(device) is None
    assert cs.restart_device("1.1.1") is None
    assert cs.read_programming_mode_devices() is None


def test_assign_individual_address_for_device_returns_none_for_empty_ia_even_when_connected() -> (
    None
):
    """The contract collision at the heart of the ProgramSection bug: an empty
    `device.individual_address` returns `None` *even when the service is
    connected* - the empty-IA guard fires before `self._xknx` is consulted, so
    the `None` is indistinguishable from a real disconnect. The fix lives
    upstream in `ProgramSection` (disable the Program button when the IA scope
    is active and IA is empty); this test pins the service-level behavior the
    UI guard works around so a future change here can't silently break the
    contract `ProgramSection` still leans on for the *real* disconnected case.
    """
    cs = _service(connected=True)
    fresh = cast(Device, SimpleNamespace(name="Fresh", individual_address=""))

    assert cs.assign_individual_address_for_device(fresh) is None


def test_assign_individual_address_for_device_delegates_when_connected_and_ia_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The happy path the Program button's button trigger relies on: a
    connected service + a device whose IA is set delegates through
    `assign_individual_address` to `run_async`, returning a Future (not the
    `None` sentinel). Stubs `run_async` so the real
    `nm_individual_address_write` coroutine - which the MagicMock xknx here
    would not survive being awaited - is closed rather than scheduled."""
    cs = _service(connected=True)
    captured = _stub_run_async(cs, monkeypatch)
    device = cast(Device, SimpleNamespace(name="Dev", individual_address="1.1.250"))

    result = cs.assign_individual_address_for_device(device)

    assert result is not None
    assert len(captured) == 1, "exactly one IA write must be scheduled"


def test_assign_individual_address_by_serial_returns_future_when_connected_even_with_empty_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The serial trigger is NOT subject to the empty-IA guard:
    `assign_individual_address_by_serial` passes the (possibly empty) address
    straight to `nm_individual_address_serial_number_write`, which fails
    *downstream* with the real reason - rather than returning the `None`
    "not connected" sentinel the button trigger collides with. That is why the
    bug report's "serial path is NOT affected" contrast holds, and why the
    ProgramSection UI guard disables the Program button for both triggers:
    with the empty IA the serial write would still fail, just less helpfully
    than disabling the button outright.
    """
    cs = _service(connected=True)
    captured = _stub_run_async(cs, monkeypatch)

    result = cs.assign_individual_address_by_serial(b"\x00\x01\x02\x03\x05\x06", "")

    assert result is not None, "serial write must be scheduled even with empty IA"
    assert len(captured) == 1
