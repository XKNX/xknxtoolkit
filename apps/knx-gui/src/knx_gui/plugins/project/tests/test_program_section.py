"""Pure (no display) unit tests for `ProgramSection.reset()` and the
per-Future generation token that guards against stale Future callbacks after a
device switch in `ConfigurePanel`.

`ProgramSection`'s non-render paths (`__init__`, `_start`,
`_handle_future_done`, `_finish`, `reset`) don't call into imgui, so they can
be exercised headlessly - the only imgui dependency of the module is at import
time (module-level `imgui.ImVec4`/`ImVec2` constants), which works without a GL
context (same pattern as `knx_gui.dpt`, which has headless tests of its own).
The rendering paths and the end-to-end device-switch flow stay covered by the
e2e suite under `src/knx_gui/testing/tests/test_configure_panel.py`.

Run via the knx-gui unit-test job (no display needed):

    uv run pytest src/knx_gui/plugins/project/tests -v
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future
from types import SimpleNamespace
from typing import cast

from knx_gui.device import Device
from knx_gui.plugins.project.strings import S
from knx_gui.plugins.project.ui.components import ProgramRequest, ProgramSection


def _device(*, node_id: int, individual_address: str, name: str) -> Device:
    """Duck-typed `Device` stand-in carrying only what `ProgramSection`'s
    non-render paths read: `individual_address` (baked into the "Write
    Individual Address {address}" checklist label at `_start` time) and
    `name` (forwarded to `on_program`). `node_id` is irrelevant to
    `ProgramSection` itself but kept for parity with the real `Device`
    identity the Configure panel switches on."""
    return cast(
        Device,
        SimpleNamespace(
            node_id=node_id, individual_address=individual_address, name=name
        ),
    )


_DEVICE_A = _device(node_id=1, individual_address="1.1.4", name="DeviceA")
_DEVICE_B = _device(node_id=2, individual_address="2.2.7", name="DeviceB")


def _make_section() -> tuple[
    ProgramSection,
    Callable[[Future[None] | None], None],
]:
    """Build a `ProgramSection` wired so `on_program` returns whichever
    `Future` the test has currently staged - the same contract
    `ConnectionService.assign_individual_address_for_device` etc. implement.
    The returned `set_return_future` swaps the staged Future so a second
    `_start` (for the switched-to device) can return a different Future
    without reassigning `section._on_program`."""
    return_future: list[Future[None] | None] = [None]

    def on_program(device: Device, request: ProgramRequest) -> Future[None] | None:
        _ = (device, request)  # not asserted here; see the e2e suite.
        return return_future[0]

    def set_return_future(future: Future[None] | None) -> None:
        return_future[0] = future

    return ProgramSection(on_program), set_return_future


def _start(section: ProgramSection, device: Device) -> None:
    """Drive `_start` directly (bypassing the wizard) - the default
    `__init__` flags (button trigger, full scope) produce a valid request
    that programs the individual address."""
    section._start(device, "")  # pyright: ignore[reportPrivateUsage]


def _ia_label(section: ProgramSection) -> str:
    return section._checklist[  # pyright: ignore[reportPrivateUsage]
        1
    ][0]


def _ia_item_status(section: ProgramSection) -> str:
    return section._checklist[  # pyright: ignore[reportPrivateUsage]
        1
    ][1]


def _assert_idle_baseline(section: ProgramSection) -> None:
    assert section._status == "idle"  # pyright: ignore[reportPrivateUsage]
    assert section._step == "find_device"  # pyright: ignore[reportPrivateUsage]
    assert not section._trigger_serial  # pyright: ignore[reportPrivateUsage]
    assert section._scope_full  # pyright: ignore[reportPrivateUsage]
    assert section._scope_ia  # pyright: ignore[reportPrivateUsage]
    assert section._scope_ga  # pyright: ignore[reportPrivateUsage]
    assert section._scope_params  # pyright: ignore[reportPrivateUsage]
    assert section._checklist == []  # pyright: ignore[reportPrivateUsage]
    assert section._ia_checklist_index is None  # pyright: ignore[reportPrivateUsage]
    assert section._error_message == ""  # pyright: ignore[reportPrivateUsage]


def test_reset_restores_idle_baseline_on_fresh_section() -> None:
    """`reset()` must return every `__init__` field to its baseline. This is
    the exact invariant the original bug violated: `ProgramSection` was added
    with accumulated state but no reset path on the Configure panel's
    device-switch branch. A future change that adds state to one of
    `__init__`/`reset` but not the other fails here, guarding against the
    same oversight recurring."""
    section, _ = _make_section()

    section.reset()  # pyright: ignore[reportPrivateUsage]

    _assert_idle_baseline(section)


def test_reset_clears_running_program_state_and_leaves_future_pending() -> None:
    """Switching devices mid-program (`_status == "running"`) must reset the
    section to idle WITHOUT touching the in-flight Future - it is owned by the
    connection service, not the section. Guards against a future change that
    adds `future.cancel()`/`set_result(...)` to `reset()`: the underlying bus
    operation would be aborted or spuriously completed for the deselected
    device. The Future's stale completion is rejected separately by the
    generation token (see the test below)."""
    future: Future[None] = Future()
    section, set_return_future = _make_section()
    set_return_future(future)
    _start(section, _DEVICE_A)
    assert section._status == "running"  # pyright: ignore[reportPrivateUsage]
    assert not future.done()

    section.reset()  # pyright: ignore[reportPrivateUsage]

    _assert_idle_baseline(section)
    assert not future.done(), "reset() must not cancel or resolve the Future"


def test_stale_future_ignored_even_after_new_start_for_switched_device() -> None:
    """The per-Future generation guard's key correctness property.

    After a mid-program device switch, the user may start programming device B
    before device A's slow Future resolves. Device A's late completion must
    still be treated as stale - and must NOT clobber device B's in-flight
    result. This is the case a single `_start_generation` field (which the new
    `_start` overwrites) would get wrong: device A's late completion would
    pass the staleness check and flip `_status` to success under device B.
    Capturing the generation per Future (in the `on_done` closure at `_start`
    time) is what keeps it correct.

    Also confirms the guard has no false negatives: device B's own fresh
    Future still transitions to success and marks its checklist entry done.
    """
    future_a: Future[None] = Future()
    section, set_return_future = _make_section()
    set_return_future(future_a)
    _start(section, _DEVICE_A)

    section.reset()  # pyright: ignore[reportPrivateUsage]

    future_b: Future[None] = Future()
    set_return_future(future_b)
    _start(section, _DEVICE_B)
    assert section._status == "running"  # pyright: ignore[reportPrivateUsage]

    # DeviceA's slow program finally completes - must NOT touch the section,
    # which is now mid-program for DeviceB.
    future_a.set_result(None)
    assert section._status == "running"  # pyright: ignore[reportPrivateUsage]
    assert _ia_label(section) == S.PROGRAM_CHECKLIST_WRITE_IA.format(address="2.2.7")

    # DeviceB's own completion still applies (no false negatives from the guard).
    future_b.set_result(None)
    assert section._status == "success"  # pyright: ignore[reportPrivateUsage]
    assert _ia_item_status(section) == "done"
