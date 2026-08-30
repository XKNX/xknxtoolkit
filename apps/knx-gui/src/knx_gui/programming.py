"""Program a configured device onto the bus, or preview what a download would change.

Bridges a GUI :class:`~knx_gui.device.Device` (which holds a live evaluator with the
current parameter state) to the ``xknxmono.download`` package: the download image is
built directly from the device's evaluator, so the bytes reflect exactly what the
editor shows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Import from the concrete modules: the package also has a ``preflight`` submodule,
# so ``from xknxmono.download import preflight`` is ambiguous to type checkers.
from xknxmono.download.download import download, preflight
from xknxmono.download.image import build_image
from xknxmono.download.scope import DownloadScope

if TYPE_CHECKING:
    from collections.abc import Callable

    from xknx import XKNX

    from knx_gui.device import Device
    from xknxmono.download.image import DownloadImage, GroupCommunication
    from xknxmono.download.preflight import PreflightReport


class DeviceProgrammingError(RuntimeError):
    """A device cannot be programmed as configured (no app, no address, ...)."""


def _image_for(
    device: Device, group_communication: GroupCommunication | None = None
) -> DownloadImage:
    ui = device.dynamic_ui
    if ui is None:
        raise DeviceProgrammingError("device has no dynamic application to program")
    return build_image(device.app, ui=ui, group_communication=group_communication)


def _address(device: Device) -> str:
    if not device.individual_address:
        raise DeviceProgrammingError("device has no individual address")
    return device.individual_address


def runtime_managed_addresses(device: Device) -> set[int]:
    """Absolute memory addresses of system parameters the device sets at runtime.

    These are parameters with access "None" (not user configurable), e.g. a
    download-detection byte the application firmware overwrites after a download.
    A pre-flight difference at such an address is expected and benign, so the
    result view can annotate it instead of flagging a real change.
    """
    ui = device.dynamic_ui
    if ui is None:
        return set()
    from xknxmono.product.parser_v2.application_indexer import ApplicationIndexer

    indexer = ApplicationIndexer(device.app.program)
    base_addresses = ui.segment_base_addrs()
    addresses: set[int] = set()
    for segment_id, offset_map in ui.memory_param_map().items():
        base = base_addresses.get(segment_id)
        if base is None:
            continue
        for offset, (parameter_id, _value) in offset_map.items():
            parameter = indexer.parameters.get(parameter_id)
            access = getattr(parameter, "access", None)
            if access is not None and access.name == "NONE":
                addresses.add(base + offset)
    return addresses


async def eval_device(
    xknx: XKNX,
    device: Device,
    scope: DownloadScope = DownloadScope.FULL,
    group_communication: GroupCommunication | None = None,
) -> PreflightReport:
    """Dry run: report what programming ``device`` would change, writing nothing."""
    return await preflight(
        xknx,
        _address(device),
        device.app,
        image=_image_for(device, group_communication),
        scope=scope,
    )


async def download_device(
    xknx: XKNX,
    device: Device,
    scope: DownloadScope = DownloadScope.FULL,
    group_communication: GroupCommunication | None = None,
    progress: Callable[[int, int], None] | None = None,
) -> None:
    """Program ``device``: build its image and run the load procedure on the bus.

    ``scope`` selects a full download or a partial one (parameters only, or group
    communication only), mirroring the ETS download options. ``group_communication``
    supplies the address/association tables a full or group download writes. ``progress``
    (optional) is called ``progress(done, total)`` after each executed load control.
    """
    await download(
        xknx,
        _address(device),
        device.app,
        image=_image_for(device, group_communication),
        scope=scope,
        progress=progress,
    )
