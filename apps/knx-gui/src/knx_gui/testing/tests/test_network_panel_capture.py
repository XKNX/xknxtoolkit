"""E2E regression test for the Network panel capture-buffer wipe on reconnect.

Driven by Dear ImGui Test Engine against the *real* `KnxGuiApp`, so the actual
`NetworkPlugin`<->`ConnectionService` wiring
(`apps/knx-gui/src/knx_gui/plugins/network/plugin.py:16`,
`api.connection.add_connected_listener(self._service.start)`) is exercised -
not a hand-wired stand-in.

The bug: a user who clicks Stop to inspect captured traffic, then Disconnects
and Connects again (e.g. to swap gateways), loses the entire stopped buffer
because the connect listener fires `start()`, which used to `clear()` both
capture buffers. The fix removes those `clear()` calls from `start()`.

Why dispatch events directly instead of clicking the Connect menu item: the
report's own trigger-chain analysis shows `dispatch_connected()` is the *only*
way the connected event fires (called from `_connect_async` after
`await self._interface.start()` succeeds). Clicking the Connect menu would
attempt a real socket connection to a KNX gateway, which isn't available in
a headless test - so we simulate "the connect just succeeded" the same way the
production code does. Likewise `dispatch_raw_cemi` is the real path that raw
CEMI frames take from the KNX interface into `NetworkService.add_raw`.

Run with:
    uv run pytest src/knx_gui/testing/tests/test_network_panel_capture.py -v
(under a display; in CI/headless: `xvfb-run -a uv run pytest ...`).
"""

from __future__ import annotations

from xknx.cemi.cemi_frame import CEMIFrame, CEMILData
from xknx.cemi.const import CEMIMessageCode
from xknx.dpt.payload import DPTBinary
from xknx.telegram import Telegram
from xknx.telegram.address import GroupAddress, IndividualAddress
from xknx.telegram.apci import GroupValueWrite

# See test_configure_panel.py: importing knx_gui.main first establishes the
# same import order the app itself uses, side-stepping a circular import via
# knx_gui.plugins.node_editor -> knx_gui.widgets.
import knx_gui.main  # noqa: F401 # pyright: ignore[reportUnusedImport]
from knx_gui.plugins.network.service import CaptureState
from knx_gui.testing.harness import TestContext as _TestContext

# Alias to dodge pytest's default discovery trying to collect any name
# starting with "Test" as a test class (TestContext has an __init__).
from knx_gui.testing.harness import (
    build_app,
    run_ui_test,
)


def _make_cemi_bytes(
    group: str = "0/0/1", value: int = 1, src: str = "1.1.10"
) -> bytes:
    telegram = Telegram(
        destination_address=GroupAddress(group),
        source_address=IndividualAddress(src),
        payload=GroupValueWrite(DPTBinary(value)),
    )
    return CEMIFrame(
        code=CEMIMessageCode.L_DATA_IND,
        data=CEMILData.init_from_telegram(telegram, src_addr=telegram.source_address),
    ).to_knx()


def test_reconnect_after_stop_preserves_capture_buffer() -> None:
    """The exact bug scenario, driven through the real app wiring.

    Capture -> Stop -> Connect-again must NOT wipe the stopped buffer; the
    Clear button is the user's only wipe control.
    """
    app_handle = build_app()
    app = app_handle.app

    # Reach the real services wired in KnxGuiApp.__init__ (main.py:37,53).
    # plugin.py:16 wired `add_connected_listener(self._service.start)` on
    # construction, so dispatch_connected() below fires the real start().
    connection = app._connection_service  # pyright: ignore[reportPrivateUsage]
    network = app._network_plugin._service  # pyright: ignore[reportPrivateUsage]

    cemi = _make_cemi_bytes()
    result: dict[str, object] = {}

    def test_function(ctx: _TestContext) -> None:
        # Let the app render a few frames so docking/panels settle.
        ctx.yield_()
        ctx.yield_()

        # 1. User clicks Connect -> _connect_async succeeds -> dispatch_connected()
        #    fires the wired start(): capture begins (state STOPPED -> CAPTURING).
        connection.dispatch_connected()
        ctx.yield_()

        # 2. Real frames arrive over the bus via the wired raw-CEMI listener
        #    (plugin.py:15: add_raw_cemi_listener(self._service.add_raw)).
        for _ in range(5):
            connection.dispatch_raw_cemi(cemi)
        ctx.yield_()

        assert network.state == CaptureState.CAPTURING  # pyright: ignore[reportPrivateUsage]
        assert len(network.telegrams) == 5  # pyright: ignore[reportPrivateUsage]
        assert len(network.cemi_records) == 5  # pyright: ignore[reportPrivateUsage]

        # 3. User clicks Stop (the Network panel toolbar's record/stop button
        #    is wired via on_stop=self._service.stop). Capture pauses; the user
        #    keeps the buffer to inspect it.
        network.stop()  # pyright: ignore[reportPrivateUsage]
        ctx.yield_()

        assert network.state == CaptureState.STOPPED  # pyright: ignore[reportPrivateUsage]
        assert len(network.telegrams) == 5  # pyright: ignore[reportPrivateUsage]

        telegrams_snapshot = list(network.telegrams)  # pyright: ignore[reportPrivateUsage]
        cemi_snapshot = list(network.cemi_records)  # pyright: ignore[reportPrivateUsage]

        # 4. User Disconnects, then Connects again (e.g. to swap gateways or
        #    recover a flaky link). dispatch_connected() fires the wired
        #    start() once more - THE BUG TRIGGER. Before the fix this wiped
        #    the stopped buffer to 0/0 and resumed capture silently.
        connection.dispatch_connected()
        ctx.yield_()
        ctx.yield_()

        result["state"] = network.state  # pyright: ignore[reportPrivateUsage]
        result["telegrams"] = list(network.telegrams)  # pyright: ignore[reportPrivateUsage]
        result["cemi_records"] = list(network.cemi_records)  # pyright: ignore[reportPrivateUsage]
        result["telegrams_snapshot"] = telegrams_snapshot
        result["cemi_snapshot"] = cemi_snapshot

    run_ui_test(test_function, app_handle=app_handle)

    assert result["state"] == CaptureState.CAPTURING
    assert result["telegrams"] == result["telegrams_snapshot"]
    assert result["cemi_records"] == result["cemi_snapshot"]
    assert len(result["telegrams"]) == 5  # type: ignore[arg-type]
    assert len(result["cemi_records"]) == 5  # type: ignore[arg-type]
