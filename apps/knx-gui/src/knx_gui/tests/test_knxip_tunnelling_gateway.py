"""
Covers the `_client_data_received` TCP framing / dispatch loop of
`TunnellingGateway`.

Driven directly against the real handler path: a real `CONNECT_REQUEST`
flips `_channel_id` to 1, and real `TUNNELLING_REQUEST` bodies are the
only thing a tunnelling client sends unsolicited in steady state -- so
`_handle_tunnelling_request`'s observable side effects (`_cemi_count +=
1`, the `on_cemi` callback) are the right behavioural metric. No
transport is attached, so `_send()` early-returns on every reply (the
gateway still ticks `_channel_id` / `_cemi_count` exactly as in
production); `_handle_body`'s real isinstance dispatch is exercised
verbatim.

The broad `except Exception` branch in the framing loop re-syncs past a
malformed/unfamiliar frame using its declared `total_length` (when the
KNX/IP header was well-formed enough to provide one) and continues the
loop, instead of dropping every well-formed frame that followed the bad
one in the same TCP segment.
"""

from __future__ import annotations

import struct
from unittest.mock import MagicMock

from xknx.knxip import (
    HPAI,
    ConnectRequest,
    ConnectRequestInformation,
    KNXIPFrame,
    TunnellingRequest,
)
from xknx.knxip.knxip_enum import HostProtocol, KNXIPServiceType

from knx_gui.knxip_tunnelling_gateway import TunnellingGateway

# A service type not enumerated by the pinned xknx 3.20.0 - structurally
# the "forward-compat KNXnet/IP spec revision" case the broad-except
# exists for. `KNXIPHeader.from_knx` sets `total_length` *before* raising
# `CouldNotParseKNXIP`, so the call site can re-sync on it.
_UNKNOWN_SERVICE_TYPE = 0x0F0F


# --- helpers ---------------------------------------------------------------


def _hdr(service_type: int, total_length: int) -> bytes:
    """A 6-byte KNX/IP header with protocol version 0x10."""
    return struct.pack(
        "!BBBBBB",
        0x06,
        0x10,
        (service_type >> 8) & 0xFF,
        service_type & 0xFF,
        (total_length >> 8) & 0xFF,
        total_length & 0xFF,
    )


def _connect_request() -> bytes:
    """A real CONNECT_REQUEST - _handle_connect_request sets _channel_id=1."""
    cr = ConnectRequest(
        control_endpoint=HPAI(protocol=HostProtocol.IPV4_TCP),
        data_endpoint=HPAI(protocol=HostProtocol.IPV4_TCP),
        cri=ConnectRequestInformation(),
    )
    return KNXIPFrame.init_from_body(cr).to_knx()


def _tunnelling_request(channel: int = 1, sequence: int = 0) -> bytes:
    """A well-formed TUNNELLING_REQUEST on `channel` carrying 4 bytes of cEMI."""
    tr = TunnellingRequest(
        communication_channel_id=channel,
        sequence_counter=sequence,
        raw_cemi=b"\x11\x00\x00\x00",
    )
    return KNXIPFrame.init_from_body(tr).to_knx()


def _bad_unknown_service_type_frame(total_length: int = 14) -> bytes:
    """Well-formed 6-byte header with an unknown service type 0x0F0F.

    `xknx.knxip.header.KNXIPHeader.from_knx` sets `total_length` and then
    raises `CouldNotParseKNXIP` (via the inner `KNXIPServiceType(...)`
    `ValueError`), so the broad `except Exception` catches it - not the
    earlier `IncompleteKNXIPFrame` branch.
    """
    return _hdr(_UNKNOWN_SERVICE_TYPE, total_length) + b"\x00" * (total_length - 6)


def _bad_search_request_extended_unknown_srp() -> bytes:
    """SEARCH_REQUEST_EXTENDED carrying an SRP of unknown type 0x33.

    The inline comment in `_client_data_received` names this path
    verbatim: `xknx.knxip.srp.SRP.from_knx` raises a plain `ValueError`
    on the unknown `SearchRequestParameterType`, propagated unguarded
    through `KNXIPFrame.from_knx` and caught by the broad-except.
    """
    hpai = bytes([0x08, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    srp = bytes([0x02, 0x33])
    body = hpai + srp
    return _hdr(KNXIPServiceType.SEARCH_REQUEST_EXTENDED.value, 6 + len(body)) + body


def _make_gateway() -> tuple[TunnellingGateway, list[bytes]]:
    """A gateway with discovery off, a MagicMock logger, and no transport
    attached, so `_send()` early-returns on every reply. The `on_cemi`
    callback appends received cEMIs to a list for behavioural asserts.
    Returns `(gateway, received_cemis)`.
    """
    received: list[bytes] = []
    gw = TunnellingGateway(
        enable_discovery=False,
        logger=MagicMock(),
        on_cemi=received.append,
    )
    return gw, received


def _connected_gateway() -> tuple[TunnellingGateway, list[bytes]]:
    """`_make_gateway` after a CONNECT_REQUEST has set `_channel_id = 1`."""
    gw, received = _make_gateway()
    _dispatch(gw, _connect_request())
    assert _channel_id(gw) == 1
    return gw, received


def _dispatch(gw: TunnellingGateway, data: bytes) -> None:
    """Drive the framing loop directly (its only caller is the asyncio shim)."""
    gw._client_data_received(data)  # pyright: ignore[reportPrivateUsage]


def _cemi_count(gw: TunnellingGateway) -> int:
    return gw._cemi_count  # pyright: ignore[reportPrivateUsage]


def _buffer_len(gw: TunnellingGateway) -> int:
    return len(gw._buffer)  # pyright: ignore[reportPrivateUsage]


def _channel_id(gw: TunnellingGateway) -> int | None:
    return gw._channel_id  # pyright: ignore[reportPrivateUsage]


# --- baseline framing: partial-frame re-buffer & multi-frame loop ----------


def test_partial_frame_is_rebuffered_then_completed_next_callback() -> None:
    """A split-across-callbacks frame must complete and dispatch via _buffer."""
    gw, received = _connected_gateway()
    full = _tunnelling_request(channel=1, sequence=0)
    half = len(full) // 2
    _dispatch(gw, full[:half])
    assert _cemi_count(gw) == 0
    assert received == []
    assert _buffer_len(gw) == half
    _dispatch(gw, full[half:])
    assert _cemi_count(gw) == 1
    assert received == [b"\x11\x00\x00\x00"]
    assert _buffer_len(gw) == 0


def test_two_complete_good_frames_in_one_segment_both_dispatch() -> None:
    """The framing loop dispatches every complete frame in one segment."""
    gw, received = _connected_gateway()
    _dispatch(gw, _tunnelling_request(1, 0) + _tunnelling_request(1, 1))
    assert _cemi_count(gw) == 2
    assert received == [b"\x11\x00\x00\x00", b"\x11\x00\x00\x00"]


# --- the fix: a trailing good frame IS now dispatched ----------------------


def test_unknown_service_type_coalesced_with_good_dispatches_good() -> None:
    """Trigger A: unknown KNXIPServiceType (CouldNotParseKNXIP after
    total_length is set), coalesced with a good TUNNELLING_REQUEST in one
    segment. Before the fix the trailing good frame was lost; after the
    fix it is dispatched."""
    gw, received = _connected_gateway()
    bad = _bad_unknown_service_type_frame()
    good = _tunnelling_request(channel=1, sequence=0)
    _dispatch(gw, bad + good)
    assert _cemi_count(gw) == 1
    assert received == [b"\x11\x00\x00\x00"]
    assert _buffer_len(gw) == 0


def test_search_request_extended_unknown_srp_coalesced_with_good_dispatches_good() -> (
    None
):
    """Trigger B (the inline comment's literal named example): unknown SRP
    type in SearchRequestExtended raises a plain ValueError on TCP,
    coalesced with a good frame. The trailing good frame is dispatched."""
    gw, received = _connected_gateway()
    bad = _bad_search_request_extended_unknown_srp()
    good = _tunnelling_request(channel=1, sequence=0)
    _dispatch(gw, bad + good)
    assert _cemi_count(gw) == 1
    assert received == [b"\x11\x00\x00\x00"]
    assert _buffer_len(gw) == 0


def test_multiple_trailing_good_frames_after_bad_all_dispatch() -> None:
    """The re-sync continues the loop, so `bad + good + good + good`
    dispatches all three trailing frames, not just the first."""
    gw, received = _connected_gateway()
    bad = _bad_unknown_service_type_frame()
    _dispatch(
        gw,
        bad
        + _tunnelling_request(1, 0)
        + _tunnelling_request(1, 1)
        + _tunnelling_request(1, 2),
    )
    assert _cemi_count(gw) == 3
    assert received == [b"\x11\x00\x00\x00"] * 3


# --- no persistent desync --------------------------------------------------
# The broad-except never re-buffers unparseable bytes (the IncompleteKNXIPFrame
# branch handles re-buffering cleanly), so a misalignment cannot propagate
# into a later segment.


def test_fresh_good_frame_after_resync_dispatches_normally() -> None:
    """After a coalesced `bad + good` dispatch, a clean good frame in a new
    callback dispatches normally - no persistent desync."""
    gw, received = _connected_gateway()
    bad = _bad_unknown_service_type_frame()
    _dispatch(gw, bad + _tunnelling_request(1, 0))
    assert _cemi_count(gw) == 1
    _dispatch(gw, _tunnelling_request(1, 1))
    assert _cemi_count(gw) == 2
    assert received == [b"\x11\x00\x00\x00", b"\x11\x00\x00\x00"]
    assert _buffer_len(gw) == 0


def test_straddled_good_frame_recovered_across_callbacks() -> None:
    """`bad + first_half_of_good` in segment 1, second half of good in
    segment 2. With the fix, the re-sync skips the bad frame, leaving
    the first half of good as an IncompleteKNXIPFrame -> re-buffered, then
    re-completed and dispatched when the second half arrives. The
    transport stays clean (no persistent desync, no surviving garbage)."""
    gw, received = _connected_gateway()
    bad = _bad_unknown_service_type_frame()
    good = _tunnelling_request(channel=1, sequence=0)
    half = len(good) // 2
    _dispatch(gw, bad + good[:half])
    # The bad frame was skipped; the partial good is incomplete -> re-buffered.
    assert _cemi_count(gw) == 0
    assert _buffer_len(gw) == half
    _dispatch(gw, good[half:])
    assert _cemi_count(gw) == 1
    assert received == [b"\x11\x00\x00\x00"]
    assert _buffer_len(gw) == 0


# --- non-resyncable cases keep the existing drop-and-return behaviour ------


def test_genuine_stream_corruption_drops_tail_keeps_transport_open() -> None:
    """data[0] != 0x06: KNXIPHeader.from_knx raises before setting
    total_length, so no re-sync is possible. The rest of the segment is
    dropped (as before the fix) and the transport stays open (no exception
    propagates out of _client_data_received)."""
    gw, received = _connected_gateway()
    garbage = b"\xff\x10\x00\x00\x00\x0e" + b"\x00" * 8
    _dispatch(gw, garbage + _tunnelling_request(1, 0))
    assert _cemi_count(gw) == 0
    assert received == []
    assert _buffer_len(gw) == 0


def test_declared_total_length_exceeds_received_bytes_drops_tail_no_rebuffer() -> None:
    """Header is well-formed but its declared total_length exceeds the
    bytes actually received in this segment. Re-sync to data[total_length:]
    would skip past the actual bad frame into unrelated bytes, so the fix
    treats it as non-resyncable: drop the rest of the segment (no
    re-buffer - the bytes are not a known-good frame prefix)."""
    gw, received = _connected_gateway()
    bad = _hdr(_UNKNOWN_SERVICE_TYPE, 1000)  # only 6 bytes, total_length=1000
    _dispatch(gw, bad + _tunnelling_request(1, 0))
    assert _cemi_count(gw) == 0
    assert received == []
    assert _buffer_len(gw) == 0
