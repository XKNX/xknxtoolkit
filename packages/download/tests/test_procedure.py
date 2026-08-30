"""Tests for the Load Procedure interpreter."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest
from xknx.telegram.apci import (
    FunctionPropertyCommand,
    FunctionPropertyStateRead,
    MemoryRead,
    PropertyValueWrite,
)

from xknxmono.download.errors import DownloadError
from xknxmono.download.image import (
    DownloadImage,
    MemorySegment,
    PropertyValue,
    RelativeSegment,
)
from xknxmono.download.load_state import PID_LOAD_STATE_CONTROL, LoadState
from xknxmono.download.procedure import LoadProcedureRunner
from xknxmono.download.programmer import DeviceProgrammer
from xknxmono.download.scope import DownloadScope
from xknxmono.models.intermediate.ld_ctrl_abs_segment_t import LdCtrlAbsSegment
from xknxmono.models.intermediate.ld_ctrl_connect_t import LdCtrlConnect
from xknxmono.models.intermediate.ld_ctrl_declare_prop_desc_t import (
    LdCtrlDeclarePropDesc,
)
from xknxmono.models.intermediate.ld_ctrl_disconnect_t import LdCtrlDisconnect
from xknxmono.models.intermediate.ld_ctrl_invoke_function_prop_t import (
    LdCtrlInvokeFunctionProp,
)
from xknxmono.models.intermediate.ld_ctrl_load_completed_t import LdCtrlLoadCompleted
from xknxmono.models.intermediate.ld_ctrl_load_image_mem_t import LdCtrlLoadImageMem
from xknxmono.models.intermediate.ld_ctrl_load_t import LdCtrlLoad
from xknxmono.models.intermediate.ld_ctrl_master_reset_t import LdCtrlMasterReset
from xknxmono.models.intermediate.ld_ctrl_read_function_prop_t import (
    LdCtrlReadFunctionProp,
)
from xknxmono.models.intermediate.ld_ctrl_restart_t import LdCtrlRestart
from xknxmono.models.intermediate.ld_ctrl_unload_t import LdCtrlUnload
from xknxmono.models.intermediate.ld_ctrl_write_mem_t import LdCtrlWriteMem
from xknxmono.models.intermediate.ld_ctrl_write_prop_t import LdCtrlWriteProp
from xknxmono.models.intermediate.ld_ctrl_write_rel_mem_t import LdCtrlWriteRelMem
from xknxmono.models.intermediate.load_procedure_style_t import LoadProcedureStyle
from xknxmono.models.intermediate.load_procedures_t import LoadProcedures
from xknxmono.models.intermediate.load_procedures_t_load_procedure import (
    LoadProceduresLoadProcedure,
)

from .conftest import FakeDevice

if True:  # keep import used for typing without a runtime dependency cycle
    from xknxmono.product import Application

# Interface object type of the address table object used in the fixtures below.
_ADDRESS_TABLE_TYPE = 1


def _application(*controls: object) -> Application:
    """Wrap Load Controls into a minimal application stand-in."""
    procedure = LoadProceduresLoadProcedure(choice=list(controls))  # type: ignore[arg-type]
    load_procedures = LoadProcedures(load_procedure=[procedure])
    fake = SimpleNamespace(
        load_procedures=load_procedures,
        load_procedure_style=LoadProcedureStyle.PRODUCT_PROCEDURE,
        manufacturer_id="M-0072",
        program=SimpleNamespace(
            pei_type=1,
            application_number=1,
            application_version=1,
            mask_version="MV-0705",
        ),
    )
    return cast("Application", fake)


def _runner(
    application: Application, image: DownloadImage
) -> tuple[LoadProcedureRunner, FakeDevice]:
    device = FakeDevice(object_types={0: 0x0000, 1: _ADDRESS_TABLE_TYPE})
    programmer = DeviceProgrammer(device)
    return LoadProcedureRunner(application, image, programmer), device


async def test_full_property_based_sequence() -> None:
    image = DownloadImage(
        segments=(MemorySegment(address=0x4000, data=bytes(range(8))),),
        properties=(),
    )
    application = _application(
        LdCtrlConnect(),
        LdCtrlUnload(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        LdCtrlWriteMem(
            address=0x4000, size=8, verify=False, inline_data=bytes(range(8))
        ),
        LdCtrlLoadCompleted(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        LdCtrlRestart(),
        LdCtrlDisconnect(),
    )
    runner, device = _runner(application, image)

    await runner.run()

    # the data was written to memory
    assert bytes(device.memory[0x4000 + i] for i in range(8)) == bytes(range(8))
    # the load state machine ended up loaded and the device restarted
    assert device.load_states[1] == LoadState.LOADED
    assert device.restarted
    assert runner.restarted


async def test_load_image_mem_reads_without_writing() -> None:
    application = _application(LdCtrlLoadImageMem(address=0x4000, size=4))
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    # LoadImageMem reads device memory into the image; it must not write.
    assert 0x4000 not in device.memory
    assert any(isinstance(p, MemoryRead) and p.address == 0x4000 for p in device.sent)


async def test_master_reset_sends_restart_master_reset() -> None:
    application = _application(
        LdCtrlConnect(),
        LdCtrlMasterReset(erase_code=4, channel_number=0),
        LdCtrlDisconnect(),
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    # The Master Reset went out with its erase code / channel and marked a restart.
    assert device.master_reset == (4, 0)
    assert device.restarted
    assert runner.restarted


async def test_master_reset_error_code_raises() -> None:
    application = _application(LdCtrlMasterReset(erase_code=4, channel_number=0))
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))
    device.master_reset_error_code = 0x02

    with pytest.raises(DownloadError, match="refused master reset"):
        await runner.run()


async def test_invoke_function_property_sends_command() -> None:
    application = _application(
        LdCtrlInvokeFunctionProp(obj_idx=1, prop_id=52, inline_data=bytes([0x01, 0x02]))
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert device.function_properties[(1, 52)] == bytes([0x01, 0x02])
    assert any(
        isinstance(p, FunctionPropertyCommand)
        and p.object_index == 1
        and p.property_id == 52
        for p in device.sent
    )


async def test_invoke_function_property_error_code_raises() -> None:
    application = _application(
        LdCtrlInvokeFunctionProp(obj_idx=1, prop_id=52, inline_data=b"\x01")
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))
    device.function_property_return_code = 0x03

    with pytest.raises(DownloadError, match="returned error code"):
        await runner.run()


async def test_read_function_property_reads_without_writing() -> None:
    application = _application(LdCtrlReadFunctionProp(obj_idx=1, prop_id=52))
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert (1, 52) not in device.function_properties
    assert any(
        isinstance(p, FunctionPropertyStateRead) and p.property_id == 52
        for p in device.sent
    )


async def test_declare_prop_desc_is_client_side_noop() -> None:
    # DeclarePropDesc only declares a property description to the client object
    # model; it must not send any telegram.
    application = _application(
        LdCtrlDeclarePropDesc(
            obj_idx=1,
            prop_id=52,
            prop_type=1,
            max_elements=1,
            read_access=0,
            write_access=0,
            writable=True,
        )
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert device.sent == []


async def test_write_mem_inline_data() -> None:
    application = _application(
        LdCtrlWriteMem(address=0x100, size=3, verify=False, inline_data=b"\x01\x02\x03")
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert bytes(device.memory[0x100 + i] for i in range(3)) == b"\x01\x02\x03"


async def test_write_mem_image_backed() -> None:
    image = DownloadImage(
        segments=(MemorySegment(address=0x500, data=b"\xde\xad\xbe\xef"),),
        properties=(),
    )
    application = _application(
        LdCtrlWriteMem(address=0x500, size=4, verify=False, inline_data=None)
    )
    runner, device = _runner(application, image)

    await runner.run()

    assert bytes(device.memory[0x500 + i] for i in range(4)) == b"\xde\xad\xbe\xef"


async def test_write_rel_mem_uses_table_reference() -> None:
    application = _application(
        LdCtrlWriteRelMem(
            obj_type=_ADDRESS_TABLE_TYPE,
            occurrence=0,
            offset=4,
            size=2,
            verify=False,
            inline_data=b"\x11\x22",
        )
    )
    device = FakeDevice(object_types={0: 0x0000, 1: _ADDRESS_TABLE_TYPE})
    device.table_references[1] = 0x4000
    runner = LoadProcedureRunner(
        application, DownloadImage(segments=(), properties=()), DeviceProgrammer(device)
    )

    await runner.run()

    # written at table base (0x4000) + offset (4)
    assert bytes(device.memory[0x4004 + i] for i in range(2)) == b"\x11\x22"


async def test_write_rel_mem_image_backed_uses_relative_lookup() -> None:
    # The image mirrors a relative segment in its own relative address space
    # (base 0x0); the device write adds the table base read at run time. Only the
    # masked bytes are written, at base + their relative offset.
    image = DownloadImage(
        segments=(
            MemorySegment(
                address=0x0,
                data=b"\x00\x00\xab\xcd",
                mask=b"\x00\x00\xff\xff",
            ),
        ),
        properties=(),
    )
    application = _application(
        LdCtrlWriteRelMem(
            obj_type=_ADDRESS_TABLE_TYPE,
            occurrence=0,
            offset=0,
            size=4,
            verify=False,
            inline_data=None,
        )
    )
    device = FakeDevice(object_types={0: 0x0000, 1: _ADDRESS_TABLE_TYPE})
    device.table_references[1] = 0x3804
    runner = LoadProcedureRunner(application, image, DeviceProgrammer(device))

    await runner.run()

    # relative offsets 2..3 written at table base 0x3804 + 2
    assert bytes(device.memory[0x3806 + i] for i in range(2)) == b"\xab\xcd"
    assert 0x3804 not in device.memory and 0x3805 not in device.memory


async def test_write_rel_mem_relative_segment_by_object_type() -> None:
    # A System B group communication table: the image holds it as a relative
    # segment keyed by object type, and the write lands at the table base.
    image = DownloadImage(
        segments=(),
        properties=(),
        relative_segments=(
            RelativeSegment(
                object_type=_ADDRESS_TABLE_TYPE,
                data=b"\x00\x02\x0b\x08",
                mask=b"\xff\xff\xff\xff",
            ),
        ),
    )
    application = _application(
        LdCtrlWriteRelMem(
            obj_type=_ADDRESS_TABLE_TYPE,
            occurrence=0,
            offset=0,
            size=4,
            verify=False,
            inline_data=None,
        )
    )
    device = FakeDevice(object_types={0: 0x0000, 1: _ADDRESS_TABLE_TYPE})
    device.table_references[1] = 0x3400
    runner = LoadProcedureRunner(application, image, DeviceProgrammer(device))

    await runner.run()

    assert bytes(device.memory[0x3400 + i] for i in range(4)) == b"\x00\x02\x0b\x08"


async def test_write_prop_inline_data() -> None:
    application = _application(
        LdCtrlWriteProp(
            obj_idx=5,
            prop_id=0x33,
            start_element=1,
            count=1,
            verify=False,
            inline_data=b"\xaa\xbb",
        )
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    writes = [p for p in device.sent if isinstance(p, PropertyValueWrite)]
    assert writes and writes[0].object_index == 5
    assert device.properties[(5, 0x33)] == b"\xaa\xbb"


async def test_write_prop_image_backed() -> None:
    image = DownloadImage(
        segments=(),
        properties=(
            PropertyValue(
                object_index=5, property_id=0x33, occurrence=0, data=b"\xca\xfe"
            ),
        ),
    )
    application = _application(
        LdCtrlWriteProp(
            obj_idx=5,
            prop_id=0x33,
            start_element=1,
            count=1,
            verify=False,
            inline_data=None,
        )
    )
    runner, device = _runner(application, image)

    await runner.run()

    assert device.properties[(5, 0x33)] == b"\xca\xfe"


async def test_compare_prop_tolerates_trailing_padding() -> None:
    from xknxmono.models.intermediate.ld_ctrl_compare_prop_t import LdCtrlCompareProp

    device = FakeDevice()
    device.properties[(0, 78)] = (
        b"\x00\x00\x00\x00\x02\x27"  # 6 bytes, as a real device reports
    )
    application = _application(
        LdCtrlCompareProp(
            obj_idx=0,
            prop_id=78,
            start_element=1,
            count=1,
            inline_data=b"\x00\x00\x00\x00\x02\x27\x00\x00\x00\x00",  # padded to 10
        )
    )
    runner = LoadProcedureRunner(
        application, DownloadImage(segments=(), properties=()), DeviceProgrammer(device)
    )
    await runner.run()  # must not raise: the 6 significant bytes match


async def test_compare_prop_detects_real_mismatch() -> None:
    from xknxmono.download.errors import VerificationError
    from xknxmono.models.intermediate.ld_ctrl_compare_prop_t import LdCtrlCompareProp

    device = FakeDevice()
    device.properties[(0, 78)] = b"\x00\x00\x00\x00\x09\x99"
    application = _application(
        LdCtrlCompareProp(
            obj_idx=0,
            prop_id=78,
            start_element=1,
            count=1,
            inline_data=b"\x00\x00\x00\x00\x02\x27",
        )
    )
    runner = LoadProcedureRunner(
        application, DownloadImage(segments=(), properties=()), DeviceProgrammer(device)
    )
    with pytest.raises(VerificationError, match="compare failed"):
        await runner.run()


async def test_compare_prop_mask_ignores_unmarked_octets() -> None:
    from xknxmono.models.intermediate.ld_ctrl_compare_prop_t import LdCtrlCompareProp

    device = FakeDevice()
    # application id: manufacturer 0x0002, app number 0xa062, version 0x14
    device.properties[(0, 13)] = b"\x00\x02\xa0\x62\x14"
    application = _application(
        LdCtrlCompareProp(
            obj_idx=0,
            prop_id=13,
            start_element=1,
            count=1,
            inline_data=b"\x00\x00\xa0\x62\x00",
            mask=b"\x00\x00\xff\xff\x00",  # only the app-number octets matter
        )
    )
    runner = LoadProcedureRunner(
        application, DownloadImage(segments=(), properties=()), DeviceProgrammer(device)
    )
    await runner.run()  # must not raise: manufacturer and version are masked out


async def test_compare_prop_mask_still_detects_marked_mismatch() -> None:
    from xknxmono.download.errors import VerificationError
    from xknxmono.models.intermediate.ld_ctrl_compare_prop_t import LdCtrlCompareProp

    device = FakeDevice()
    device.properties[(0, 13)] = b"\x00\x02\xa0\x63\x14"  # app number differs
    application = _application(
        LdCtrlCompareProp(
            obj_idx=0,
            prop_id=13,
            start_element=1,
            count=1,
            inline_data=b"\x00\x00\xa0\x62\x00",
            mask=b"\x00\x00\xff\xff\x00",
        )
    )
    runner = LoadProcedureRunner(
        application, DownloadImage(segments=(), properties=()), DeviceProgrammer(device)
    )
    with pytest.raises(VerificationError, match="compare failed"):
        await runner.run()


async def test_abs_segment_writes_image_data_for_its_range() -> None:
    image = DownloadImage(
        segments=(MemorySegment(address=0x4000, data=b"\x01\x02\x03\x04"),),
        properties=(),
    )
    application = _application(
        LdCtrlAbsSegment(
            obj_type=_ADDRESS_TABLE_TYPE,
            occurrence=0,
            seg_type=0,
            address=0x4000,
            size=4,
            access=0xFF,
            mem_type=3,
            seg_flags=0x80,
        )
    )
    runner, device = _runner(application, image)

    await runner.run()

    # segment allocated (LSM loading) and its image data written to memory
    assert device.load_states[1] == LoadState.LOADING
    assert bytes(device.memory[0x4000 + i] for i in range(4)) == b"\x01\x02\x03\x04"


async def test_abs_segment_without_image_only_allocates() -> None:
    application = _application(
        LdCtrlAbsSegment(
            obj_type=_ADDRESS_TABLE_TYPE,
            occurrence=0,
            seg_type=0,
            address=0x9000,
            size=4,
            access=0xFF,
            mem_type=3,
            seg_flags=0x80,
        )
    )
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert device.load_states[1] == LoadState.LOADING
    assert 0x9000 not in device.memory  # nothing written when image lacks the range


async def test_load_event_written_to_load_state_control() -> None:
    application = _application(LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0))
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    load_events = [
        p
        for p in device.sent
        if isinstance(p, PropertyValueWrite) and p.property_id == PID_LOAD_STATE_CONTROL
    ]
    assert load_events and load_events[0].data[0] == 0x01  # start loading


async def test_lsm_idx_addresses_object_directly() -> None:
    # For property based management LsmIdx is the interface object index.
    application = _application(LdCtrlLoad(lsm_idx=1, occurrence=0))
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert device.load_states[1] == LoadState.LOADING


async def test_connect_and_disconnect_are_noops() -> None:
    application = _application(LdCtrlConnect(), LdCtrlDisconnect())
    runner, device = _runner(application, DownloadImage(segments=(), properties=()))

    await runner.run()

    assert device.sent == []


_ASSOCIATION_TABLE_TYPE = 2
_APPLICATION_TYPE = 3


def _scoped_application() -> Application:
    # group communication parts (address=1, association=2) and the application
    # part (3); a partial download runs only the matching parts.
    return _application(
        LdCtrlLoad(obj_type=1, occurrence=0),
        LdCtrlLoad(obj_type=_ASSOCIATION_TABLE_TYPE, occurrence=0),
        LdCtrlLoad(obj_type=_APPLICATION_TYPE, occurrence=0),
    )


def _scoped_device() -> FakeDevice:
    return FakeDevice(object_types={0: 0x0000, 1: 1, 2: 2, 3: 3})


async def test_partial_parameters_scope_runs_only_application_part() -> None:
    device = _scoped_device()
    runner = LoadProcedureRunner(
        _scoped_application(),
        DownloadImage(segments=(), properties=()),
        DeviceProgrammer(device),
        scope=DownloadScope.PARAMETERS,
    )
    await runner.run()
    assert set(device.load_states) == {3}  # only the application part loaded


async def test_partial_group_scope_runs_only_table_parts() -> None:
    device = _scoped_device()
    runner = LoadProcedureRunner(
        _scoped_application(),
        DownloadImage(segments=(), properties=()),
        DeviceProgrammer(device),
        scope=DownloadScope.GROUP_COMMUNICATION,
    )
    await runner.run()
    assert set(device.load_states) == {1, 2}  # address + association tables


async def test_full_scope_runs_all_parts() -> None:
    device = _scoped_device()
    runner = LoadProcedureRunner(
        _scoped_application(),
        DownloadImage(segments=(), properties=()),
        DeviceProgrammer(device),
        scope=DownloadScope.FULL,
    )
    await runner.run()
    assert set(device.load_states) == {1, 2, 3}


class _FakeManager:
    """Connection manager handing out one fake device, counting open/close."""

    def __init__(self, device: FakeDevice) -> None:
        self.device = device
        self.opens = 0
        self.closes = 0

    async def open(self) -> FakeDevice:
        self.opens += 1
        return self.device

    async def close(self) -> None:
        self.closes += 1


def _managed_runner(
    *controls: object, **kwargs: object
) -> tuple[LoadProcedureRunner, _FakeManager]:
    device = FakeDevice(object_types={0: 0x0000, 1: _ADDRESS_TABLE_TYPE})
    manager = _FakeManager(device)
    runner = LoadProcedureRunner(
        _application(*controls),
        DownloadImage(segments=(), properties=()),
        connection_manager=manager,
        restart_cooldown=0,
        **kwargs,  # type: ignore[arg-type]
    )
    return runner, manager


async def test_connect_opens_and_disconnect_closes() -> None:
    runner, manager = _managed_runner(
        LdCtrlConnect(),
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        LdCtrlDisconnect(),
    )
    await runner.run()
    assert manager.opens == 1
    assert manager.closes == 1
    assert manager.device.load_states[1] == LoadState.LOADING


async def test_bus_control_auto_connects() -> None:
    runner, manager = _managed_runner(
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0)
    )
    await runner.run()
    assert manager.opens == 1  # opened automatically, no explicit Connect


async def test_restart_tears_down_and_next_control_reconnects() -> None:
    runner, manager = _managed_runner(
        LdCtrlConnect(),
        LdCtrlRestart(),
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
    )
    await runner.run()
    assert runner.restarted
    assert manager.device.restarted
    # opened for Connect, torn down by Restart, reopened for Load
    assert manager.opens == 2
    assert manager.closes >= 1


async def test_runner_requires_programmer_or_manager() -> None:
    with pytest.raises(DownloadError, match="programmer or a connection manager"):
        LoadProcedureRunner(_application(), DownloadImage(segments=(), properties=()))


async def test_expected_descriptor_mismatch_refuses_to_program() -> None:
    # Device reports mask 0x0705 (FakeDevice default); expecting System B 0x07B0.
    runner, manager = _managed_runner(
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        expected_descriptor=0x07B0,
    )
    with pytest.raises(DownloadError, match="device mask mismatch"):
        await runner.run()
    # It refused before driving the load state machine.
    assert manager.device.load_states == {}


async def test_expected_descriptor_match_proceeds() -> None:
    runner, manager = _managed_runner(
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        expected_descriptor=0x0705,
    )
    await runner.run()
    assert manager.device.load_states[1] == LoadState.LOADING


async def test_negotiate_apdu_uses_device_maximum() -> None:
    runner, manager = _managed_runner(
        LdCtrlLoad(obj_type=_ADDRESS_TABLE_TYPE, occurrence=0),
        max_apdu_length=254,
        negotiate_apdu=True,
    )
    # Device Object PID_MAX_APDU_LENGTH (56) reports 40 octets.
    manager.device.properties[(0, 56)] = (40).to_bytes(2, "big")

    await runner.run()

    # The device's maximum APDU length was read (negotiated) before programming.
    assert any(
        type(p).__name__ == "PropertyValueRead"
        and getattr(p, "object_index", None) == 0
        and getattr(p, "property_id", None) == 56
        for p in manager.device.sent
    )
