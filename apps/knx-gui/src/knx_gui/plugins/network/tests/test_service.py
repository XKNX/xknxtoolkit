from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast

import pytest
from xknx.cemi.cemi_frame import CEMIFrame, CEMILData
from xknx.cemi.const import CEMIMessageCode
from xknx.dpt.payload import DPTBinary
from xknx.telegram import Telegram
from xknx.telegram.address import GroupAddress, IndividualAddress
from xknx.telegram.apci import GroupValueWrite

from knx_gui.net import TelegramSource
from knx_gui.plugins.base import Logger
from knx_gui.plugins.connection.service import ConnectionService
from knx_gui.plugins.network.service import CaptureState, NetworkService


def make_cemi_bytes(
    group: str = "0/0/1", value: int = 1, source: str = "1.1.10"
) -> bytes:
    telegram = Telegram(
        destination_address=GroupAddress(group),
        source_address=IndividualAddress(source),
        payload=GroupValueWrite(DPTBinary(value)),
    )
    return CEMIFrame(
        code=CEMIMessageCode.L_DATA_IND,
        data=CEMILData.init_from_telegram(telegram, src_addr=telegram.source_address),
    ).to_knx()


def _silent_error(*args: object, **kwargs: object) -> None:
    # NetworkService only ever calls self._log.error(...); this stand-in (cast
    # to Logger) is the repo's SimpleNamespace + cast idiom for duck-typed fakes.
    pass


@pytest.fixture
def service() -> NetworkService:
    svc = NetworkService()
    svc.set_logger(cast(Logger, SimpleNamespace(error=_silent_error)))
    return svc


def test_start_does_not_clear_existing_telegrams_or_cemi(
    service: NetworkService,
) -> None:
    # Regression guard for the capture-buffer wipe on reconnect: NetworkPlugin
    # wires add_connected_listener(self._service.start) (plugin.py:16), so a
    # manual Connect fires start() again. The stopped capture buffer the user
    # paused to inspect must survive this — only clear() (the Clear button)
    # wipes buffers.
    service.start()
    cemi = make_cemi_bytes()
    for _ in range(3):
        service.add_raw_with_timestamp(
            cemi, TelegramSource.CONNECTION, datetime.now(UTC)
        )
    assert len(service.telegrams) == 3
    assert len(service.cemi_records) == 3

    service.stop()
    assert service.state == CaptureState.STOPPED

    service.start()  # the connect listener firing start

    assert service.state == CaptureState.CAPTURING
    assert len(service.telegrams) == 3
    assert len(service.cemi_records) == 3


def test_new_frames_append_to_preserved_buffer_after_reconnect(
    service: NetworkService,
) -> None:
    # The preserved buffer stays usable: frames captured after a reconnect
    # appends to it rather than replacing — so the user keeps both the paused
    # analysis data and the new traffic.
    service.start()
    service.add_raw_with_timestamp(
        make_cemi_bytes("0/0/1", 1), TelegramSource.CONNECTION, datetime.now(UTC)
    )
    service.stop()
    service.start()  # connect listener

    service.add_raw_with_timestamp(
        make_cemi_bytes("0/0/2", 0), TelegramSource.CONNECTION, datetime.now(UTC)
    )
    assert len(service.telegrams) == 2
    assert len(service.cemi_records) == 2


def test_manual_start_does_not_clear_user_must_use_clear(
    service: NetworkService,
) -> None:
    # After the fix, Start (manual or connect-triggered) never wipes data; the
    # Clear button (on_clear=self._service.clear) is the only wipe path.
    service.start()
    service.add_raw_with_timestamp(
        make_cemi_bytes(), TelegramSource.CONNECTION, datetime.now(UTC)
    )
    service.stop()
    service.start()
    assert len(service.telegrams) == 1
    assert len(service.cemi_records) == 1

    service.clear()
    assert service.telegrams == []
    assert service.cemi_records == []


def test_connect_listener_does_not_clear_stopped_capture(
    service: NetworkService,
) -> None:
    # End-to-end via the real ConnectionService wiring (plugin.py:16):
    #   api.connection.add_connected_listener(self._service.start)
    # The Stop -> manual Connect -> dispatch_connected -> start() chain is the
    # exact bug trigger — the stopped buffer must survive it.
    connection = ConnectionService()
    connection.add_connected_listener(service.start)

    connection.dispatch_connected()
    assert service.state == CaptureState.CAPTURING

    for _ in range(5):
        service.add_raw_with_timestamp(
            make_cemi_bytes(), TelegramSource.CONNECTION, datetime.now(UTC)
        )

    service.stop()  # user clicks Stop to inspect
    assert service.state == CaptureState.STOPPED

    telegrams_snapshot = list(service.telegrams)
    cemi_snapshot = list(service.cemi_records)

    connection.dispatch_connected()  # user clicks Disconnect then Connect

    assert service.state == CaptureState.CAPTURING
    assert service.telegrams == telegrams_snapshot
    assert service.cemi_records == cemi_snapshot
