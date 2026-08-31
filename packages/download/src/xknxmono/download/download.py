"""High level entry point for downloading an application into a device.

Assembles the download image and runs the device's Load Procedure over a
point-to-point connection, following KNX Standard v3.0.0, Chapter 3/5/3
"Configuration Procedures": the complete download procedure (section 3.5.2) and
the partial download procedure (section 3.5.3).
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

from xknx.exceptions import ManagementConnectionError
from xknx.telegram import IndividualAddress

from .group_communication import synthesize_group_communication_controls
from .image import build_image
from .merge import resolve_download_controls
from .procedure import LoadProcedureRunner
from .programmer import MAX_NEGOTIATED_APDU_LENGTH
from .scope import DownloadScope

if TYPE_CHECKING:
    from xknx import XKNX
    from xknx.telegram.address import IndividualAddressableType

    from xknxmono.product import Application, MasterData

    from .data_secure import DeviceSecurity
    from .image import DownloadImage, GroupCommunication
    from .preflight import PreflightReport
    from .programmer import BusConnection, ConnectionManager
    from .project_data import SeedDevice


class _XknxConnectionManager:
    """Open/close point-to-point connections to one device via ``xknx``."""

    def __init__(self, xknx: XKNX, address: IndividualAddress) -> None:
        """Initialize for a target individual address."""
        self._xknx = xknx
        self._address = address
        self._connection: BusConnection | None = None

    async def open(self) -> BusConnection:
        """Open a fresh connection to the device."""
        self._connection = await self._xknx.management.connect(self._address)
        return self._connection

    async def close(self) -> None:
        """Close the current connection, tolerating a peer that already dropped it."""
        if self._connection is None:
            return
        self._connection = None
        with contextlib.suppress(ManagementConnectionError):
            await self._xknx.management.disconnect(self._address)


def _apdu_settings(max_apdu_length: int | None) -> tuple[int, bool]:
    """Resolve the APDU ceiling and whether to negotiate it from the device."""
    if max_apdu_length is None:
        return MAX_NEGOTIATED_APDU_LENGTH, True
    return max_apdu_length, False


def _connection_manager(
    xknx: XKNX, address: IndividualAddress, security: DeviceSecurity | None
) -> ConnectionManager:
    """Return a plain or a Tool-Key secured connection manager for ``address``."""
    if security is None:
        return _XknxConnectionManager(xknx, address)
    from .data_secure import SecureProgrammingError
    from .secure_session import SecureConnectionManager

    if security.address != address:
        raise SecureProgrammingError(
            f"security material is for {security.address}, not the download "
            f"target {address}"
        )
    return SecureConnectionManager(xknx, address, security)


def _apdu_overhead(security: DeviceSecurity | None) -> int:
    """Wire APDU overhead a secure session adds around each plaintext APDU."""
    if security is None:
        return 0
    from .data_secure import SECURE_APDU_OVERHEAD

    return SECURE_APDU_OVERHEAD


async def download(
    xknx: XKNX,
    individual_address: IndividualAddressableType,
    application: Application,
    *,
    master: MasterData | None = None,
    device: SeedDevice | None = None,
    image: DownloadImage | None = None,
    group_communication: GroupCommunication | None = None,
    scope: DownloadScope = DownloadScope.FULL,
    parameter_values: Mapping[str, str] | None = None,
    max_apdu_length: int | None = None,
    expected_descriptor: int | None = None,
    security: DeviceSecurity | None = None,
    progress: Callable[[int, int], None] | None = None,
) -> None:
    """Download ``application`` into the device at ``individual_address``.

    Assembles the download image (applying ``parameter_values`` on top of the
    application defaults), resolves the Load Procedure (merging the application's
    fragments into the mask version's default procedure from ``master`` for
    default/merged procedure styles) and runs it. The transport connection is
    opened and closed following the procedure's Connect/Disconnect/Restart
    controls. ``scope`` selects a full or partial download.

    ``max_apdu_length`` defaults to ``None``, which negotiates the length from the
    device (reading its maximum APDU length once, for larger and fewer telegrams);
    pass a fixed integer to override. ``expected_descriptor`` (the device
    descriptor type 0, e.g. ``0x07B0`` for a System B device) is checked against
    the device before any write when given, guarding against programming the wrong
    device.

    Pass a pre-built ``image`` to skip assembly (e.g. one an editor built from its
    live evaluator); otherwise it is built from ``device``/``parameter_values``.
    ``master`` (``registry.master``) is required for applications with a default
    or merged procedure style. The device must already carry ``individual_address``
    (program the individual address first for a virgin device). ``xknx`` has to be
    started.
    """
    if image is None:
        image = build_image(
            application,
            device=device,
            parameter_values=parameter_values,
            group_communication=group_communication,
        )
    controls = [
        *resolve_download_controls(
            application, master.raw if master is not None else None
        ),
        # System B products carry no Load Controls for the group communication
        # tables, so they are synthesized and appended here. NOTE: they run after
        # the application procedure; for a product whose procedure ends in a
        # Restart the runner reconnects and writes the tables in a fresh session.
        # ETS/Falcon instead bind the table images to the master procedure's own
        # allocation/write controls (before its restart). This ordering has only
        # been validated read-only via preflight, not on a real write+restart, so
        # it should be verified against hardware before relying on it there.
        *synthesize_group_communication_controls(image),
    ]
    address = IndividualAddress(individual_address)
    apdu_ceiling, negotiate_apdu = _apdu_settings(max_apdu_length)

    manager = _connection_manager(xknx, address, security)
    runner = LoadProcedureRunner(
        application,
        image,
        connection_manager=manager,
        max_apdu_length=apdu_ceiling,
        controls=controls,
        scope=scope,
        expected_descriptor=expected_descriptor,
        negotiate_apdu=negotiate_apdu,
        apdu_overhead=_apdu_overhead(security),
    )
    try:
        await runner.run(progress)
    finally:
        # Ensure the connection is closed even if the procedure omits a trailing
        # Disconnect or fails partway through.
        await manager.close()


async def preflight(
    xknx: XKNX,
    individual_address: IndividualAddressableType,
    application: Application,
    *,
    master: MasterData | None = None,
    device: SeedDevice | None = None,
    image: DownloadImage | None = None,
    group_communication: GroupCommunication | None = None,
    scope: DownloadScope = DownloadScope.FULL,
    parameter_values: Mapping[str, str] | None = None,
    max_apdu_length: int | None = None,
    expected_descriptor: int | None = None,
    security: DeviceSecurity | None = None,
) -> PreflightReport:
    """Report what :func:`download` would change on the device, changing nothing.

    Assembles the same download image and resolves the same Load Procedure as
    :func:`download` (with the same arguments), then reads the device's current
    bytes at every location a write would target and returns the diff. Nothing is
    written and no load state is changed. Run this before a real download to
    confirm the change set (and to catch a mismatched application via the
    procedure's compare controls). Pass a pre-built ``image`` to skip assembly.
    ``xknx`` has to be started.
    """
    if image is None:
        image = build_image(
            application,
            device=device,
            parameter_values=parameter_values,
            group_communication=group_communication,
        )
    controls = [
        *resolve_download_controls(
            application, master.raw if master is not None else None
        ),
        # System B products carry no Load Controls for the group communication
        # tables, so they are synthesized and appended here. NOTE: they run after
        # the application procedure; for a product whose procedure ends in a
        # Restart the runner reconnects and writes the tables in a fresh session.
        # ETS/Falcon instead bind the table images to the master procedure's own
        # allocation/write controls (before its restart). This ordering has only
        # been validated read-only via preflight, not on a real write+restart, so
        # it should be verified against hardware before relying on it there.
        *synthesize_group_communication_controls(image),
    ]
    address = IndividualAddress(individual_address)
    apdu_ceiling, negotiate_apdu = _apdu_settings(max_apdu_length)

    manager = _connection_manager(xknx, address, security)
    runner = LoadProcedureRunner(
        application,
        image,
        connection_manager=manager,
        max_apdu_length=apdu_ceiling,
        controls=controls,
        scope=scope,
        expected_descriptor=expected_descriptor,
        negotiate_apdu=negotiate_apdu,
        apdu_overhead=_apdu_overhead(security),
    )
    try:
        return await runner.preflight()
    finally:
        await manager.close()
