"""Tests for the files.vXX -> intermediate converter."""

from __future__ import annotations

import pytest

from xknxmono.models.adapters.convert import (
    Context,
    ConversionError,
    PuidAllocator,
    convert,
)
from xknxmono.models.files.v10.device_instance_t_additional_addresses import (
    DeviceInstanceAdditionalAddresses as V10AdditionalAddresses,
)
from xknxmono.models.files.v10.group_address_t import GroupAddress as V10GroupAddress
from xknxmono.models.files.v20.device_instance_t_binary_data_binary_data import (
    DeviceInstanceBinaryDataBinaryData as V20BinaryData,
)
from xknxmono.models.files.v20.group_address_t import GroupAddress as V20GroupAddress
from xknxmono.models.intermediate.device_instance_t_additional_addresses import (
    DeviceInstanceAdditionalAddresses as IRAdditionalAddresses,
)
from xknxmono.models.intermediate.device_instance_t_binary_data_binary_data import (
    DeviceInstanceBinaryDataBinaryData as IRBinaryData,
)
from xknxmono.models.intermediate.group_address_t import GroupAddress as IRGroupAddress


def v10() -> Context:
    return Context(version="v10")


# --- PuidAllocator --------------------------------------------------------

def test_puid_allocator_is_sequential():
    alloc = PuidAllocator()
    assert [alloc.allocate() for _ in range(3)] == [1, 2, 3]


# --- generic field copy ---------------------------------------------------

def test_copies_same_named_scalar_fields():
    src = V10GroupAddress(id="GA-1", address=42, name="Living", central=True)
    out = convert(src, IRGroupAddress, v10())
    assert out.id == "GA-1"
    assert out.address == 42
    assert out.name == "Living"
    assert out.central is True


def test_recurses_into_lists_of_dataclasses():
    src = V10AdditionalAddresses(address=[5, 7])
    out = convert(src, IRAdditionalAddresses, v10())
    assert [a.address for a in out.address] == [5, 7]
    assert all(isinstance(a, type(out.address[0])) for a in out.address)


# --- universal PUID synthesis --------------------------------------------

def test_synthesizes_puid_when_source_lacks_it():
    ctx = v10()
    a = convert(V10GroupAddress(id="GA-1", address=1, name="a"), IRGroupAddress, ctx)
    b = convert(V10GroupAddress(id="GA-2", address=2, name="b"), IRGroupAddress, ctx)
    assert (a.puid, b.puid) == (1, 2)  # sequential, fabricated


def test_preserves_existing_puid():
    src = V20GroupAddress(id="GA-1", address=1, name="a", puid=99)
    out = convert(src, IRGroupAddress, Context(version="v20"))
    assert out.puid == 99  # real PUID kept, not synthesized


# --- GroupAddress.DatapointType: list -> single ---------------------------

def test_datapoint_type_single_entry():
    src = V10GroupAddress(id="GA-1", address=1, name="a", datapoint_type=["DPST-1-1"])
    out = convert(src, IRGroupAddress, v10())
    assert out.datapoint_type == "DPST-1-1"


def test_datapoint_type_empty_becomes_none():
    src = V10GroupAddress(id="GA-1", address=1, name="a", datapoint_type=[])
    out = convert(src, IRGroupAddress, v10())
    assert out.datapoint_type is None


def test_datapoint_type_multiple_rejected():
    src = V10GroupAddress(id="GA-1", address=1, name="a", datapoint_type=["DPST-1-1", "DPST-5-1"])
    with pytest.raises(ConversionError, match="DatapointType"):
        convert(src, IRGroupAddress, v10())


# --- AdditionalAddresses: text ints -> Address objects --------------------

def test_additional_addresses_wraps_ints():
    out = convert(V10AdditionalAddresses(address=[1, 255]), IRAdditionalAddresses, v10())
    assert [a.address for a in out.address] == [1, 255]


def test_additional_addresses_empty():
    out = convert(V10AdditionalAddresses(address=[]), IRAdditionalAddresses, v10())
    assert out.address == []


# --- BinaryData: AutoCopy -> DoNotCopy (inverted) -------------------------

def test_auto_copy_inverts_to_do_not_copy():
    out = convert(V20BinaryData(auto_copy=False), IRBinaryData, Context(version="v20"))
    assert out.do_not_copy is True  # not False

    out = convert(V20BinaryData(auto_copy=True), IRBinaryData, Context(version="v20"))
    assert out.do_not_copy is False  # not True


# --- AddInData/AddInId casing: v10 capital-'In' -> v12+ lowercase (via aliases) -----

def test_addin_id_casing_aliased():
    from xknxmono.models.files.v10.addin_data_t import AddinData as V10AddinData
    from xknxmono.models.intermediate.addin_data_t import AddinData as IRAddinData

    src = V10AddinData(add_in_id="{0815-GUID}", name="vendor.addin")
    out = convert(src, IRAddinData, v10())
    assert out.addin_id == "{0815-GUID}"  # add_in_id -> addin_id, GUID string copied as-is
    assert out.name == "vendor.addin"


def test_project_addin_data_casing_aliased():
    from xknxmono.models.files.v10.addin_data_t import AddinData as V10AddinData
    from xknxmono.models.files.v10.project_t_add_in_data import ProjectAddInData as V10ProjectAddInData
    from xknxmono.models.intermediate.project_t_addin_data import ProjectAddinData as IRProjectAddinData

    src = V10ProjectAddInData(add_in_data=[V10AddinData(add_in_id="g1", name="a")])
    out = convert(src, IRProjectAddinData, v10())
    assert [a.addin_id for a in out.addin_data] == ["g1"]  # nested rename + recursion


# --- MulticastTTL relocation: v10/v11 Topology>Line -> v14+ Installation -----------

def test_multicast_ttl_relocated_from_line():
    """v11 stored MulticastTTL on the line; the unified model has it on the installation."""
    from types import SimpleNamespace as NS

    from xknxmono.models.adapters.convert import _installation

    src = NS(multicast_ttl=None, topology=NS(area=[NS(line=[NS(multicast_ttl=8)])]))
    assert _installation(src, v10()) == {"multicast_ttl": 8}


def test_multicast_ttl_kept_when_on_installation():
    """v14+ already have it at installation level — leave it for the generic copy."""
    from types import SimpleNamespace as NS

    from xknxmono.models.adapters.convert import _installation

    src = NS(multicast_ttl=4, topology=NS(area=[]))
    assert _installation(src, Context(version="v20")) == {}


# --- Baggage: legacy fields retained as a superset in the IR -----------------------

def _ir_baggage():
    from xknxmono.models.intermediate.manufacturer_data_t_manufacturer_baggages_baggage import (
        ManufacturerDataManufacturerBaggagesBaggage,
    )
    return ManufacturerDataManufacturerBaggagesBaggage


def test_baggage_v11_legacy_fields_copied():
    from xknxmono.models.files.v11.manufacturer_data_t_manufacturer_baggages_baggage import (
        ManufacturerDataManufacturerBaggagesBaggage as V11Baggage,
    )
    from xknxmono.models.files.v11.manufacturer_data_t_manufacturer_baggages_baggage_file_info import (
        ManufacturerDataManufacturerBaggagesBaggageFileInfo as V11FileInfo,
    )

    src = V11Baggage(
        file_info=V11FileInfo(), target_path="x/y", name="b", id="B-1",
        install_on_import=False, data=b"payload", group_addresses16_bit_enabled=False,
    )
    out = convert(src, _ir_baggage(), Context(version="v11"))
    assert out.install_on_import is False       # real value copied
    assert out.data == b"payload"               # inline Data preserved
    assert out.group_addresses16_bit_enabled is False


def test_baggage_v23_defaults_for_missing_legacy_fields():
    from xknxmono.models.files.v23.manufacturer_data_t_manufacturer_baggages_baggage import (
        ManufacturerDataManufacturerBaggagesBaggage as V23Baggage,
    )
    from xknxmono.models.files.v23.manufacturer_data_t_manufacturer_baggages_baggage_file_info import (
        ManufacturerDataManufacturerBaggagesBaggageFileInfo as V23FileInfo,
    )

    src = V23Baggage(file_info=V23FileInfo(), target_path="x/y", name="b", id="B-1", file_integrity="DEADBEEF")
    out = convert(src, _ir_baggage(), Context(version="v23"))
    assert out.install_on_import is True            # IR default for versions lacking it
    assert out.group_addresses16_bit_enabled is True
    assert out.file_integrity == "DEADBEEF"
    assert out.data is None


# --- Line -> Segment upgrade: flat pre-v21 line wraps into one Segment --------------

def test_flat_line_wraps_into_segment():
    from xknxmono.models.files.v11.topology_t_area_line import TopologyAreaLine as V11Line
    from xknxmono.models.intermediate.topology_t_area_line import TopologyAreaLine as IRLine

    src = V11Line(id="L-1", name="Main", address=1, medium_type_ref_id="MT-1", domain_address=42)
    out = convert(src, IRLine, Context(version="v11"))

    # line-level attrs stay on the line
    assert out.id == "L-1" and out.name == "Main" and out.address == 1
    # medium attrs moved into a single synthesized segment
    assert len(out.segment) == 1
    seg = out.segment[0]
    assert seg.medium_type_ref_id == "MT-1"
    assert seg.domain_address == 42
    assert seg.id == "L-1-S1"          # derived, distinct from the line's Id
    assert seg.number == 1
    # the IR line no longer has a direct device home (clean v23 shape)
    assert not hasattr(out, "device_instance")


def test_segmented_line_passes_through():
    from xknxmono.models.adapters.convert import _line
    from types import SimpleNamespace as NS

    src = NS(segment=["already-here"])
    assert _line(src, Context(version="v23")) == {}  # v21+ untouched


# --- v13->v14: HorizontalRuler bool -> UIHint enum ---------------------------------

def test_horizontal_ruler_maps_to_uihint():
    from xknxmono.models.files.v13.parameter_separator_t import ParameterSeparator as V13Sep
    from xknxmono.models.intermediate.parameter_separator_t import ParameterSeparator as IRSep
    from xknxmono.models.intermediate.parameter_separator_t_uihint import ParameterSeparatorUihint

    out = convert(V13Sep(id="S-1", text="t", horizontal_ruler=True), IRSep, Context(version="v13"))
    assert out.uihint is ParameterSeparatorUihint.HORIZONTAL_RULER

    out = convert(V13Sep(id="S-2", text="t", horizontal_ruler=False), IRSep, Context(version="v13"))
    assert out.uihint is None


# --- v13->v14: Buildings/BuildingPart -> Locations/Space (aliases) -----------------

def test_building_part_aliases_to_space():
    from xknxmono.models.files.v13.building_part_t import BuildingPart as V13BuildingPart
    from xknxmono.models.files.v13.locations_t import Locations as V13Locations
    from xknxmono.models.intermediate.locations_t import Locations as IRLocations

    src = V13Locations(building_part=[V13BuildingPart(id="B-1", name="House", type_value="x", puid=7)])
    out = convert(src, IRLocations, Context(version="v13"))
    assert [s.id for s in out.space] == ["B-1"]          # BuildingPart -> Space
    assert out.space[0].name == "House"


# --- v13->v14: loaded credential -> hash (fake, must raise) ------------------------

def test_loaded_credential_hash_raises():
    from xknxmono.models.files.v13.security_t import Security as V13Security
    from xknxmono.models.intermediate.security_t import Security as IRSecurity
    from xknxmono.models.adapters.convert import fake_hash

    src = V13Security(loaded_device_authentication_code="s3cr3t")
    with pytest.raises(NotImplementedError, match="hashing algorithm unknown"):
        convert(src, IRSecurity, Context(version="v13"))

    # but a security record without loaded plaintext converts fine
    out = convert(V13Security(), IRSecurity, Context(version="v13"))
    assert out.loaded_device_authentication_code_hash is None

    with pytest.raises(NotImplementedError):
        fake_hash("anything")
