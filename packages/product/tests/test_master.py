"""Unit tests for MasterData's medium_types/manufacturers id->name maps."""

from __future__ import annotations

from xknxmono.models.intermediate import MasterData as IrMasterData
from xknxmono.models.intermediate import (
    MasterDataManufacturers,
    MasterDataMediumTypes,
)
from xknxmono.models.intermediate.master_data_t_manufacturers_manufacturer import (
    MasterDataManufacturersManufacturer,
)
from xknxmono.models.intermediate.master_data_t_medium_types_medium_type import (
    MasterDataMediumTypesMediumType,
)
from xknxmono.product.master import MasterData


def test_medium_types_raw_none_is_empty() -> None:
    assert MasterData(raw=None).medium_types == {}


def test_medium_types_holder_none_is_empty() -> None:
    raw = IrMasterData(
        version=20,
        signature=b"",
        id="MASTER",
        medium_types=None,
    )
    assert MasterData(raw=raw).medium_types == {}


def test_medium_types_uses_name_or_falls_back_to_text_then_id() -> None:
    raw = IrMasterData(
        version=20,
        signature=b"",
        id="MASTER",
        medium_types=MasterDataMediumTypes(
            medium_type=[
                MasterDataMediumTypesMediumType(
                    id="MT-1", number=1, name="TP", domain_address_length=2
                ),
                MasterDataMediumTypesMediumType(
                    id="MT-2",
                    number=2,
                    name="",
                    text="RF Medium",
                    domain_address_length=6,
                ),
            ]
        ),
    )
    md = MasterData(raw=raw)
    assert md.medium_types == {"MT-1": "TP", "MT-2": "RF Medium"}
    assert md.medium_types is md.medium_types  # cached


def test_manufacturers_raw_none_is_empty() -> None:
    assert MasterData(raw=None).manufacturers == {}


def test_manufacturers_holder_none_is_empty() -> None:
    raw = IrMasterData(version=20, signature=b"", id="MASTER", manufacturers=None)
    assert MasterData(raw=raw).manufacturers == {}


def test_manufacturers_maps_id_to_name() -> None:
    raw = IrMasterData(
        version=20,
        signature=b"",
        id="MASTER",
        manufacturers=MasterDataManufacturers(
            manufacturer=[
                MasterDataManufacturersManufacturer(
                    id="M-0008", name="Gira", knx_manufacturer_id=8
                )
            ]
        ),
    )
    md = MasterData(raw=raw)
    assert md.manufacturers == {"M-0008": "Gira"}
    assert md.manufacturers is md.manufacturers  # cached
