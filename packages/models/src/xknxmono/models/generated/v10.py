from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "http://knx.org/xml/project/10"


class AccessT(Enum):
    NONE = "None"
    READ = "Read"
    READ_WRITE = "ReadWrite"


@dataclass(slots=True, kw_only=True)
class AddInDataT:
    class Meta:
        name = "AddInData_t"

    add_in_id: str = field(
        metadata={
            "name": "AddInId",
            "type": "Attribute",
            "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )


class ApplicationProgramIpconfigT(Enum):
    CUSTOM = "Custom"
    TOOL = "Tool"


@dataclass(slots=True, kw_only=True)
class ApplicationProgramRefT:
    """
    :ivar ref_id: registration-relevant
    """

    class Meta:
        name = "ApplicationProgramRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTAddressTable:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar max_entries: registration-relevant
    """

    class Meta:
        global_type = False

    code_segment: None | str = field(
        default=None,
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        },
    )
    offset: None | int = field(
        default=None,
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        },
    )
    max_entries: int = field(
        metadata={
            "name": "MaxEntries",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTAssociationTable:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar max_entries: registration-relevant
    """

    class Meta:
        global_type = False

    code_segment: None | str = field(
        default=None,
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        },
    )
    offset: None | int = field(
        default=None,
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        },
    )
    max_entries: int = field(
        metadata={
            "name": "MaxEntries",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTCodeRelativeSegment:
    """
    :ivar data: registration-relevant
    :ivar mask: registration-relevant
    :ivar id: registration-relevant
    :ivar name:
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    :ivar load_state_machine: registration-relevant
    """

    class Meta:
        global_type = False

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    mask: None | bytes = field(
        default=None,
        metadata={
            "name": "Mask",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    load_state_machine: int = field(
        metadata={
            "name": "LoadStateMachine",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTDeviceCompareExcludeMemory:
    class Meta:
        global_type = False

    code_segment: str = field(
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTDeviceCompareExcludeProperty:
    class Meta:
        global_type = False

    object_index: None | int = field(
        default=None,
        metadata={
            "name": "ObjectIndex",
            "type": "Attribute",
        },
    )
    object_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjectType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    property_id: int = field(
        metadata={
            "name": "PropertyId",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTExtensionBaggage:
    class Meta:
        global_type = False

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class ApplicationProgramStaticTOptionsParameterByteOrder(Enum):
    BIG_ENDIAN = "BigEndian"
    LITTLE_ENDIAN = "LittleEndian"


class ApplicationProgramStaticTOptionsTextParameterEncoding(Enum):
    US_ASCII = "us-ascii"
    ISO_8859_1 = "iso-8859-1"
    ISO_8859_2 = "iso-8859-2"
    ISO_8859_3 = "iso-8859-3"
    ISO_8859_4 = "iso-8859-4"
    ISO_8859_5 = "iso-8859-5"
    ISO_8859_6 = "iso-8859-6"
    ISO_8859_7 = "iso-8859-7"
    ISO_8859_8 = "iso-8859-8"
    ISO_8859_9 = "iso-8859-9"
    ISO_8859_10 = "iso-8859-10"
    ISO_8859_13 = "iso-8859-13"
    ISO_8859_15 = "iso-8859-15"
    UTF_8 = "utf-8"


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParametersUnionMemory:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        global_type = False

    code_segment: str = field(
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    bit_offset: int = field(
        metadata={
            "name": "BitOffset",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 7,
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParametersUnionProperty:
    """
    :ivar object_index: registration-relevant
    :ivar object_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar property_id: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        global_type = False

    object_index: None | int = field(
        default=None,
        metadata={
            "name": "ObjectIndex",
            "type": "Attribute",
        },
    )
    object_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjectType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    property_id: int = field(
        metadata={
            "name": "PropertyId",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    bit_offset: int = field(
        metadata={
            "name": "BitOffset",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 7,
        }
    )


class ApplicationProgramTypeT(Enum):
    APPLICATION_PROGRAM = "ApplicationProgram"
    PEI_PROGRAM = "PeiProgram"


class ApplicationProgramTMinEtsVersion(Enum):
    VALUE_3_0 = "3.0"
    VALUE_3_0D = "3.0d"
    VALUE_3_0F = "3.0f"
    VALUE_4_0 = "4.0"


@dataclass(slots=True, kw_only=True)
class AssignT:
    """
    :ivar target_param_ref_ref: registration-relevant
    :ivar source_param_ref_ref: registration-relevant
    :ivar value: registration-relevant
    """

    class Meta:
        name = "Assign_t"

    target_param_ref_ref: str = field(
        metadata={
            "name": "TargetParamRefRef",
            "type": "Attribute",
        }
    )
    source_param_ref_ref: None | str = field(
        default=None,
        metadata={
            "name": "SourceParamRefRef",
            "type": "Attribute",
        },
    )
    value: None | str = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class BinaryDataRefT:
    """
    :ivar data: registration-relevant
    :ivar ref_id: registration-relevant
    """

    class Meta:
        name = "BinaryDataRef_t"

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class BinaryDataT:
    class Meta:
        name = "BinaryData_t"

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )


class BuildingPartTypeT(Enum):
    BUILDING = "Building"
    BUILDING_PART = "BuildingPart"
    FLOOR = "Floor"
    ROOM = "Room"
    DISTRIBUTION_BOARD = "DistributionBoard"
    STAIRWAY = "Stairway"
    CORRIDOR = "Corridor"


@dataclass(slots=True, kw_only=True)
class BusAccessT:
    class Meta:
        name = "BusAccess_t"

    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    edi: str = field(
        metadata={
            "name": "Edi",
            "type": "Attribute",
            "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        }
    )
    parameter: str = field(
        metadata={
            "name": "Parameter",
            "type": "Attribute",
        }
    )


class CapabilityT(Enum):
    ADD_DELETE_DEVICE = "AddDeleteDevice"
    GROUP_COMMUNICATION_EVENTS = "GroupCommunicationEvents"
    GROUP_COMMUNICATION_LIMITS = "GroupCommunicationLimits"
    TRANSFER_PARAMETERS = "TransferParameters"
    PROJECT_CHECK = "ProjectCheck"
    PRINTING = "Printing"


@dataclass(slots=True, kw_only=True)
class CatalogSectionTCatalogItem:
    class Meta:
        global_type = False

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    product_ref_id: str = field(
        metadata={
            "name": "ProductRefId",
            "type": "Attribute",
        }
    )
    hardware2_program_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "Hardware2ProgramRefId",
            "type": "Attribute",
        },
    )
    default_language: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLanguage",
            "type": "Attribute",
        },
    )
    medium_types: list[str] = field(
        default_factory=list,
        metadata={
            "name": "MediumTypes",
            "type": "Attribute",
            "tokens": True,
        },
    )
    non_reg_relevant_data_version: int = field(
        default=0,
        metadata={
            "name": "NonRegRelevantDataVersion",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ChannelChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "ChannelChoose_t"

    when: list[ChannelChooseTWhen] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefTConnectorsReceive:
    class Meta:
        global_type = False

    group_address_ref_id: str = field(
        metadata={
            "name": "GroupAddressRefId",
            "type": "Attribute",
        }
    )
    acknowledge: bool = field(
        default=False,
        metadata={
            "name": "Acknowledge",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefTConnectorsSend:
    class Meta:
        global_type = False

    group_address_ref_id: str = field(
        metadata={
            "name": "GroupAddressRefId",
            "type": "Attribute",
        }
    )
    acknowledge: bool = field(
        default=False,
        metadata={
            "name": "Acknowledge",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "ComObjectParameterChoose_t"

    when: list[ComObjectParameterChooseTWhen] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )


class ComObjectPriorityT(Enum):
    LOW = "Low"
    HIGH = "High"
    ALERT = "Alert"


@dataclass(slots=True, kw_only=True)
class ComObjectRefRefT:
    """
    :ivar ref_id: registration-relevant
    """

    class Meta:
        name = "ComObjectRefRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class ComObjectSizeT(Enum):
    VALUE_1_BIT = "1 Bit"
    VALUE_2_BIT = "2 Bit"
    VALUE_3_BIT = "3 Bit"
    VALUE_4_BIT = "4 Bit"
    VALUE_5_BIT = "5 Bit"
    VALUE_6_BIT = "6 Bit"
    VALUE_7_BIT = "7 Bit"
    VALUE_1_BYTE = "1 Byte"
    VALUE_2_BYTES = "2 Bytes"
    VALUE_3_BYTES = "3 Bytes"
    VALUE_4_BYTES = "4 Bytes"
    VALUE_5_BYTES = "5 Bytes"
    VALUE_6_BYTES = "6 Bytes"
    VALUE_7_BYTES = "7 Bytes"
    VALUE_8_BYTES = "8 Bytes"
    VALUE_9_BYTES = "9 Bytes"
    VALUE_10_BYTES = "10 Bytes"
    VALUE_11_BYTES = "11 Bytes"
    VALUE_12_BYTES = "12 Bytes"
    VALUE_14_BYTES = "14 Bytes"
    LEGACY_VAR_DATA = "LegacyVarData"


class CompletionStatusT(Enum):
    UNDEFINED = "Undefined"
    EDITING = "Editing"
    FINISHED_DESIGN = "FinishedDesign"
    FINISHED_COMMISSIONING = "FinishedCommissioning"
    TESTED = "Tested"
    ACCEPTED = "Accepted"


@dataclass(slots=True, kw_only=True)
class DependentChannelChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "DependentChannelChoose_t"

    when: list[DependentChannelChooseTWhen] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceRefT:
    class Meta:
        name = "DeviceInstanceRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceTAdditionalAddresses:
    class Meta:
        global_type = False

    address: list[int] = field(
        default_factory=list,
        metadata={
            "name": "Address",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
            "max_occurs": 254,
            "min_inclusive": 1,
            "max_inclusive": 255,
        },
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceTBinaryDataBinaryData:
    class Meta:
        global_type = False

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    ref_id: None | str = field(
        default=None,
        metadata={
            "name": "RefId",
            "type": "Attribute",
        },
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )


class EnableT(Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"


@dataclass(slots=True, kw_only=True)
class FixupT:
    """
    :ivar offset: registration-relevant set
    :ivar function_ref: registration-relevant
    :ivar code_segment: registration-relevant
    """

    class Meta:
        name = "Fixup_t"

    offset: list[int] = field(
        default_factory=list,
        metadata={
            "name": "Offset",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
            "max_inclusive": 65535,
        },
    )
    function_ref: str = field(
        metadata={
            "name": "FunctionRef",
            "type": "Attribute",
        }
    )
    code_segment: str = field(
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        }
    )


class GroupAddressStyleT(Enum):
    TWO_LEVEL = "TwoLevel"
    THREE_LEVEL = "ThreeLevel"
    FREE = "Free"


@dataclass(slots=True, kw_only=True)
class GroupAddressT:
    class Meta:
        name = "GroupAddress_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 65535,
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    unfiltered: bool = field(
        default=False,
        metadata={
            "name": "Unfiltered",
            "type": "Attribute",
        },
    )
    central: bool = field(
        default=False,
        metadata={
            "name": "Central",
            "type": "Attribute",
        },
    )
    global_value: bool = field(
        default=False,
        metadata={
            "name": "Global",
            "type": "Attribute",
        },
    )
    datapoint_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DatapointType",
            "type": "Attribute",
            "tokens": True,
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )


class HardwareTProductsProductAttributesAttributeName(Enum):
    CATALOG_NAME = "CatalogName"
    SERIES = "Series"
    COLOUR = "Colour"


@dataclass(slots=True, kw_only=True)
class HardwareTProductsProductBaggagesBaggage:
    class Meta:
        global_type = False

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class HawkConfigurationDataTFeaturesFeatureName(Enum):
    PARAMETER_BYTE_ORDER = "ParameterByteOrder"
    FIRST_APP_OBJECT_IDX = "FirstAppObjectIdx"
    MAX_INDIVIDUAL_ADDRESS = "MaxIndividualAddress"
    MAX_GROUP_ADDRESS = "MaxGroupAddress"
    POLLING_GROUP_SUPPORT = "PollingGroupSupport"
    AUTHORIZE_LEVELS = "AuthorizeLevels"
    RESTART_TIME = "RestartTime"
    UNLOADED_INDIVIDUAL_ADDRESS = "UnloadedIndividualAddress"
    ASSOCIATION_TABLE_FLAVOUR = "AssociationTableFlavour"
    VERIFY_MODE = "VerifyMode"
    MGMT_CONN_TYPES = "MgmtConnTypes"
    PROPERTY_MAPPED_LSMS = "PropertyMappedLsms"
    ALLOC_EXTRA_BYTE = "AllocExtraByte"
    MASKDATA_VERSION = "MaskdataVersion"
    DOWNLOAD_STAMP = "DownloadStamp"
    GROUP_OBJECT_TABLE_FLAVOUR = "GroupObjectTableFlavour"


class HawkConfigurationDataTProceduresProcedureValue(Enum):
    AP1 = "ap1"
    CFG = "cfg"


class HawkConfigurationDataTResourcesResourceResourceTypeFlavour(Enum):
    BYTE_ORDER_BIG_ENDIAN = "ByteOrder_BigEndian"
    BYTE_ORDER_LITTLE_ENDIAN = "ByteOrder_LittleEndian"
    MANAGEMENT_STYLE_BCU2 = "ManagementStyle_Bcu2"
    PTR_STANDARD_MEMORY = "Ptr_StandardMemory"
    PTR_STANDARD_MEMORY100 = "Ptr_StandardMemory100"
    ADDRESS_TABLE_BCU1 = "AddressTable_Bcu1"
    ADDRESS_TABLE_BCU1_PL = "AddressTable_Bcu1PL"
    ADDRESS_TABLE_SYSTEM_B = "AddressTable_SystemB"
    ASSOCIATION_TABLE_BCU1 = "AssociationTable_Bcu1"
    ASSOCIATION_TABLE_BCU2 = "AssociationTable_Bcu2"
    ASSOCIATION_TABLE_M112 = "AssociationTable_M112"
    ASSOCIATION_TABLE_SYSTEM_B = "AssociationTable_SystemB"
    ASSOCIATION_TABLE_SYSTEM_BSMALL = "AssociationTable_SystemBSmall"
    ASSOCIATION_TABLE_SYSTEM_BBIG = "AssociationTable_SystemBBig"
    GROUP_OBJECT_TABLE_BCU10 = "GroupObjectTable_Bcu10"
    GROUP_OBJECT_TABLE_BCU11 = "GroupObjectTable_Bcu11"
    GROUP_OBJECT_TABLE_BCU1_PL = "GroupObjectTable_Bcu1PL"
    GROUP_OBJECT_TABLE_BCU2 = "GroupObjectTable_Bcu2"
    GROUP_OBJECT_TABLE_M112 = "GroupObjectTable_M112"
    GROUP_OBJECT_TABLE_SYSTEM_B = "GroupObjectTable_SystemB"
    GROUP_OBJECT_TABLE_SYSTEM300 = "GroupObjectTable_System300"
    LOAD_CONTROL_BCU2 = "LoadControl_Bcu2"
    LOAD_CONTROL_M112 = "LoadControl_M112"
    RUN_CONTROL_BCU2 = "RunControl_Bcu2"
    RUN_CONTROL_M112 = "RunControl_M112"
    RUN_CONTROL_BCU1 = "RunControl_Bcu1"
    VOLTAGE_ADC = "Voltage_Adc"
    PEI_TYPE_PROP = "PeiType_Prop"
    PEI_TYPE_ADC = "PeiType_Adc"
    RE_CONFIG_BCU1_PL = "ReConfig_Bcu1PL"
    FREQUENCY_CHANNEL_BCU1_PL = "FrequencyChannel_Bcu1PL"
    SENSITIVITY_BCU1_PL = "Sensitivity_Bcu1PL"
    RUNERROR_BCU1 = "Runerror_Bcu1"
    PROGRAMMING_MODE_BCU1 = "ProgrammingMode_Bcu1"
    PROGRAMMING_MODE_PROP = "ProgrammingMode_Prop"
    LC_10 = "Lc_10"
    LC_11 = "Lc_11"
    HARDWARE_CONFIG_IDENTICAL = "HardwareConfig_Identical"
    HARDWARE_CONFIG_VERSION = "HardwareConfig_Version"
    STAMP_SYSTEM_B = "Stamp_SystemB"


class IpconfigAssignT(Enum):
    FIXED = "Fixed"
    AUTO = "Auto"


@dataclass(slots=True, kw_only=True)
class IndependentParameterBlockChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "IndependentParameterBlockChoose_t"

    when: list[IndependentParameterBlockChooseTWhen] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LanguageDataTTranslationUnitTranslationElementTranslation:
    class Meta:
        global_type = False

    attribute_name: str = field(
        metadata={
            "name": "AttributeName",
            "type": "Attribute",
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
        }
    )


class LdCtrlControlVariableT(Enum):
    ENABLE_SEGMENT_WRITE = "EnableSegmentWrite"
    ENABLE_VERIFY_ON_WRITE_DIRECT = "EnableVerifyOnWriteDirect"
    ENABLE_OPTIMISTIC_WRITE = "EnableOptimisticWrite"
    ENABLE_MEMORY_AUTO_VERIFY = "EnableMemoryAutoVerify"


class LdCtrlMemAddrSpaceT(Enum):
    STANDARD = "Standard"
    USER = "User"
    LC_SLAVE = "LcSlave"
    LC_FILTER = "LcFilter"


class LdCtrlProcTypeT(Enum):
    FULL = "full"
    PAR = "par"
    GRP = "grp"
    FULL_PAR = "full,par"
    FULL_GRP = "full,grp"
    PAR_GRP = "par,grp"
    ALL = "all"
    AUTO = "auto"


class LoadProcedureStyleT(Enum):
    DEFAULT_PROCEDURE = "DefaultProcedure"
    PRODUCT_PROCEDURE = "ProductProcedure"
    MERGED_PROCEDURE = "MergedProcedure"


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlMerge:
    """
    :ivar merge_id: registration-relevant
    """

    class Meta:
        global_type = False

    merge_id: int = field(
        metadata={
            "name": "MergeId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerBaggagesBaggageFileInfo:
    class Meta:
        global_type = False

    version: None | str = field(
        default=None,
        metadata={
            "name": "Version",
            "type": "Attribute",
            "pattern": r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+",
        },
    )
    time_info: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "TimeInfo",
            "type": "Attribute",
        },
    )
    hidden: bool = field(
        default=False,
        metadata={
            "name": "Hidden",
            "type": "Attribute",
        },
    )
    read_only: bool = field(
        default=False,
        metadata={
            "name": "ReadOnly",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class MaskVersionTDownwardCompatibleMasksDownwardCompatibleMask:
    class Meta:
        global_type = False

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class MaskVersionTManagementModel(Enum):
    NONE = "None"
    BCU1 = "Bcu1"
    BIM_M112 = "BimM112"
    BCU2 = "Bcu2"
    PROPERTY_BASED = "PropertyBased"
    SYSTEM_B = "SystemB"


@dataclass(slots=True, kw_only=True)
class MaskVersionTMaskEntriesMaskEntry:
    class Meta:
        global_type = False

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTDatapointTypesDatapointTypeDatapointSubtypesDatapointSubtype:
    class Meta:
        global_type = False

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTManufacturersManufacturer:
    class Meta:
        global_type = False

    order_number_formatting_script: None | str = field(
        default=None,
        metadata={
            "name": "OrderNumberFormattingScript",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    knx_manufacturer_id: int = field(
        metadata={
            "name": "KnxManufacturerId",
            "type": "Attribute",
        }
    )
    default_language: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLanguage",
            "type": "Attribute",
        },
    )
    compatibility_group: None | int = field(
        default=None,
        metadata={
            "name": "CompatibilityGroup",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTMediumTypesMediumType:
    class Meta:
        global_type = False

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 20,
        }
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    domain_address_length: int = field(
        metadata={
            "name": "DomainAddressLength",
            "type": "Attribute",
        }
    )


class MemoryTypeT(Enum):
    RAM = "RAM"
    EEPROM = "EEPROM"
    FLASH = "FLASH"


@dataclass(slots=True, kw_only=True)
class ParameterBlockRenameT:
    """
    :ivar id: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar text:
    """

    class Meta:
        name = "ParameterBlockRename_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )


class ParameterCalculationTLanguage(Enum):
    VBSCRIPT = "VBScript"
    JAVA_SCRIPT = "JavaScript"


@dataclass(slots=True, kw_only=True)
class ParameterChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "ParameterChoose_t"

    when: list[ParameterChooseTWhen] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterInstanceRefT:
    class Meta:
        name = "ParameterInstanceRef_t"

    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    value: None | str = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterRefRefT:
    """
    :ivar ref_id: registration-relevant
    """

    class Meta:
        name = "ParameterRefRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class ParameterTypeTTypeDateEncoding(Enum):
    DPT_11 = "DPT 11"


class ParameterTypeTTypeFloatEncoding(Enum):
    DPT_9 = "DPT 9"
    IEEE_754_SINGLE = "IEEE-754 Single"
    IEEE_754_DOUBLE = "IEEE-754 Double"


class ParameterTypeTTypeFloatUihint(Enum):
    SLIDER = "Slider"


class ParameterTypeTTypeIpaddressAddressType(Enum):
    HOST_ADDRESS = "HostAddress"
    GATEWAY_ADDRESS = "GatewayAddress"
    UNICAST_ADDRESS = "UnicastAddress"
    BROADCAST_ADDRESS = "BroadcastAddress"
    MULTICAST_ADDRESS = "MulticastAddress"
    SUBNET_MASK = "SubnetMask"


class ParameterTypeTTypeIpaddressVersion(Enum):
    IPV4 = "IPv4"
    IPV6 = "IPv6"


class ParameterTypeTTypeNumberType(Enum):
    SIGNED_INT = "signedInt"
    UNSIGNED_INT = "unsignedInt"


class ParameterTypeTTypeNumberUihint(Enum):
    SLIDER = "Slider"
    CHECK_BOX = "CheckBox"


class ParameterTypeTTypeRestrictionBase(Enum):
    VALUE = "Value"
    BINARY_VALUE = "BinaryValue"


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeRestrictionEnumeration:
    """
    :ivar text:
    :ivar value: registration-relevant
    :ivar id: registration-relevant
    :ivar display_order:
    :ivar binary_value: registration-relevant
    """

    class Meta:
        global_type = False

    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    value: int = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    display_order: None | int = field(
        default=None,
        metadata={
            "name": "DisplayOrder",
            "type": "Attribute",
        },
    )
    binary_value: None | bytes = field(
        default=None,
        metadata={
            "name": "BinaryValue",
            "type": "Attribute",
            "format": "base64",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeText:
    """
    :ivar size_in_bit: registration-relevant
    :ivar pattern:
    """

    class Meta:
        global_type = False

    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
            "min_inclusive": 8,
            "max_inclusive": 1048575,
        }
    )
    pattern: None | str = field(
        default=None,
        metadata={
            "name": "Pattern",
            "type": "Attribute",
        },
    )


class ParameterTypeTTypeTimeUihint(Enum):
    TIME_HHMM = "Time_hhmm"
    TIME_HHMMSS = "Time_hhmmss"
    TIME_HHMMSSF = "Time_hhmmssf"
    TIME_HHMMSSFF = "Time_hhmmssff"
    TIME_HHMMSSFFF = "Time_hhmmssfff"
    DURATION_HHMM = "Duration_hhmm"
    DURATION_HHMMSS = "Duration_hhmmss"
    DURATION_HHMMSSF = "Duration_hhmmssf"
    DURATION_HHMMSSFF = "Duration_hhmmssff"
    DURATION_HHMMSSFFF = "Duration_hhmmssfff"


class ParameterTypeTTypeTimeUnit(Enum):
    HOURS = "Hours"
    MINUTES = "Minutes"
    SECONDS = "Seconds"
    HUNDRED_MILLISECONDS = "HundredMilliseconds"
    TEN_MILLISECONDS = "TenMilliseconds"
    MILLISECONDS = "Milliseconds"


@dataclass(slots=True, kw_only=True)
class ParameterTMemory:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        global_type = False

    code_segment: str = field(
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    bit_offset: int = field(
        metadata={
            "name": "BitOffset",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 7,
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterTProperty:
    """
    :ivar object_index: registration-relevant
    :ivar object_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar property_id: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        global_type = False

    object_index: None | int = field(
        default=None,
        metadata={
            "name": "ObjectIndex",
            "type": "Attribute",
        },
    )
    object_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjectType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    property_id: int = field(
        metadata={
            "name": "PropertyId",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    bit_offset: int = field(
        metadata={
            "name": "BitOffset",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 7,
        }
    )


class ProcedureTypeT(Enum):
    LOAD = "Load"
    UNLOAD = "Unload"


@dataclass(slots=True, kw_only=True)
class ProjectTraceT:
    class Meta:
        name = "ProjectTrace_t"

    date: XmlDateTime = field(
        metadata={
            "name": "Date",
            "type": "Attribute",
        }
    )
    user_name: str = field(
        metadata={
            "name": "UserName",
            "type": "Attribute",
        }
    )
    comment: str = field(
        metadata={
            "name": "Comment",
            "type": "Attribute",
        }
    )


class ProjectTracingLevelT(Enum):
    NONE = "None"
    OPERATION_USED = "OperationUsed"
    DETAILED = "Detailed"


@dataclass(slots=True, kw_only=True)
class ProjectTProjectInformationHistoryEntriesHistoryEntry:
    class Meta:
        global_type = False

    date: XmlDateTime = field(
        metadata={
            "name": "Date",
            "type": "Attribute",
        }
    )
    user: None | str = field(
        default=None,
        metadata={
            "name": "User",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
        }
    )
    detail: None | str = field(
        default=None,
        metadata={
            "name": "Detail",
            "type": "Attribute",
        },
    )


class PropTypeT(Enum):
    PDT_CONTROL = "PDT_CONTROL"
    PDT_CHAR = "PDT_CHAR"
    PDT_UNSIGNED_CHAR = "PDT_UNSIGNED_CHAR"
    PDT_INT = "PDT_INT"
    PDT_UNSIGNED_INT = "PDT_UNSIGNED_INT"
    PDT_KNX_FLOAT = "PDT_KNX_FLOAT"
    PDT_DATE = "PDT_DATE"
    PDT_TIME = "PDT_TIME"
    PDT_LONG = "PDT_LONG"
    PDT_UNSIGNED_LONG = "PDT_UNSIGNED_LONG"
    PDT_FLOAT = "PDT_FLOAT"
    PDT_DOUBLE = "PDT_DOUBLE"
    PDT_CHAR_BLOCK = "PDT_CHAR_BLOCK"
    PDT_POLL_GROUP_SETTINGS = "PDT_POLL_GROUP_SETTINGS"
    PDT_SHORT_CHAR_BLOCK = "PDT_SHORT_CHAR_BLOCK"
    PDT_DATE_TIME = "PDT_DATE_TIME"
    PDT_VARIABLE_LENGTH = "PDT_VARIABLE_LENGTH"
    PDT_GENERIC_01 = "PDT_GENERIC_01"
    PDT_GENERIC_02 = "PDT_GENERIC_02"
    PDT_GENERIC_03 = "PDT_GENERIC_03"
    PDT_GENERIC_04 = "PDT_GENERIC_04"
    PDT_GENERIC_05 = "PDT_GENERIC_05"
    PDT_GENERIC_06 = "PDT_GENERIC_06"
    PDT_GENERIC_07 = "PDT_GENERIC_07"
    PDT_GENERIC_08 = "PDT_GENERIC_08"
    PDT_GENERIC_09 = "PDT_GENERIC_09"
    PDT_GENERIC_10 = "PDT_GENERIC_10"
    PDT_GENERIC_11 = "PDT_GENERIC_11"
    PDT_GENERIC_12 = "PDT_GENERIC_12"
    PDT_GENERIC_13 = "PDT_GENERIC_13"
    PDT_GENERIC_14 = "PDT_GENERIC_14"
    PDT_GENERIC_15 = "PDT_GENERIC_15"
    PDT_GENERIC_16 = "PDT_GENERIC_16"
    PDT_GENERIC_17 = "PDT_GENERIC_17"
    PDT_GENERIC_18 = "PDT_GENERIC_18"
    PDT_GENERIC_19 = "PDT_GENERIC_19"
    PDT_GENERIC_20 = "PDT_GENERIC_20"
    PDT_UTF_8 = "PDT_UTF-8"
    PDT_VERSION = "PDT_VERSION"
    PDT_ALARM_INFO = "PDT_ALARM_INFO"
    PDT_BINARY_INFORMATION = "PDT_BINARY_INFORMATION"
    PDT_BITSET8 = "PDT_BITSET8"
    PDT_BITSET16 = "PDT_BITSET16"
    PDT_ENUM8 = "PDT_ENUM8"
    PDT_SCALING = "PDT_SCALING"
    PDT_NE_VL = "PDT_NE_VL"
    PDT_NE_FL = "PDT_NE_FL"
    PDT_FUNCTION = "PDT_FUNCTION"


class RegistrationInfoTRegistrationKey(Enum):
    KNXCONV = "knxconv"
    KNXCERT = "knxcert"


class RegistrationStatusT(Enum):
    UNREGISTERED = "Unregistered"
    REGISTERED = "Registered"
    CERTIFIED = "Certified"
    FUTURE_USE_NOT_RECOMMENDED = "FutureUseNotRecommended"
    FUTURE_USE_NOT_ALLOWED = "FutureUseNotAllowed"


class ResourceAccessRightsT(Enum):
    NONE = "None"
    SYSTEM_MANUFACTURER = "SystemManufacturer"
    MANUFACTURER = "Manufacturer"
    CONFIGURATION = "Configuration"
    RUNTIME = "Runtime"


class ResourceAccessT(Enum):
    REMOTE = "remote"
    LOCAL1 = "local1"
    LOCAL2 = "local2"


class ResourceAddrSpaceT(Enum):
    NONE = "None"
    STANDARD_MEMORY = "StandardMemory"
    USER_MEMORY = "UserMemory"
    SYSTEM_PROPERTY = "SystemProperty"
    APP_PROPERTY = "AppProperty"
    LC_SLAVE_MEMORY = "LcSlaveMemory"
    LC_FILTER_MEMORY = "LcFilterMemory"
    ADC = "ADC"
    CONSTANT = "Constant"
    POINTER = "Pointer"
    PROPERTY = "Property"
    RELATIVE_MEMORY = "RelativeMemory"


class ResourceMgmtStyleT(Enum):
    SIMPLE = "simple"
    LSM = "lsm"


class ResourceNameT(Enum):
    MANAGEMENT_STYLE = "ManagementStyle"
    DEVICE_MANUFACTURER_ID = "DeviceManufacturerId"
    DEVICE_BUS_VOLTAGE = "DeviceBusVoltage"
    DEVICE_PEI_TYPE = "DevicePeiType"
    GROUP_ADDRESS_TABLE_LOAD_CONTROL = "GroupAddressTableLoadControl"
    GROUP_ADDRESS_TABLE_LOAD_STATUS = "GroupAddressTableLoadStatus"
    GROUP_ADDRESS_TABLE_PTR = "GroupAddressTablePtr"
    GROUP_ADDRESS_TABLE = "GroupAddressTable"
    GROUP_ASSOCIATION_TABLE_LOAD_CONTROL = "GroupAssociationTableLoadControl"
    GROUP_ASSOCIATION_TABLE_LOAD_STATUS = "GroupAssociationTableLoadStatus"
    GROUP_ASSOCIATION_TABLE_PTR = "GroupAssociationTablePtr"
    GROUP_ASSOCIATION_TABLE = "GroupAssociationTable"
    GROUP_OBJECT_TABLE_PTR = "GroupObjectTablePtr"
    GROUP_OBJECT_TABLE = "GroupObjectTable"
    GROUP_FILTER_TABLE_PTR = "GroupFilterTablePtr"
    GROUP_FILTER_TABLE = "GroupFilterTable"
    APPLICATION_ID = "ApplicationId"
    APPLICATION_LOAD_CONTROL = "ApplicationLoadControl"
    APPLICATION_LOAD_STATUS = "ApplicationLoadStatus"
    APPLICATION_RUN_CONTROL = "ApplicationRunControl"
    APPLICATION_RUN_STATUS = "ApplicationRunStatus"
    PEIPROG_ID = "PeiprogId"
    PEIPROG_LOAD_CONTROL = "PeiprogLoadControl"
    PEIPROG_LOAD_STATUS = "PeiprogLoadStatus"
    PEIPROG_RUN_CONTROL = "PeiprogRunControl"
    PEIPROG_RUN_STATUS = "PeiprogRunStatus"
    APPLICATION_PEI_TYPE = "ApplicationPeiType"
    RE_CONFIG = "ReConfig"
    INDIVIDUAL_ADDRESS = "IndividualAddress"
    DOMAIN_ADDRESS = "DomainAddress"
    FREQUENCY_CHANNEL = "FrequencyChannel"
    SENSITIVITY = "Sensitivity"
    HARDWARE_CONFIG1 = "HardwareConfig1"
    HARDWARE_CONFIG2 = "HardwareConfig2"
    HARDWARE_CONFIG3 = "HardwareConfig3"
    HARDWARE_CONFIG4 = "HardwareConfig4"
    DEVICE_ORDER_ID = "DeviceOrderId"
    DEVICE_SERIAL_NUMBER = "DeviceSerialNumber"
    PROGRAMMING_MODE = "ProgrammingMode"
    POLLING_GROUP_SETTINGS = "PollingGroupSettings"
    MANAGEMENT_DESCRIPTOR01 = "ManagementDescriptor01"
    RUN_ERROR = "RunError"
    LC_CONFIG = "LcConfig"
    LC_GRP_CONFIG = "LcGrpConfig"
    LC_ERROR = "LcError"
    LC_MODE = "LcMode"
    GROUP_OBJECT_TABLE_LOAD_CONTROL = "GroupObjectTableLoadControl"
    GROUP_OBJECT_TABLE_LOAD_STATUS = "GroupObjectTableLoadStatus"
    GROUP_ACKNOWLEDGE_TABLE = "GroupAcknowledgeTable"
    HARDWARE_TYPE = "HardwareType"
    FIRMWARE_VERSION = "FirmwareVersion"
    MANUFACTURER_DATA = "ManufacturerData"
    APPLICATION_DATA_PTR = "ApplicationDataPtr"
    PEIPROG_DATA_PTR = "PeiprogDataPtr"
    GROUP_ADDRESS_TABLE_STAMP = "GroupAddressTableStamp"
    GROUP_ASSOCIATION_TABLE_STAMP = "GroupAssociationTableStamp"
    GROUP_OBJECT_TABLE_STAMP = "GroupObjectTableStamp"
    GROUP_FILTER_TABLE_STAMP = "GroupFilterTableStamp"
    APPLICATION_STAMP = "ApplicationStamp"
    PEIPROG_STAMP = "PeiprogStamp"


class ToDoStatusT(Enum):
    OPEN = "Open"
    ACCOMPLISHED = "Accomplished"


@dataclass(slots=True, kw_only=True)
class TopologyTAreaLineAdditionalGroupAddressesGroupAddress:
    class Meta:
        global_type = False

    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class UserFileT:
    class Meta:
        name = "UserFile_t"

    filename: str = field(
        metadata={
            "name": "Filename",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class WhenT:
    """
    :ivar test: registration-relevant
    :ivar default: registration-relevant
    """

    class Meta:
        name = "When_t"

    test: None | str = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"((-?\d+\s)*-?\d+)|((=|(!=)|>|<|(>=)|(<=))-?\d+)",
        },
    )
    default: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTBinaryData:
    class Meta:
        global_type = False

    binary_data: list[BinaryDataT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTCodeAbsoluteSegment:
    """
    :ivar data: registration-relevant
    :ivar mask: registration-relevant
    :ivar id: registration-relevant
    :ivar name:
    :ivar memory_type:
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar user_memory: registration-relevant
    """

    class Meta:
        global_type = False

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    mask: None | bytes = field(
        default=None,
        metadata={
            "name": "Mask",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    memory_type: None | MemoryTypeT = field(
        default=None,
        metadata={
            "name": "MemoryType",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    user_memory: bool = field(
        default=False,
        metadata={
            "name": "UserMemory",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTDeviceCompare:
    class Meta:
        global_type = False

    exclude_memory: list[ApplicationProgramStaticTDeviceCompareExcludeMemory] = field(
        default_factory=list,
        metadata={
            "name": "ExcludeMemory",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    exclude_property: list[ApplicationProgramStaticTDeviceCompareExcludeProperty] = field(
        default_factory=list,
        metadata={
            "name": "ExcludeProperty",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTExtension:
    class Meta:
        global_type = False

    baggage: list[ApplicationProgramStaticTExtensionBaggage] = field(
        default_factory=list,
        metadata={
            "name": "Baggage",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    ets_download_plugin: None | str = field(
        default=None,
        metadata={
            "name": "EtsDownloadPlugin",
            "type": "Attribute",
        },
    )
    ets_ui_plugin: None | str = field(
        default=None,
        metadata={
            "name": "EtsUiPlugin",
            "type": "Attribute",
        },
    )
    ets_data_handler: None | str = field(
        default=None,
        metadata={
            "name": "EtsDataHandler",
            "type": "Attribute",
        },
    )
    ets_data_handler_capabilities: list[CapabilityT] = field(
        default_factory=list,
        metadata={
            "name": "EtsDataHandlerCapabilities",
            "type": "Attribute",
            "tokens": True,
        },
    )
    requires_external_software: bool = field(
        default=False,
        metadata={
            "name": "RequiresExternalSoftware",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTFixupList:
    """
    :ivar fixup: registration-relevant set
    """

    class Meta:
        global_type = False

    fixup: list[FixupT] = field(
        default_factory=list,
        metadata={
            "name": "Fixup",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTOptions:
    class Meta:
        global_type = False

    prefer_partial_download_if_application_loaded: bool = field(
        default=False,
        metadata={
            "name": "PreferPartialDownloadIfApplicationLoaded",
            "type": "Attribute",
        },
    )
    easy_ctrl_mode_mode_style_empty_group_com_tables: bool = field(
        default=False,
        metadata={
            "name": "EasyCtrlModeModeStyleEmptyGroupComTables",
            "type": "Attribute",
        },
    )
    set_object_table_length_always_to_one: bool = field(
        default=False,
        metadata={
            "name": "SetObjectTableLengthAlwaysToOne",
            "type": "Attribute",
        },
    )
    text_parameter_encoding: None | ApplicationProgramStaticTOptionsTextParameterEncoding = field(
        default=None,
        metadata={
            "name": "TextParameterEncoding",
            "type": "Attribute",
        },
    )
    text_parameter_zero_terminate: bool = field(
        default=False,
        metadata={
            "name": "TextParameterZeroTerminate",
            "type": "Attribute",
        },
    )
    parameter_byte_order: ApplicationProgramStaticTOptionsParameterByteOrder = field(
        default=ApplicationProgramStaticTOptionsParameterByteOrder.BIG_ENDIAN,
        metadata={
            "name": "ParameterByteOrder",
            "type": "Attribute",
        },
    )
    partial_download_only_visible_parameters: bool = field(
        default=False,
        metadata={
            "name": "PartialDownloadOnlyVisibleParameters",
            "type": "Attribute",
        },
    )
    legacy_no_partial_download: bool = field(
        default=False,
        metadata={
            "name": "LegacyNoPartialDownload",
            "type": "Attribute",
        },
    )
    legacy_no_memory_verify_mode: bool = field(
        default=False,
        metadata={
            "name": "LegacyNoMemoryVerifyMode",
            "type": "Attribute",
        },
    )
    legacy_no_optimistic_write: bool = field(
        default=False,
        metadata={
            "name": "LegacyNoOptimisticWrite",
            "type": "Attribute",
        },
    )
    legacy_do_not_report_property_write_errors: bool = field(
        default=False,
        metadata={
            "name": "LegacyDoNotReportPropertyWriteErrors",
            "type": "Attribute",
        },
    )
    legacy_no_background_download: bool = field(
        default=False,
        metadata={
            "name": "LegacyNoBackgroundDownload",
            "type": "Attribute",
        },
    )
    legacy_do_not_check_manufacturer_id: bool = field(
        default=False,
        metadata={
            "name": "LegacyDoNotCheckManufacturerId",
            "type": "Attribute",
        },
    )
    legacy_always_reload_app_if_co_visibility_changed: bool = field(
        default=False,
        metadata={
            "name": "LegacyAlwaysReloadAppIfCoVisibilityChanged",
            "type": "Attribute",
        },
    )
    legacy_never_reload_app_if_co_visibility_changed: bool = field(
        default=False,
        metadata={
            "name": "LegacyNeverReloadAppIfCoVisibilityChanged",
            "type": "Attribute",
        },
    )
    legacy_do_not_support_undo_delete: bool = field(
        default=False,
        metadata={
            "name": "LegacyDoNotSupportUndoDelete",
            "type": "Attribute",
        },
    )
    legacy_allow_partial_download_if_ap2_mismatch: bool = field(
        default=False,
        metadata={
            "name": "LegacyAllowPartialDownloadIfAp2Mismatch",
            "type": "Attribute",
        },
    )
    legacy_keep_object_table_gaps: bool = field(
        default=False,
        metadata={
            "name": "LegacyKeepObjectTableGaps",
            "type": "Attribute",
        },
    )
    legacy_proxy_communication_objects: bool = field(
        default=False,
        metadata={
            "name": "LegacyProxyCommunicationObjects",
            "type": "Attribute",
        },
    )
    device_info_ignore_run_state: bool = field(
        default=False,
        metadata={
            "name": "DeviceInfoIgnoreRunState",
            "type": "Attribute",
        },
    )
    device_info_ignore_loaded_state: bool = field(
        default=False,
        metadata={
            "name": "DeviceInfoIgnoreLoadedState",
            "type": "Attribute",
        },
    )
    device_compare_allow_compatible_manufacturer_id: bool = field(
        default=False,
        metadata={
            "name": "DeviceCompareAllowCompatibleManufacturerId",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class BuildingPartT:
    class Meta:
        name = "BuildingPart_t"

    building_part: list[BuildingPartT] = field(
        default_factory=list,
        metadata={
            "name": "BuildingPart",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    type_value: BuildingPartTypeT = field(
        metadata={
            "name": "Type",
            "type": "Attribute",
        }
    )
    number: None | str = field(
        default=None,
        metadata={
            "name": "Number",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    completion_status: CompletionStatusT = field(
        default=CompletionStatusT.UNDEFINED,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    default_line: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLine",
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class CatalogSectionT:
    class Meta:
        name = "CatalogSection_t"

    catalog_section: list[CatalogSectionT] = field(
        default_factory=list,
        metadata={
            "name": "CatalogSection",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    catalog_item: list[CatalogSectionTCatalogItem] = field(
        default_factory=list,
        metadata={
            "name": "CatalogItem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    number: str = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
            "max_length": 20,
        }
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    default_language: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLanguage",
            "type": "Attribute",
        },
    )
    non_reg_relevant_data_version: int = field(
        default=0,
        metadata={
            "name": "NonRegRelevantDataVersion",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefTConnectors:
    class Meta:
        global_type = False

    send: ComObjectInstanceRefTConnectorsSend = field(
        metadata={
            "name": "Send",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    receive: list[ComObjectInstanceRefTConnectorsReceive] = field(
        default_factory=list,
        metadata={
            "name": "Receive",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectRefT:
    """
    :ivar id: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar tag:
    :ivar function_text:
    :ivar visible_description:
    :ivar priority:
    :ivar object_size: registration-relevant
    :ivar read_flag:
    :ivar write_flag:
    :ivar communication_flag:
    :ivar transmit_flag:
    :ivar update_flag:
    :ivar read_on_init_flag:
    :ivar datapoint_type:
    """

    class Meta:
        name = "ComObjectRef_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    tag: None | str = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    function_text: None | str = field(
        default=None,
        metadata={
            "name": "FunctionText",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    priority: None | ComObjectPriorityT = field(
        default=None,
        metadata={
            "name": "Priority",
            "type": "Attribute",
        },
    )
    object_size: None | ComObjectSizeT = field(
        default=None,
        metadata={
            "name": "ObjectSize",
            "type": "Attribute",
        },
    )
    read_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "ReadFlag",
            "type": "Attribute",
        },
    )
    write_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "WriteFlag",
            "type": "Attribute",
        },
    )
    communication_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "CommunicationFlag",
            "type": "Attribute",
        },
    )
    transmit_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "TransmitFlag",
            "type": "Attribute",
        },
    )
    update_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "UpdateFlag",
            "type": "Attribute",
        },
    )
    read_on_init_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "ReadOnInitFlag",
            "type": "Attribute",
        },
    )
    datapoint_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DatapointType",
            "type": "Attribute",
            "tokens": True,
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar number: registration-relevant
    :ivar function_text:
    :ivar visible_description:
    :ivar priority:
    :ivar object_size: registration-relevant
    :ivar read_flag:
    :ivar write_flag:
    :ivar communication_flag:
    :ivar transmit_flag:
    :ivar update_flag:
    :ivar read_on_init_flag:
    :ivar datapoint_type:
    """

    class Meta:
        name = "ComObject_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    function_text: str = field(
        metadata={
            "name": "FunctionText",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    priority: ComObjectPriorityT = field(
        default=ComObjectPriorityT.LOW,
        metadata={
            "name": "Priority",
            "type": "Attribute",
        },
    )
    object_size: ComObjectSizeT = field(
        metadata={
            "name": "ObjectSize",
            "type": "Attribute",
        }
    )
    read_flag: EnableT = field(
        metadata={
            "name": "ReadFlag",
            "type": "Attribute",
        }
    )
    write_flag: EnableT = field(
        metadata={
            "name": "WriteFlag",
            "type": "Attribute",
        }
    )
    communication_flag: EnableT = field(
        metadata={
            "name": "CommunicationFlag",
            "type": "Attribute",
        }
    )
    transmit_flag: EnableT = field(
        metadata={
            "name": "TransmitFlag",
            "type": "Attribute",
        }
    )
    update_flag: EnableT = field(
        metadata={
            "name": "UpdateFlag",
            "type": "Attribute",
        }
    )
    read_on_init_flag: EnableT = field(
        metadata={
            "name": "ReadOnInitFlag",
            "type": "Attribute",
        }
    )
    datapoint_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DatapointType",
            "type": "Attribute",
            "tokens": True,
        },
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceTBinaryData:
    class Meta:
        global_type = False

    binary_data: list[DeviceInstanceTBinaryDataBinaryData] = field(
        default_factory=list,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceTParameterInstanceRefs:
    class Meta:
        global_type = False

    parameter_instance_ref: list[ParameterInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class GroupRangeT:
    class Meta:
        name = "GroupRange_t"

    group_range: list[GroupRangeT] = field(
        default_factory=list,
        metadata={
            "name": "GroupRange",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 65535,
        },
    )
    group_address: list[GroupAddressT] = field(
        default_factory=list,
        metadata={
            "name": "GroupAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 65535,
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    range_start: int = field(
        metadata={
            "name": "RangeStart",
            "type": "Attribute",
        }
    )
    range_end: int = field(
        metadata={
            "name": "RangeEnd",
            "type": "Attribute",
        }
    )
    unfiltered: bool = field(
        default=False,
        metadata={
            "name": "Unfiltered",
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class HardwareTProductsProductAttributesAttribute:
    class Meta:
        global_type = False

    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    name: HardwareTProductsProductAttributesAttributeName = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    value: str = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
            "max_length": 255,
        }
    )


@dataclass(slots=True, kw_only=True)
class HardwareTProductsProductBaggages:
    class Meta:
        global_type = False

    baggage: list[HardwareTProductsProductBaggagesBaggage] = field(
        default_factory=list,
        metadata={
            "name": "Baggage",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTFeaturesFeature:
    class Meta:
        global_type = False

    name: HawkConfigurationDataTFeaturesFeatureName = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    value: int = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTInterfaceObjectsInterfaceObjectProperty:
    class Meta:
        global_type = False

    property_id: int = field(
        metadata={
            "name": "PropertyID",
            "type": "Attribute",
        }
    )
    property_data_type: None | PropTypeT = field(
        default=None,
        metadata={
            "name": "PropertyDataType",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTMemorySegmentsMemorySegmentAccessRights:
    class Meta:
        global_type = False

    read: ResourceAccessRightsT = field(
        metadata={
            "name": "Read",
            "type": "Attribute",
        }
    )
    write: ResourceAccessRightsT = field(
        metadata={
            "name": "Write",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTResourcesResourceAccessRights:
    class Meta:
        global_type = False

    read: ResourceAccessRightsT = field(
        metadata={
            "name": "Read",
            "type": "Attribute",
        }
    )
    write: ResourceAccessRightsT = field(
        metadata={
            "name": "Write",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTResourcesResourceResourceType:
    class Meta:
        global_type = False

    length: int = field(
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    flavour: None | HawkConfigurationDataTResourcesResourceResourceTypeFlavour = field(
        default=None,
        metadata={
            "name": "Flavour",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class IpconfigT:
    class Meta:
        name = "IPConfig_t"

    assign: IpconfigAssignT = field(
        default=IpconfigAssignT.AUTO,
        metadata={
            "name": "Assign",
            "type": "Attribute",
        },
    )
    ipaddress: None | str = field(
        default=None,
        metadata={
            "name": "IPAddress",
            "type": "Attribute",
            "pattern": r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])",
        },
    )
    subnet_mask: None | str = field(
        default=None,
        metadata={
            "name": "SubnetMask",
            "type": "Attribute",
            "pattern": r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])",
        },
    )
    default_gateway: None | str = field(
        default=None,
        metadata={
            "name": "DefaultGateway",
            "type": "Attribute",
            "pattern": r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])",
        },
    )
    macaddress: None | str = field(
        default=None,
        metadata={
            "name": "MACAddress",
            "type": "Attribute",
            "max_length": 50,
        },
    )


@dataclass(slots=True, kw_only=True)
class LanguageDataTTranslationUnitTranslationElement:
    class Meta:
        global_type = False

    translation: list[LanguageDataTTranslationUnitTranslationElementTranslation] = field(
        default_factory=list,
        metadata={
            "name": "Translation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlAbsSegment:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar seg_type: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar access: registration-relevant
    :ivar mem_type: registration-relevant
    :ivar seg_flags: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    seg_type: int = field(
        metadata={
            "name": "SegType",
            "type": "Attribute",
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    access: int = field(
        metadata={
            "name": "Access",
            "type": "Attribute",
        }
    )
    mem_type: int = field(
        metadata={
            "name": "MemType",
            "type": "Attribute",
        }
    )
    seg_flags: int = field(
        metadata={
            "name": "SegFlags",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlClearCachedObjectTypes:
    """
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlClearLcfilterTable:
    """
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlCompareMem:
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    address_space: LdCtrlMemAddrSpaceT = field(
        default=LdCtrlMemAddrSpaceT.STANDARD,
        metadata={
            "name": "AddressSpace",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    inline_data: bytes = field(
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlCompareProp:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar start_element: registration-relevant
    :ivar count: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    start_element: int = field(
        default=1,
        metadata={
            "name": "StartElement",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    inline_data: bytes = field(
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlCompareRelMem:
    """
    :ivar obj_idx: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: int = field(
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    inline_data: bytes = field(
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlConnect:
    """
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlDeclarePropDesc:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar prop_type: registration-relevant
    :ivar max_elements: registration-relevant
    :ivar read_access: registration-relevant
    :ivar write_access: registration-relevant
    :ivar writable: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    prop_type: PropTypeT = field(
        metadata={
            "name": "PropType",
            "type": "Attribute",
        }
    )
    max_elements: int = field(
        metadata={
            "name": "MaxElements",
            "type": "Attribute",
            "min_inclusive": 1,
        }
    )
    read_access: int = field(
        metadata={
            "name": "ReadAccess",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 15,
        }
    )
    write_access: int = field(
        metadata={
            "name": "WriteAccess",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 15,
        }
    )
    writable: bool = field(
        metadata={
            "name": "Writable",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlDelay:
    """
    :ivar milli_seconds: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    milli_seconds: int = field(
        metadata={
            "name": "MilliSeconds",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlDisconnect:
    """
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlInvokeFunctionProp:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    inline_data: None | bytes = field(
        default=None,
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlLoad:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlLoadCompleted:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlLoadImageMem:
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    address_space: LdCtrlMemAddrSpaceT = field(
        default=LdCtrlMemAddrSpaceT.STANDARD,
        metadata={
            "name": "AddressSpace",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlLoadImageProp:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar count: registration-relevant
    :ivar start_element: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    start_element: int = field(
        default=1,
        metadata={
            "name": "StartElement",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlLoadImageRelMem:
    """
    :ivar obj_idx: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: int = field(
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlMapError:
    """
    :ivar ld_ctrl_filter: registration-relevant
    :ivar original_error: registration-relevant
    :ivar mapped_error: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    ld_ctrl_filter: int = field(
        default=0,
        metadata={
            "name": "LdCtrlFilter",
            "type": "Attribute",
        },
    )
    original_error: int = field(
        metadata={
            "name": "OriginalError",
            "type": "Attribute",
        }
    )
    mapped_error: int = field(
        metadata={
            "name": "MappedError",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlMaxLength:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar applies_to: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlProgressText:
    """
    :ivar text_id: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    text_id: int = field(
        metadata={
            "name": "TextId",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlReadFunctionProp:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlRelSegment:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar size: registration-relevant
    :ivar mode: registration-relevant
    :ivar fill: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    mode: int = field(
        metadata={
            "name": "Mode",
            "type": "Attribute",
        }
    )
    fill: int = field(
        metadata={
            "name": "Fill",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlRestart:
    """
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlSetControlVariable:
    """
    :ivar name: registration-relevant
    :ivar value: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    name: LdCtrlControlVariableT = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    value: bool = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlTaskCtrl1:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar address: registration-relevant
    :ivar count: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    count: int = field(
        metadata={
            "name": "Count",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlTaskCtrl2:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar callback: registration-relevant
    :ivar address: registration-relevant
    :ivar seg0: registration-relevant
    :ivar seg1: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    callback: int = field(
        metadata={
            "name": "Callback",
            "type": "Attribute",
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    seg0: int = field(
        metadata={
            "name": "Seg0",
            "type": "Attribute",
        }
    )
    seg1: int = field(
        metadata={
            "name": "Seg1",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlTaskPtr:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar init_ptr: registration-relevant
    :ivar save_ptr: registration-relevant
    :ivar serial_ptr: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    init_ptr: int = field(
        metadata={
            "name": "InitPtr",
            "type": "Attribute",
        }
    )
    save_ptr: int = field(
        metadata={
            "name": "SavePtr",
            "type": "Attribute",
        }
    )
    serial_ptr: int = field(
        metadata={
            "name": "SerialPtr",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlTaskSegment:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar address: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlUnload:
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    lsm_idx: None | int = field(
        default=None,
        metadata={
            "name": "LsmIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlWriteMem:
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    address_space: LdCtrlMemAddrSpaceT = field(
        default=LdCtrlMemAddrSpaceT.STANDARD,
        metadata={
            "name": "AddressSpace",
            "type": "Attribute",
        },
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    verify: bool = field(
        metadata={
            "name": "Verify",
            "type": "Attribute",
        }
    )
    inline_data: None | bytes = field(
        default=None,
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlWriteProp:
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar start_element: registration-relevant
    :ivar count: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: None | int = field(
        default=None,
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        },
    )
    obj_type: None | int = field(
        default=None,
        metadata={
            "name": "ObjType",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    prop_id: int = field(
        metadata={
            "name": "PropId",
            "type": "Attribute",
        }
    )
    start_element: int = field(
        default=1,
        metadata={
            "name": "StartElement",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 4095,
        },
    )
    verify: bool = field(
        metadata={
            "name": "Verify",
            "type": "Attribute",
        }
    )
    inline_data: None | bytes = field(
        default=None,
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureTLdCtrlWriteRelMem:
    """
    :ivar obj_idx: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar applies_to: registration-relevant
    """

    class Meta:
        global_type = False

    obj_idx: int = field(
        metadata={
            "name": "ObjIdx",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    size: int = field(
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    verify: bool = field(
        metadata={
            "name": "Verify",
            "type": "Attribute",
        }
    )
    inline_data: None | bytes = field(
        default=None,
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        },
    )
    applies_to: LdCtrlProcTypeT = field(
        default=LdCtrlProcTypeT.AUTO,
        metadata={
            "name": "AppliesTo",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerBaggagesBaggage:
    class Meta:
        global_type = False

    file_info: ManufacturerDataTManufacturerBaggagesBaggageFileInfo = field(
        metadata={
            "name": "FileInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "format": "base64",
        },
    )
    target_path: str = field(
        metadata={
            "name": "TargetPath",
            "type": "Attribute",
            "max_length": 255,
            "pattern": r'(([^"<>\|:\*\?/\\\t\n\r]+\\)*[^"<>\|:\*\?/\\\t\n\r]+)?',
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
            "pattern": r'[^"<>\|:\*\?/\\\t\n\r]+',
        }
    )
    install_on_import: bool = field(
        metadata={
            "name": "InstallOnImport",
            "type": "Attribute",
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class MaskVersionTDownwardCompatibleMasks:
    class Meta:
        global_type = False

    downward_compatible_mask: list[MaskVersionTDownwardCompatibleMasksDownwardCompatibleMask] = (
        field(
            default_factory=list,
            metadata={
                "name": "DownwardCompatibleMask",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/10",
                "min_occurs": 1,
            },
        )
    )


@dataclass(slots=True, kw_only=True)
class MaskVersionTMaskEntries:
    class Meta:
        global_type = False

    mask_entry: list[MaskVersionTMaskEntriesMaskEntry] = field(
        default_factory=list,
        metadata={
            "name": "MaskEntry",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTDatapointTypesDatapointTypeDatapointSubtypes:
    class Meta:
        global_type = False

    datapoint_subtype: list[
        MasterDataTDatapointTypesDatapointTypeDatapointSubtypesDatapointSubtype
    ] = field(
        default_factory=list,
        metadata={
            "name": "DatapointSubtype",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTManufacturers:
    class Meta:
        global_type = False

    manufacturer: list[MasterDataTManufacturersManufacturer] = field(
        default_factory=list,
        metadata={
            "name": "Manufacturer",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTMediumTypes:
    class Meta:
        global_type = False

    medium_type: list[MasterDataTMediumTypesMediumType] = field(
        default_factory=list,
        metadata={
            "name": "MediumType",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterCalculationTLparametersParameterRefRef(ParameterRefRefT):
    """
    :ivar alias_name: registration-relevant
    """

    class Meta:
        global_type = False

    alias_name: None | str = field(
        default=None,
        metadata={
            "name": "AliasName",
            "type": "Attribute",
            "max_length": 50,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterCalculationTRparametersParameterRefRef(ParameterRefRefT):
    """
    :ivar alias_name: registration-relevant
    """

    class Meta:
        global_type = False

    alias_name: None | str = field(
        default=None,
        metadata={
            "name": "AliasName",
            "type": "Attribute",
            "max_length": 50,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterRefT:
    """
    :ivar id: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar tag:
    :ivar display_order:
    :ivar access:
    :ivar value: registration-relevant
    """

    class Meta:
        name = "ParameterRef_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    tag: None | str = field(
        default=None,
        metadata={
            "name": "Tag",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    display_order: None | int = field(
        default=None,
        metadata={
            "name": "DisplayOrder",
            "type": "Attribute",
        },
    )
    access: None | AccessT = field(
        default=None,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )
    value: None | str = field(
        default=None,
        metadata={
            "name": "Value",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterSeparatorT:
    """
    :ivar id: registration-relevant
    :ivar text:
    :ivar access:
    """

    class Meta:
        name = "ParameterSeparator_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    access: AccessT = field(
        default=AccessT.READ_WRITE,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeDate:
    """
    :ivar encoding: registration-relevant
    """

    class Meta:
        global_type = False

    encoding: ParameterTypeTTypeDateEncoding = field(
        metadata={
            "name": "Encoding",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeFloat:
    """
    :ivar encoding: registration-relevant
    :ivar min_inclusive: registration-relevant
    :ivar max_inclusive: registration-relevant
    :ivar uihint:
    :ivar display_format:
    """

    class Meta:
        global_type = False

    encoding: ParameterTypeTTypeFloatEncoding = field(
        metadata={
            "name": "Encoding",
            "type": "Attribute",
        }
    )
    min_inclusive: float = field(
        metadata={
            "name": "minInclusive",
            "type": "Attribute",
        }
    )
    max_inclusive: float = field(
        metadata={
            "name": "maxInclusive",
            "type": "Attribute",
        }
    )
    uihint: None | ParameterTypeTTypeFloatUihint = field(
        default=None,
        metadata={
            "name": "UIHint",
            "type": "Attribute",
        },
    )
    display_format: None | str = field(
        default=None,
        metadata={
            "name": "DisplayFormat",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeIpaddress:
    """
    :ivar address_type: registration-relevant
    :ivar version: registration-relevant
    """

    class Meta:
        global_type = False

    address_type: ParameterTypeTTypeIpaddressAddressType = field(
        metadata={
            "name": "AddressType",
            "type": "Attribute",
        }
    )
    version: ParameterTypeTTypeIpaddressVersion = field(
        default=ParameterTypeTTypeIpaddressVersion.IPV4,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeNumber:
    """
    :ivar size_in_bit: registration-relevant
    :ivar type_value: registration-relevant
    :ivar min_inclusive: registration-relevant
    :ivar max_inclusive: registration-relevant
    :ivar uihint:
    """

    class Meta:
        global_type = False

    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 32,
        }
    )
    type_value: ParameterTypeTTypeNumberType = field(
        metadata={
            "name": "Type",
            "type": "Attribute",
        }
    )
    min_inclusive: int = field(
        metadata={
            "name": "minInclusive",
            "type": "Attribute",
        }
    )
    max_inclusive: int = field(
        metadata={
            "name": "maxInclusive",
            "type": "Attribute",
        }
    )
    uihint: None | ParameterTypeTTypeNumberUihint = field(
        default=None,
        metadata={
            "name": "UIHint",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeRestriction:
    """
    :ivar enumeration: registration-relevant set
    :ivar base: registration-relevant
    :ivar size_in_bit: registration-relevant
    """

    class Meta:
        global_type = False

    enumeration: list[ParameterTypeTTypeRestrictionEnumeration] = field(
        default_factory=list,
        metadata={
            "name": "Enumeration",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    base: ParameterTypeTTypeRestrictionBase = field(
        metadata={
            "name": "Base",
            "type": "Attribute",
        }
    )
    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
            "min_inclusive": 1,
            "max_inclusive": 1048575,
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeTTypeTime:
    """
    :ivar size_in_bit: registration-relevant
    :ivar unit: registration-relevant
    :ivar min_inclusive: registration-relevant
    :ivar max_inclusive: registration-relevant
    :ivar uihint:
    """

    class Meta:
        global_type = False

    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
            "min_inclusive": 8,
            "max_inclusive": 64,
        }
    )
    unit: ParameterTypeTTypeTimeUnit = field(
        metadata={
            "name": "Unit",
            "type": "Attribute",
        }
    )
    min_inclusive: int = field(
        metadata={
            "name": "minInclusive",
            "type": "Attribute",
        }
    )
    max_inclusive: int = field(
        metadata={
            "name": "maxInclusive",
            "type": "Attribute",
        }
    )
    uihint: None | ParameterTypeTTypeTimeUihint = field(
        default=None,
        metadata={
            "name": "UIHint",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterT:
    """
    :ivar memory_or_property:
    :ivar legacy_patch_always: registration-relevant
    :ivar id: registration-relevant
    :ivar name:
    :ivar parameter_type: registration-relevant
    :ivar text:
    :ivar access:
    :ivar value: registration-relevant
    """

    class Meta:
        name = "Parameter_t"

    memory_or_property: None | ParameterTMemory | ParameterTProperty = field(
        default=None,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Memory",
                    "type": ParameterTMemory,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Property",
                    "type": ParameterTProperty,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )
    legacy_patch_always: bool = field(
        default=False,
        metadata={
            "name": "LegacyPatchAlways",
            "type": "Attribute",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    parameter_type: str = field(
        metadata={
            "name": "ParameterType",
            "type": "Attribute",
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    access: AccessT = field(
        default=AccessT.READ_WRITE,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )
    value: str = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ProjectTAddInData:
    class Meta:
        global_type = False

    add_in_data: list[AddInDataT] = field(
        default_factory=list,
        metadata={
            "name": "AddInData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ProjectTProjectInformationHistoryEntries:
    class Meta:
        global_type = False

    history_entry: list[ProjectTProjectInformationHistoryEntriesHistoryEntry] = field(
        default_factory=list,
        metadata={
            "name": "HistoryEntry",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ProjectTProjectInformationProjectTraces:
    class Meta:
        global_type = False

    project_trace: ProjectTraceT = field(
        metadata={
            "name": "ProjectTrace",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )


@dataclass(slots=True, kw_only=True)
class ProjectTUserFiles:
    class Meta:
        global_type = False

    user_file: list[UserFileT] = field(
        default_factory=list,
        metadata={
            "name": "UserFile",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class RegistrationInfoT:
    """
    :ivar registration_status: registration-relevant
    :ivar registration_number: registration-relevant
    :ivar original_registration_number: registration-relevant
    :ivar registration_date: registration-relevant
    :ivar registration_signature: registration-relevant
    :ivar registration_key: registration-relevant
    """

    class Meta:
        name = "RegistrationInfo_t"

    registration_status: RegistrationStatusT = field(
        metadata={
            "name": "RegistrationStatus",
            "type": "Attribute",
        }
    )
    registration_number: None | str = field(
        default=None,
        metadata={
            "name": "RegistrationNumber",
            "type": "Attribute",
            "pattern": r"\d{4}/\d+",
        },
    )
    original_registration_number: None | str = field(
        default=None,
        metadata={
            "name": "OriginalRegistrationNumber",
            "type": "Attribute",
            "pattern": r"\d{4}/\d+",
        },
    )
    registration_date: None | XmlDate = field(
        default=None,
        metadata={
            "name": "RegistrationDate",
            "type": "Attribute",
        },
    )
    registration_signature: None | bytes = field(
        default=None,
        metadata={
            "name": "RegistrationSignature",
            "type": "Attribute",
            "format": "base64",
        },
    )
    registration_key: RegistrationInfoTRegistrationKey = field(
        default=RegistrationInfoTRegistrationKey.KNXCONV,
        metadata={
            "name": "RegistrationKey",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ResourceLocationT:
    class Meta:
        name = "ResourceLocation_t"

    address_space: ResourceAddrSpaceT = field(
        metadata={
            "name": "AddressSpace",
            "type": "Attribute",
        }
    )
    interface_object_ref: None | int = field(
        default=None,
        metadata={
            "name": "InterfaceObjectRef",
            "type": "Attribute",
        },
    )
    property_id: None | int = field(
        default=None,
        metadata={
            "name": "PropertyID",
            "type": "Attribute",
        },
    )
    start_address: None | int = field(
        default=None,
        metadata={
            "name": "StartAddress",
            "type": "Attribute",
        },
    )
    occurrence: int = field(
        default=0,
        metadata={
            "name": "Occurrence",
            "type": "Attribute",
        },
    )
    ptr_resource: None | ResourceNameT = field(
        default=None,
        metadata={
            "name": "PtrResource",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ToDoItemT:
    class Meta:
        name = "ToDoItem_t"

    description: str = field(
        metadata={
            "name": "Description",
            "type": "Attribute",
        }
    )
    object_path: None | str = field(
        default=None,
        metadata={
            "name": "ObjectPath",
            "type": "Attribute",
        },
    )
    status: ToDoStatusT = field(
        metadata={
            "name": "Status",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class TopologyTAreaLineAdditionalGroupAddresses:
    class Meta:
        global_type = False

    group_address: list[TopologyTAreaLineAdditionalGroupAddressesGroupAddress] = field(
        default_factory=list,
        metadata={
            "name": "GroupAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class TradeT:
    class Meta:
        name = "Trade_t"

    trade: list[TradeT] = field(
        default_factory=list,
        metadata={
            "name": "Trade",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    number: None | str = field(
        default=None,
        metadata={
            "name": "Number",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    completion_status: CompletionStatusT = field(
        default=CompletionStatusT.UNDEFINED,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class UnionParameterT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar parameter_type: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    :ivar text:
    :ivar access:
    :ivar value: registration-relevant
    :ivar default_union_parameter: registration-relevant
    """

    class Meta:
        name = "UnionParameter_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    parameter_type: str = field(
        metadata={
            "name": "ParameterType",
            "type": "Attribute",
        }
    )
    offset: int = field(
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        }
    )
    bit_offset: int = field(
        metadata={
            "name": "BitOffset",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 7,
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    access: AccessT = field(
        default=AccessT.READ_WRITE,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )
    value: str = field(
        metadata={
            "name": "Value",
            "type": "Attribute",
        }
    )
    default_union_parameter: bool = field(
        default=False,
        metadata={
            "name": "DefaultUnionParameter",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTCode:
    """
    :ivar absolute_segment: registration-relevant set
    :ivar relative_segment: registration-relevant set
    """

    class Meta:
        global_type = False

    absolute_segment: list[ApplicationProgramStaticTCodeAbsoluteSegment] = field(
        default_factory=list,
        metadata={
            "name": "AbsoluteSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    relative_segment: list[ApplicationProgramStaticTCodeRelativeSegment] = field(
        default_factory=list,
        metadata={
            "name": "RelativeSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTComObjectRefs:
    """
    :ivar com_object_ref: registration-relevant set This is a list to ensure deterministic
        behaviour in case of multiple active communication object refs
    """

    class Meta:
        global_type = False

    com_object_ref: list[ComObjectRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTComObjectTable:
    """
    :ivar com_object: registration-relevant set
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    """

    class Meta:
        global_type = False

    com_object: list[ComObjectT] = field(
        default_factory=list,
        metadata={
            "name": "ComObject",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    code_segment: None | str = field(
        default=None,
        metadata={
            "name": "CodeSegment",
            "type": "Attribute",
        },
    )
    offset: None | int = field(
        default=None,
        metadata={
            "name": "Offset",
            "type": "Attribute",
            "max_inclusive": 1048575,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParameterRefs:
    """
    :ivar parameter_ref: registration-relevant list This is a list to ensure deterministic
        behaviour in case of multiple active parameter refs
    """

    class Meta:
        global_type = False

    parameter_ref: list[ParameterRefT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParametersUnion:
    """
    :ivar memory_or_property:
    :ivar parameter: registration-relevant list This is a list to ensure deterministic
        behaviour in case of overlapping active parameters
    :ivar size_in_bit:
    """

    class Meta:
        global_type = False

    memory_or_property: (
        None
        | ApplicationProgramStaticTParametersUnionMemory
        | ApplicationProgramStaticTParametersUnionProperty
    ) = field(
        default=None,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Memory",
                    "type": ApplicationProgramStaticTParametersUnionMemory,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Property",
                    "type": ApplicationProgramStaticTParametersUnionProperty,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )
    parameter: list[UnionParameterT] = field(
        default_factory=list,
        metadata={
            "name": "Parameter",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
            "max_inclusive": 8388600,
        }
    )


@dataclass(slots=True, kw_only=True)
class BuildingsT:
    class Meta:
        name = "Buildings_t"

    building_part: list[BuildingPartT] = field(
        default_factory=list,
        metadata={
            "name": "BuildingPart",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefT:
    class Meta:
        name = "ComObjectInstanceRef_t"

    connectors: None | ComObjectInstanceRefTConnectors = field(
        default=None,
        metadata={
            "name": "Connectors",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    function_text: None | str = field(
        default=None,
        metadata={
            "name": "FunctionText",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    priority: None | ComObjectPriorityT = field(
        default=None,
        metadata={
            "name": "Priority",
            "type": "Attribute",
        },
    )
    read_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "ReadFlag",
            "type": "Attribute",
        },
    )
    write_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "WriteFlag",
            "type": "Attribute",
        },
    )
    communication_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "CommunicationFlag",
            "type": "Attribute",
        },
    )
    transmit_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "TransmitFlag",
            "type": "Attribute",
        },
    )
    update_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "UpdateFlag",
            "type": "Attribute",
        },
    )
    read_on_init_flag: None | EnableT = field(
        default=None,
        metadata={
            "name": "ReadOnInitFlag",
            "type": "Attribute",
        },
    )
    datapoint_type: list[str] = field(
        default_factory=list,
        metadata={
            "name": "DatapointType",
            "type": "Attribute",
            "tokens": True,
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    is_active: None | bool = field(
        default=None,
        metadata={
            "name": "IsActive",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterBlockT:
    """
    :ivar choice:
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar help_topic:
    :ivar internal_description:
    :ivar param_ref_id: registration-relevant
    """

    class Meta:
        name = "ComObjectParameterBlock_t"

    choice: list[
        ParameterSeparatorT
        | ParameterRefRefT
        | ComObjectParameterChooseT
        | BinaryDataRefT
        | ComObjectRefRefT
        | AssignT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterSeparator",
                    "type": ParameterSeparatorT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterRefRef",
                    "type": ParameterRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": ComObjectParameterChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ComObjectRefRef",
                    "type": ComObjectRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Assign",
                    "type": AssignT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    access: AccessT = field(
        default=AccessT.READ_WRITE,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )
    help_topic: None | int = field(
        default=None,
        metadata={
            "name": "HelpTopic",
            "type": "Attribute",
        },
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    param_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterChooseTWhen(WhenT):
    class Meta:
        global_type = False

    choice: list[
        ParameterSeparatorT
        | ParameterRefRefT
        | ComObjectParameterChooseT
        | BinaryDataRefT
        | ComObjectRefRefT
        | AssignT
        | ParameterBlockRenameT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterSeparator",
                    "type": ParameterSeparatorT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterRefRef",
                    "type": ParameterRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": ComObjectParameterChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ComObjectRefRef",
                    "type": ComObjectRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Assign",
                    "type": AssignT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterBlockRename",
                    "type": ParameterBlockRenameT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class GroupAddressesTGroupRanges:
    class Meta:
        global_type = False

    group_range: list[GroupRangeT] = field(
        default_factory=list,
        metadata={
            "name": "GroupRange",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 65535,
        },
    )


@dataclass(slots=True, kw_only=True)
class Hardware2ProgramT:
    """
    :ivar application_program_ref: registration-relevant list
    :ivar registration_info:
    :ivar id: registration-relevant
    :ivar medium_types:
    :ivar hash:
    """

    class Meta:
        name = "Hardware2Program_t"

    application_program_ref: list[ApplicationProgramRefT] = field(
        default_factory=list,
        metadata={
            "name": "ApplicationProgramRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 2,
        },
    )
    registration_info: None | RegistrationInfoT = field(
        default=None,
        metadata={
            "name": "RegistrationInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    medium_types: list[str] = field(
        default_factory=list,
        metadata={
            "name": "MediumTypes",
            "type": "Attribute",
            "tokens": True,
        },
    )
    hash: None | bytes = field(
        default=None,
        metadata={
            "name": "Hash",
            "type": "Attribute",
            "format": "base64",
        },
    )


@dataclass(slots=True, kw_only=True)
class HardwareTProductsProductAttributes:
    class Meta:
        global_type = False

    attribute: list[HardwareTProductsProductAttributesAttribute] = field(
        default_factory=list,
        metadata={
            "name": "Attribute",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTFeatures:
    class Meta:
        global_type = False

    feature: list[HawkConfigurationDataTFeaturesFeature] = field(
        default_factory=list,
        metadata={
            "name": "Feature",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTInterfaceObjectsInterfaceObject:
    class Meta:
        global_type = False

    property: list[HawkConfigurationDataTInterfaceObjectsInterfaceObjectProperty] = field(
        default_factory=list,
        metadata={
            "name": "Property",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    index: None | int = field(
        default=None,
        metadata={
            "name": "Index",
            "type": "Attribute",
        },
    )
    object_type: int = field(
        metadata={
            "name": "ObjectType",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTMemorySegmentsMemorySegment:
    class Meta:
        global_type = False

    location: ResourceLocationT = field(
        metadata={
            "name": "Location",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    access_rights: HawkConfigurationDataTMemorySegmentsMemorySegmentAccessRights = field(
        metadata={
            "name": "AccessRights",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    length: int = field(
        metadata={
            "name": "Length",
            "type": "Attribute",
        }
    )
    optional: bool = field(
        default=False,
        metadata={
            "name": "Optional",
            "type": "Attribute",
        },
    )
    memory_type: None | MemoryTypeT = field(
        default=None,
        metadata={
            "name": "MemoryType",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTResourcesResource:
    class Meta:
        global_type = False

    location: None | ResourceLocationT = field(
        default=None,
        metadata={
            "name": "Location",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    img_location: None | ResourceLocationT = field(
        default=None,
        metadata={
            "name": "ImgLocation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    resource_type: HawkConfigurationDataTResourcesResourceResourceType = field(
        metadata={
            "name": "ResourceType",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    access_rights: HawkConfigurationDataTResourcesResourceAccessRights = field(
        metadata={
            "name": "AccessRights",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    name: ResourceNameT = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    access: list[ResourceAccessT] = field(
        default_factory=list,
        metadata={
            "name": "Access",
            "type": "Attribute",
            "tokens": True,
        },
    )
    mgmt_style: list[ResourceMgmtStyleT] = field(
        default_factory=list,
        metadata={
            "name": "MgmtStyle",
            "type": "Attribute",
            "tokens": True,
        },
    )


@dataclass(slots=True, kw_only=True)
class LanguageDataTTranslationUnit:
    class Meta:
        global_type = False

    translation_element: list[LanguageDataTTranslationUnitTranslationElement] = field(
        default_factory=list,
        metadata={
            "name": "TranslationElement",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    version: int = field(
        default=0,
        metadata={
            "name": "Version",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProcedureT:
    class Meta:
        name = "LoadProcedure_t"

    choice: list[
        LoadProcedureTLdCtrlUnload
        | LoadProcedureTLdCtrlLoad
        | LoadProcedureTLdCtrlMaxLength
        | LoadProcedureTLdCtrlClearCachedObjectTypes
        | LoadProcedureTLdCtrlLoadCompleted
        | LoadProcedureTLdCtrlAbsSegment
        | LoadProcedureTLdCtrlRelSegment
        | LoadProcedureTLdCtrlTaskSegment
        | LoadProcedureTLdCtrlTaskPtr
        | LoadProcedureTLdCtrlTaskCtrl1
        | LoadProcedureTLdCtrlTaskCtrl2
        | LoadProcedureTLdCtrlWriteProp
        | LoadProcedureTLdCtrlCompareProp
        | LoadProcedureTLdCtrlLoadImageProp
        | LoadProcedureTLdCtrlInvokeFunctionProp
        | LoadProcedureTLdCtrlReadFunctionProp
        | LoadProcedureTLdCtrlWriteMem
        | LoadProcedureTLdCtrlCompareMem
        | LoadProcedureTLdCtrlLoadImageMem
        | LoadProcedureTLdCtrlWriteRelMem
        | LoadProcedureTLdCtrlCompareRelMem
        | LoadProcedureTLdCtrlLoadImageRelMem
        | LoadProcedureTLdCtrlConnect
        | LoadProcedureTLdCtrlDisconnect
        | LoadProcedureTLdCtrlRestart
        | LoadProcedureTLdCtrlDelay
        | LoadProcedureTLdCtrlSetControlVariable
        | LoadProcedureTLdCtrlMapError
        | LoadProcedureTLdCtrlProgressText
        | LoadProcedureTLdCtrlDeclarePropDesc
        | LoadProcedureTLdCtrlClearLcfilterTable
        | LoadProcedureTLdCtrlMerge
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "LdCtrlUnload",
                    "type": LoadProcedureTLdCtrlUnload,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlLoad",
                    "type": LoadProcedureTLdCtrlLoad,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlMaxLength",
                    "type": LoadProcedureTLdCtrlMaxLength,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlClearCachedObjectTypes",
                    "type": LoadProcedureTLdCtrlClearCachedObjectTypes,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlLoadCompleted",
                    "type": LoadProcedureTLdCtrlLoadCompleted,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlAbsSegment",
                    "type": LoadProcedureTLdCtrlAbsSegment,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlRelSegment",
                    "type": LoadProcedureTLdCtrlRelSegment,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlTaskSegment",
                    "type": LoadProcedureTLdCtrlTaskSegment,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlTaskPtr",
                    "type": LoadProcedureTLdCtrlTaskPtr,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlTaskCtrl1",
                    "type": LoadProcedureTLdCtrlTaskCtrl1,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlTaskCtrl2",
                    "type": LoadProcedureTLdCtrlTaskCtrl2,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlWriteProp",
                    "type": LoadProcedureTLdCtrlWriteProp,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlCompareProp",
                    "type": LoadProcedureTLdCtrlCompareProp,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlLoadImageProp",
                    "type": LoadProcedureTLdCtrlLoadImageProp,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlInvokeFunctionProp",
                    "type": LoadProcedureTLdCtrlInvokeFunctionProp,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlReadFunctionProp",
                    "type": LoadProcedureTLdCtrlReadFunctionProp,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlWriteMem",
                    "type": LoadProcedureTLdCtrlWriteMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlCompareMem",
                    "type": LoadProcedureTLdCtrlCompareMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlLoadImageMem",
                    "type": LoadProcedureTLdCtrlLoadImageMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlWriteRelMem",
                    "type": LoadProcedureTLdCtrlWriteRelMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlCompareRelMem",
                    "type": LoadProcedureTLdCtrlCompareRelMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlLoadImageRelMem",
                    "type": LoadProcedureTLdCtrlLoadImageRelMem,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlConnect",
                    "type": LoadProcedureTLdCtrlConnect,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlDisconnect",
                    "type": LoadProcedureTLdCtrlDisconnect,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlRestart",
                    "type": LoadProcedureTLdCtrlRestart,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlDelay",
                    "type": LoadProcedureTLdCtrlDelay,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlSetControlVariable",
                    "type": LoadProcedureTLdCtrlSetControlVariable,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlMapError",
                    "type": LoadProcedureTLdCtrlMapError,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlProgressText",
                    "type": LoadProcedureTLdCtrlProgressText,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlDeclarePropDesc",
                    "type": LoadProcedureTLdCtrlDeclarePropDesc,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlClearLCFilterTable",
                    "type": LoadProcedureTLdCtrlClearLcfilterTable,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "LdCtrlMerge",
                    "type": LoadProcedureTLdCtrlMerge,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerBaggages:
    class Meta:
        global_type = False

    baggage: list[ManufacturerDataTManufacturerBaggagesBaggage] = field(
        default_factory=list,
        metadata={
            "name": "Baggage",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerCatalog:
    class Meta:
        global_type = False

    catalog_section: list[CatalogSectionT] = field(
        default_factory=list,
        metadata={
            "name": "CatalogSection",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTDatapointTypesDatapointType:
    class Meta:
        global_type = False

    datapoint_subtypes: None | MasterDataTDatapointTypesDatapointTypeDatapointSubtypes = field(
        default=None,
        metadata={
            "name": "DatapointSubtypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    number: int = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    size_in_bit: int = field(
        metadata={
            "name": "SizeInBit",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterBlockT:
    """
    :ivar choice:
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar help_topic:
    :ivar internal_description:
    """

    class Meta:
        name = "ParameterBlock_t"

    choice: list[
        ParameterSeparatorT | ParameterRefRefT | ParameterChooseT | BinaryDataRefT | AssignT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterSeparator",
                    "type": ParameterSeparatorT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterRefRef",
                    "type": ParameterRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": ParameterChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Assign",
                    "type": AssignT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    access: AccessT = field(
        default=AccessT.READ_WRITE,
        metadata={
            "name": "Access",
            "type": "Attribute",
        },
    )
    help_topic: None | int = field(
        default=None,
        metadata={
            "name": "HelpTopic",
            "type": "Attribute",
        },
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterCalculationTLparameters:
    """
    :ivar parameter_ref_ref: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_ref_ref: list[ParameterCalculationTLparametersParameterRefRef] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterCalculationTRparameters:
    """
    :ivar parameter_ref_ref: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_ref_ref: list[ParameterCalculationTRparametersParameterRefRef] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterChooseTWhen(WhenT):
    class Meta:
        global_type = False

    choice: list[
        ParameterSeparatorT
        | ParameterRefRefT
        | ParameterChooseT
        | BinaryDataRefT
        | AssignT
        | ParameterBlockRenameT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterSeparator",
                    "type": ParameterSeparatorT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterRefRef",
                    "type": ParameterRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": ParameterChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Assign",
                    "type": AssignT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterBlockRename",
                    "type": ParameterBlockRenameT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterTypeT:
    """
    :ivar choice:
    :ivar id: registration-relevant
    :ivar name: registration-relevant
    :ivar internal_description:
    :ivar plugin:
    """

    class Meta:
        name = "ParameterType_t"

    choice: (
        None
        | ParameterTypeTTypeNumber
        | ParameterTypeTTypeFloat
        | ParameterTypeTTypeRestriction
        | ParameterTypeTTypeText
        | ParameterTypeTTypeTime
        | ParameterTypeTTypeDate
        | ParameterTypeTTypeIpaddress
        | object
    ) = field(
        default=None,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "TypeNumber",
                    "type": ParameterTypeTTypeNumber,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeFloat",
                    "type": ParameterTypeTTypeFloat,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeRestriction",
                    "type": ParameterTypeTTypeRestriction,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeText",
                    "type": ParameterTypeTTypeText,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeTime",
                    "type": ParameterTypeTTypeTime,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeDate",
                    "type": ParameterTypeTTypeDate,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeIPAddress",
                    "type": ParameterTypeTTypeIpaddress,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "TypeNone",
                    "type": object,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    plugin: None | str = field(
        default=None,
        metadata={
            "name": "Plugin",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ProjectTProjectInformationToDoItems:
    class Meta:
        global_type = False

    to_do_item: ToDoItemT = field(
        metadata={
            "name": "ToDoItem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )


@dataclass(slots=True, kw_only=True)
class TradesT:
    class Meta:
        name = "Trades_t"

    trade: list[TradeT] = field(
        default_factory=list,
        metadata={
            "name": "Trade",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramChannelT:
    """
    :ivar choice:
    :ivar name:
    :ivar text:
    :ivar number: registration-relevant
    :ivar id: registration-relevant
    """

    class Meta:
        name = "ApplicationProgramChannel_t"

    choice: list[ComObjectParameterBlockT | ComObjectRefRefT | BinaryDataRefT | ChannelChooseT] = (
        field(
            default_factory=list,
            metadata={
                "type": "Elements",
                "choices": (
                    {
                        "name": "ParameterBlock",
                        "type": ComObjectParameterBlockT,
                        "namespace": "http://knx.org/xml/project/10",
                    },
                    {
                        "name": "ComObjectRefRef",
                        "type": ComObjectRefRefT,
                        "namespace": "http://knx.org/xml/project/10",
                    },
                    {
                        "name": "BinaryDataRef",
                        "type": BinaryDataRefT,
                        "namespace": "http://knx.org/xml/project/10",
                    },
                    {
                        "name": "choose",
                        "type": ChannelChooseT,
                        "namespace": "http://knx.org/xml/project/10",
                    },
                ),
            },
        )
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    text: None | str = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    number: str = field(
        metadata={
            "name": "Number",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramDynamicTChannelIndependentBlock:
    class Meta:
        global_type = False

    parameter_block_or_choose_or_binary_data_ref: list[
        ParameterBlockT | IndependentParameterBlockChooseT | BinaryDataRefT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterBlock",
                    "type": ParameterBlockT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": IndependentParameterBlockChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParameterTypes:
    """
    :ivar parameter_type: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_type: list[ParameterTypeT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterType",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParameters:
    class Meta:
        global_type = False

    parameter_or_union: list[ParameterT | ApplicationProgramStaticTParametersUnion] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Parameter",
                    "type": ParameterT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Union",
                    "type": ApplicationProgramStaticTParametersUnion,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class ChannelChooseTWhen(WhenT):
    class Meta:
        global_type = False

    choice: list[
        ComObjectParameterBlockT
        | ComObjectRefRefT
        | BinaryDataRefT
        | ChannelChooseT
        | ParameterBlockRenameT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterBlock",
                    "type": ComObjectParameterBlockT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ComObjectRefRef",
                    "type": ComObjectRefRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "BinaryDataRef",
                    "type": BinaryDataRefT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": ChannelChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterBlockRename",
                    "type": ParameterBlockRenameT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceTComObjectInstanceRefs:
    class Meta:
        global_type = False

    com_object_instance_ref: list[ComObjectInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class GroupAddressesT:
    class Meta:
        name = "GroupAddresses_t"

    group_ranges: GroupAddressesTGroupRanges = field(
        metadata={
            "name": "GroupRanges",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )


@dataclass(slots=True, kw_only=True)
class HardwareTHardware2Programs:
    class Meta:
        global_type = False

    hardware2_program: list[Hardware2ProgramT] = field(
        default_factory=list,
        metadata={
            "name": "Hardware2Program",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HardwareTProductsProduct:
    """
    :ivar baggages:
    :ivar attributes:
    :ivar registration_info:
    :ivar id: registration-relevant
    :ivar text:
    :ivar order_number: registration-relevant
    :ivar is_rail_mounted:
    :ivar width_in_millimeter:
    :ivar visible_description:
    :ivar default_language:
    :ivar non_reg_relevant_data_version:
    :ivar hash:
    """

    class Meta:
        global_type = False

    baggages: None | HardwareTProductsProductBaggages = field(
        default=None,
        metadata={
            "name": "Baggages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    attributes: None | HardwareTProductsProductAttributes = field(
        default=None,
        metadata={
            "name": "Attributes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    registration_info: None | RegistrationInfoT = field(
        default=None,
        metadata={
            "name": "RegistrationInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    order_number: str = field(
        metadata={
            "name": "OrderNumber",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    is_rail_mounted: bool = field(
        metadata={
            "name": "IsRailMounted",
            "type": "Attribute",
        }
    )
    width_in_millimeter: None | float = field(
        default=None,
        metadata={
            "name": "WidthInMillimeter",
            "type": "Attribute",
        },
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    default_language: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLanguage",
            "type": "Attribute",
        },
    )
    non_reg_relevant_data_version: int = field(
        default=0,
        metadata={
            "name": "NonRegRelevantDataVersion",
            "type": "Attribute",
        },
    )
    hash: None | bytes = field(
        default=None,
        metadata={
            "name": "Hash",
            "type": "Attribute",
            "format": "base64",
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTInterfaceObjects:
    class Meta:
        global_type = False

    interface_object: list[HawkConfigurationDataTInterfaceObjectsInterfaceObject] = field(
        default_factory=list,
        metadata={
            "name": "InterfaceObject",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTMemorySegments:
    class Meta:
        global_type = False

    memory_segment: list[HawkConfigurationDataTMemorySegmentsMemorySegment] = field(
        default_factory=list,
        metadata={
            "name": "MemorySegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTProceduresProcedure(LoadProcedureT):
    class Meta:
        global_type = False

    procedure_type: ProcedureTypeT = field(
        metadata={
            "name": "ProcedureType",
            "type": "Attribute",
        }
    )
    procedure_sub_type: LdCtrlProcTypeT | HawkConfigurationDataTProceduresProcedureValue = field(
        metadata={
            "name": "ProcedureSubType",
            "type": "Attribute",
        }
    )
    access: list[ResourceAccessT] = field(
        default_factory=list,
        metadata={
            "name": "Access",
            "type": "Attribute",
            "tokens": True,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTResources:
    class Meta:
        global_type = False

    resource: list[HawkConfigurationDataTResourcesResource] = field(
        default_factory=list,
        metadata={
            "name": "Resource",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class IndependentParameterBlockChooseTWhen(WhenT):
    class Meta:
        global_type = False

    parameter_block_or_choose_or_parameter_block_rename: list[
        ParameterBlockT | IndependentParameterBlockChooseT | ParameterBlockRenameT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ParameterBlock",
                    "type": ParameterBlockT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": IndependentParameterBlockChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterBlockRename",
                    "type": ParameterBlockRenameT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class LanguageDataT:
    class Meta:
        name = "LanguageData_t"

    translation_unit: list[LanguageDataTTranslationUnit] = field(
        default_factory=list,
        metadata={
            "name": "TranslationUnit",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )
    identifier: str = field(
        metadata={
            "name": "Identifier",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LoadProceduresTLoadProcedure(LoadProcedureT):
    """
    :ivar merge_id: registration-relevant
    """

    class Meta:
        global_type = False

    merge_id: None | int = field(
        default=None,
        metadata={
            "name": "MergeId",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTDatapointTypes:
    class Meta:
        global_type = False

    datapoint_type: list[MasterDataTDatapointTypesDatapointType] = field(
        default_factory=list,
        metadata={
            "name": "DatapointType",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterCalculationT:
    """
    :ivar rltransformation: registration-relevant
    :ivar lrtransformation: registration-relevant
    :ivar lparameters:
    :ivar rparameters:
    :ivar id: registration-relevant
    :ivar language: registration-relevant
    :ivar name:
    """

    class Meta:
        name = "ParameterCalculation_t"

    rltransformation: str = field(
        metadata={
            "name": "RLTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    lrtransformation: str = field(
        metadata={
            "name": "LRTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    lparameters: ParameterCalculationTLparameters = field(
        metadata={
            "name": "LParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    rparameters: ParameterCalculationTRparameters = field(
        metadata={
            "name": "RParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    language: ParameterCalculationTLanguage = field(
        metadata={
            "name": "Language",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )


@dataclass(slots=True, kw_only=True)
class ProjectTProjectInformation:
    class Meta:
        global_type = False

    history_entries: None | ProjectTProjectInformationHistoryEntries = field(
        default=None,
        metadata={
            "name": "HistoryEntries",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    to_do_items: None | ProjectTProjectInformationToDoItems = field(
        default=None,
        metadata={
            "name": "ToDoItems",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    project_traces: None | ProjectTProjectInformationProjectTraces = field(
        default=None,
        metadata={
            "name": "ProjectTraces",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    group_address_style: GroupAddressStyleT = field(
        metadata={
            "name": "GroupAddressStyle",
            "type": "Attribute",
        }
    )
    project_number: None | str = field(
        default=None,
        metadata={
            "name": "ProjectNumber",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    contract_number: None | str = field(
        default=None,
        metadata={
            "name": "ContractNumber",
            "type": "Attribute",
            "max_length": 50,
        },
    )
    last_modified: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "LastModified",
            "type": "Attribute",
        },
    )
    project_start: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "ProjectStart",
            "type": "Attribute",
        },
    )
    project_end: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "ProjectEnd",
            "type": "Attribute",
        },
    )
    project_id: None | int = field(
        default=None,
        metadata={
            "name": "ProjectId",
            "type": "Attribute",
            "max_inclusive": 4095,
        },
    )
    project_password: None | str = field(
        default=None,
        metadata={
            "name": "ProjectPassword",
            "type": "Attribute",
            "max_length": 20,
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    completion_status: CompletionStatusT = field(
        default=CompletionStatusT.UNDEFINED,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    project_tracing_level: ProjectTracingLevelT = field(
        default=ProjectTracingLevelT.NONE,
        metadata={
            "name": "ProjectTracingLevel",
            "type": "Attribute",
        },
    )
    hide16_bit_groups_from_legacy_plugins: bool = field(
        default=False,
        metadata={
            "name": "Hide16BitGroupsFromLegacyPlugins",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramDynamicT:
    class Meta:
        name = "ApplicationProgramDynamic_t"

    channel_independent_block_or_channel_or_choose: list[
        ApplicationProgramDynamicTChannelIndependentBlock
        | ApplicationProgramChannelT
        | DependentChannelChooseT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "ChannelIndependentBlock",
                    "type": ApplicationProgramDynamicTChannelIndependentBlock,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "Channel",
                    "type": ApplicationProgramChannelT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": DependentChannelChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticTParameterCalculations:
    """
    :ivar parameter_calculation: registration-relevant set
    """

    class Meta:
        global_type = False

    parameter_calculation: list[ParameterCalculationT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterCalculation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class DependentChannelChooseTWhen(WhenT):
    class Meta:
        global_type = False

    channel_or_choose_or_parameter_block_rename: list[
        ApplicationProgramChannelT | DependentChannelChooseT | ParameterBlockRenameT
    ] = field(
        default_factory=list,
        metadata={
            "type": "Elements",
            "choices": (
                {
                    "name": "Channel",
                    "type": ApplicationProgramChannelT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "choose",
                    "type": DependentChannelChooseT,
                    "namespace": "http://knx.org/xml/project/10",
                },
                {
                    "name": "ParameterBlockRename",
                    "type": ParameterBlockRenameT,
                    "namespace": "http://knx.org/xml/project/10",
                },
            ),
        },
    )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceT:
    class Meta:
        name = "DeviceInstance_t"

    parameter_instance_refs: None | DeviceInstanceTParameterInstanceRefs = field(
        default=None,
        metadata={
            "name": "ParameterInstanceRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    com_object_instance_refs: None | DeviceInstanceTComObjectInstanceRefs = field(
        default=None,
        metadata={
            "name": "ComObjectInstanceRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    additional_addresses: None | DeviceInstanceTAdditionalAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalAddresses",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    binary_data: None | DeviceInstanceTBinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    ipconfig: None | IpconfigT = field(
        default=None,
        metadata={
            "name": "IPConfig",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    product_ref_id: str = field(
        metadata={
            "name": "ProductRefId",
            "type": "Attribute",
        }
    )
    hardware2_program_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "Hardware2ProgramRefId",
            "type": "Attribute",
        },
    )
    address: None | int = field(
        default=None,
        metadata={
            "name": "Address",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 255,
        },
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    last_modified: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "LastModified",
            "type": "Attribute",
        },
    )
    last_download: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "LastDownload",
            "type": "Attribute",
        },
    )
    installation_hints: None | str = field(
        default=None,
        metadata={
            "name": "InstallationHints",
            "type": "Attribute",
        },
    )
    completion_status: CompletionStatusT = field(
        default=CompletionStatusT.UNDEFINED,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    individual_address_loaded: bool = field(
        default=False,
        metadata={
            "name": "IndividualAddressLoaded",
            "type": "Attribute",
        },
    )
    application_program_loaded: bool = field(
        default=False,
        metadata={
            "name": "ApplicationProgramLoaded",
            "type": "Attribute",
        },
    )
    parameters_loaded: bool = field(
        default=False,
        metadata={
            "name": "ParametersLoaded",
            "type": "Attribute",
        },
    )
    communication_part_loaded: bool = field(
        default=False,
        metadata={
            "name": "CommunicationPartLoaded",
            "type": "Attribute",
        },
    )
    medium_config_loaded: bool = field(
        default=False,
        metadata={
            "name": "MediumConfigLoaded",
            "type": "Attribute",
        },
    )
    loaded_image: None | bytes = field(
        default=None,
        metadata={
            "name": "LoadedImage",
            "type": "Attribute",
            "format": "base64",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    check_sums: None | bytes = field(
        default=None,
        metadata={
            "name": "CheckSums",
            "type": "Attribute",
            "format": "base64",
        },
    )
    is_communication_object_visibility_calculated: None | bool = field(
        default=None,
        metadata={
            "name": "IsCommunicationObjectVisibilityCalculated",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class HardwareTProducts:
    class Meta:
        global_type = False

    product: list[HardwareTProductsProduct] = field(
        default_factory=list,
        metadata={
            "name": "Product",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataTProcedures:
    class Meta:
        global_type = False

    procedure: list[HawkConfigurationDataTProceduresProcedure] = field(
        default_factory=list,
        metadata={
            "name": "Procedure",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class LoadProceduresT:
    """
    :ivar load_procedure: registration-relevant set
    """

    class Meta:
        name = "LoadProcedures_t"

    load_procedure: list[LoadProceduresTLoadProcedure] = field(
        default_factory=list,
        metadata={
            "name": "LoadProcedure",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerLanguages:
    class Meta:
        global_type = False

    language: list[LanguageDataT] = field(
        default_factory=list,
        metadata={
            "name": "Language",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTLanguages:
    class Meta:
        global_type = False

    language: list[LanguageDataT] = field(
        default_factory=list,
        metadata={
            "name": "Language",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticT:
    class Meta:
        name = "ApplicationProgramStatic_t"

    code: None | ApplicationProgramStaticTCode = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    parameter_types: None | ApplicationProgramStaticTParameterTypes = field(
        default=None,
        metadata={
            "name": "ParameterTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    parameters: None | ApplicationProgramStaticTParameters = field(
        default=None,
        metadata={
            "name": "Parameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    parameter_refs: None | ApplicationProgramStaticTParameterRefs = field(
        default=None,
        metadata={
            "name": "ParameterRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    parameter_calculations: None | ApplicationProgramStaticTParameterCalculations = field(
        default=None,
        metadata={
            "name": "ParameterCalculations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    com_object_table: None | ApplicationProgramStaticTComObjectTable = field(
        default=None,
        metadata={
            "name": "ComObjectTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    com_object_refs: None | ApplicationProgramStaticTComObjectRefs = field(
        default=None,
        metadata={
            "name": "ComObjectRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    address_table: None | ApplicationProgramStaticTAddressTable = field(
        default=None,
        metadata={
            "name": "AddressTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    association_table: None | ApplicationProgramStaticTAssociationTable = field(
        default=None,
        metadata={
            "name": "AssociationTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    fixup_list: None | ApplicationProgramStaticTFixupList = field(
        default=None,
        metadata={
            "name": "FixupList",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    load_procedures: None | LoadProceduresT = field(
        default=None,
        metadata={
            "name": "LoadProcedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    extension: None | ApplicationProgramStaticTExtension = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    binary_data: None | ApplicationProgramStaticTBinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    device_compare: None | ApplicationProgramStaticTDeviceCompare = field(
        default=None,
        metadata={
            "name": "DeviceCompare",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    options: None | ApplicationProgramStaticTOptions = field(
        default=None,
        metadata={
            "name": "Options",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class HardwareT:
    """
    :ivar products:
    :ivar hardware2_programs:
    :ivar id: registration-relevant
    :ivar name:
    :ivar serial_number: registration-relevant
    :ivar version_number: registration-relevant
    :ivar bus_current:
    :ivar is_accessory: registration-relevant
    :ivar has_individual_address: registration-relevant
    :ivar has_application_program: registration-relevant
    :ivar has_application_program2: registration-relevant
    :ivar is_power_supply: registration-relevant
    :ivar is_choke: registration-relevant
    :ivar is_coupler: registration-relevant
    :ivar is_power_line_repeater: registration-relevant
    :ivar is_power_line_signal_filter: registration-relevant
    :ivar is_cable: registration-relevant
    :ivar is_ipenabled: registration-relevant
    :ivar original_manufacturer: registration-relevant
    :ivar no_download_without_plugin:
    :ivar non_reg_relevant_data_version:
    """

    class Meta:
        name = "Hardware_t"

    products: None | HardwareTProducts = field(
        default=None,
        metadata={
            "name": "Products",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    hardware2_programs: None | HardwareTHardware2Programs = field(
        default=None,
        metadata={
            "name": "Hardware2Programs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    serial_number: str = field(
        metadata={
            "name": "SerialNumber",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    version_number: int = field(
        metadata={
            "name": "VersionNumber",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 32767,
        }
    )
    bus_current: None | float = field(
        default=None,
        metadata={
            "name": "BusCurrent",
            "type": "Attribute",
        },
    )
    is_accessory: bool = field(
        default=False,
        metadata={
            "name": "IsAccessory",
            "type": "Attribute",
        },
    )
    has_individual_address: bool = field(
        metadata={
            "name": "HasIndividualAddress",
            "type": "Attribute",
        }
    )
    has_application_program: bool = field(
        metadata={
            "name": "HasApplicationProgram",
            "type": "Attribute",
        }
    )
    has_application_program2: bool = field(
        default=False,
        metadata={
            "name": "HasApplicationProgram2",
            "type": "Attribute",
        },
    )
    is_power_supply: bool = field(
        default=False,
        metadata={
            "name": "IsPowerSupply",
            "type": "Attribute",
        },
    )
    is_choke: bool = field(
        default=False,
        metadata={
            "name": "IsChoke",
            "type": "Attribute",
        },
    )
    is_coupler: bool = field(
        default=False,
        metadata={
            "name": "IsCoupler",
            "type": "Attribute",
        },
    )
    is_power_line_repeater: bool = field(
        default=False,
        metadata={
            "name": "IsPowerLineRepeater",
            "type": "Attribute",
        },
    )
    is_power_line_signal_filter: bool = field(
        default=False,
        metadata={
            "name": "IsPowerLineSignalFilter",
            "type": "Attribute",
        },
    )
    is_cable: bool = field(
        default=False,
        metadata={
            "name": "IsCable",
            "type": "Attribute",
        },
    )
    is_ipenabled: bool = field(
        default=False,
        metadata={
            "name": "IsIPEnabled",
            "type": "Attribute",
        },
    )
    original_manufacturer: None | str = field(
        default=None,
        metadata={
            "name": "OriginalManufacturer",
            "type": "Attribute",
        },
    )
    no_download_without_plugin: bool = field(
        default=False,
        metadata={
            "name": "NoDownloadWithoutPlugin",
            "type": "Attribute",
        },
    )
    non_reg_relevant_data_version: int = field(
        default=0,
        metadata={
            "name": "NonRegRelevantDataVersion",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataT:
    class Meta:
        name = "HawkConfigurationData_t"

    features: None | HawkConfigurationDataTFeatures = field(
        default=None,
        metadata={
            "name": "Features",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    resources: None | HawkConfigurationDataTResources = field(
        default=None,
        metadata={
            "name": "Resources",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    procedures: None | HawkConfigurationDataTProcedures = field(
        default=None,
        metadata={
            "name": "Procedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    memory_segments: None | HawkConfigurationDataTMemorySegments = field(
        default=None,
        metadata={
            "name": "MemorySegments",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    interface_objects: None | HawkConfigurationDataTInterfaceObjects = field(
        default=None,
        metadata={
            "name": "InterfaceObjects",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    ets3_system_plugin: None | str = field(
        default=None,
        metadata={
            "name": "Ets3SystemPlugin",
            "type": "Attribute",
            "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        },
    )
    legacy_version: None | int = field(
        default=None,
        metadata={
            "name": "LegacyVersion",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class TopologyTAreaLine:
    class Meta:
        global_type = False

    device_instance: list[DeviceInstanceT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstance",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    bus_access: None | BusAccessT = field(
        default=None,
        metadata={
            "name": "BusAccess",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    additional_group_addresses: None | TopologyTAreaLineAdditionalGroupAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalGroupAddresses",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 15,
        }
    )
    medium_type_ref_id: str = field(
        metadata={
            "name": "MediumTypeRefId",
            "type": "Attribute",
        }
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    domain_address: None | int = field(
        default=None,
        metadata={
            "name": "DomainAddress",
            "type": "Attribute",
        },
    )
    domain_address_is_checked: bool = field(
        default=False,
        metadata={
            "name": "DomainAddressIsChecked",
            "type": "Attribute",
        },
    )
    iprouting_multicast_address: str = field(
        default="224.0.23.12",
        metadata={
            "name": "IPRoutingMulticastAddress",
            "type": "Attribute",
            "pattern": r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])",
        },
    )
    multicast_ttl: int = field(
        default=16,
        metadata={
            "name": "MulticastTTL",
            "type": "Attribute",
        },
    )
    completion_status: None | CompletionStatusT = field(
        default=None,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class TopologyTUnassignedDevices:
    class Meta:
        global_type = False

    device_instance: list[DeviceInstanceT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstance",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramT:
    """
    :ivar static:
    :ivar dynamic:
    :ivar id: registration-relevant
    :ivar application_number: registration-relevant
    :ivar application_version: registration-relevant
    :ivar program_type: registration-relevant
    :ivar mask_version: registration-relevant
    :ivar visible_description:
    :ivar name:
    :ivar load_procedure_style: registration-relevant
    :ivar pei_type: registration-relevant
    :ivar help_topic:
    :ivar help_file:
    :ivar default_language:
    :ivar dynamic_table_management: registration-relevant
    :ivar linkable: registration-relevant
    :ivar min_ets_version:
    :ivar original_manufacturer: registration-relevant
    :ivar pre_ets4_style: registration-relevant
    :ivar converted_from_pre_ets4_data: registration-relevant
    :ivar ipconfig: registration-relevant
    :ivar additional_addresses_count: registration-relevant
    :ivar non_reg_relevant_data_version:
    :ivar broken:
    :ivar download_info_incomplete:
    :ivar replaces_versions: registration-relevant
    :ivar hash:
    """

    class Meta:
        name = "ApplicationProgram_t"

    static: ApplicationProgramStaticT = field(
        metadata={
            "name": "Static",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    dynamic: None | ApplicationProgramDynamicT = field(
        default=None,
        metadata={
            "name": "Dynamic",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    application_number: int = field(
        metadata={
            "name": "ApplicationNumber",
            "type": "Attribute",
        }
    )
    application_version: int = field(
        metadata={
            "name": "ApplicationVersion",
            "type": "Attribute",
        }
    )
    program_type: ApplicationProgramTypeT = field(
        metadata={
            "name": "ProgramType",
            "type": "Attribute",
        }
    )
    mask_version: str = field(
        metadata={
            "name": "MaskVersion",
            "type": "Attribute",
        }
    )
    visible_description: None | str = field(
        default=None,
        metadata={
            "name": "VisibleDescription",
            "type": "Attribute",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    load_procedure_style: LoadProcedureStyleT = field(
        metadata={
            "name": "LoadProcedureStyle",
            "type": "Attribute",
        }
    )
    pei_type: int = field(
        metadata={
            "name": "PeiType",
            "type": "Attribute",
        }
    )
    help_topic: None | int = field(
        default=None,
        metadata={
            "name": "HelpTopic",
            "type": "Attribute",
        },
    )
    help_file: None | str = field(
        default=None,
        metadata={
            "name": "HelpFile",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    default_language: str = field(
        metadata={
            "name": "DefaultLanguage",
            "type": "Attribute",
        }
    )
    dynamic_table_management: bool = field(
        metadata={
            "name": "DynamicTableManagement",
            "type": "Attribute",
        }
    )
    linkable: bool = field(
        metadata={
            "name": "Linkable",
            "type": "Attribute",
        }
    )
    min_ets_version: None | ApplicationProgramTMinEtsVersion = field(
        default=None,
        metadata={
            "name": "MinEtsVersion",
            "type": "Attribute",
        },
    )
    original_manufacturer: None | str = field(
        default=None,
        metadata={
            "name": "OriginalManufacturer",
            "type": "Attribute",
        },
    )
    pre_ets4_style: bool = field(
        default=False,
        metadata={
            "name": "PreEts4Style",
            "type": "Attribute",
        },
    )
    converted_from_pre_ets4_data: bool = field(
        default=False,
        metadata={
            "name": "ConvertedFromPreEts4Data",
            "type": "Attribute",
        },
    )
    ipconfig: ApplicationProgramIpconfigT = field(
        default=ApplicationProgramIpconfigT.TOOL,
        metadata={
            "name": "IPConfig",
            "type": "Attribute",
        },
    )
    additional_addresses_count: int = field(
        default=0,
        metadata={
            "name": "AdditionalAddressesCount",
            "type": "Attribute",
        },
    )
    non_reg_relevant_data_version: int = field(
        default=0,
        metadata={
            "name": "NonRegRelevantDataVersion",
            "type": "Attribute",
        },
    )
    broken: bool = field(
        default=False,
        metadata={
            "name": "Broken",
            "type": "Attribute",
        },
    )
    download_info_incomplete: bool = field(
        default=False,
        metadata={
            "name": "DownloadInfoIncomplete",
            "type": "Attribute",
        },
    )
    replaces_versions: list[int] = field(
        default_factory=list,
        metadata={
            "name": "ReplacesVersions",
            "type": "Attribute",
            "tokens": True,
        },
    )
    hash: None | bytes = field(
        default=None,
        metadata={
            "name": "Hash",
            "type": "Attribute",
            "format": "base64",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerHardware:
    class Meta:
        global_type = False

    hardware: list[HardwareT] = field(
        default_factory=list,
        metadata={
            "name": "Hardware",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MaskVersionT:
    class Meta:
        name = "MaskVersion_t"

    downward_compatible_masks: None | MaskVersionTDownwardCompatibleMasks = field(
        default=None,
        metadata={
            "name": "DownwardCompatibleMasks",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    mask_entries: None | MaskVersionTMaskEntries = field(
        default=None,
        metadata={
            "name": "MaskEntries",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    hawk_configuration_data: list[HawkConfigurationDataT] = field(
        default_factory=list,
        metadata={
            "name": "HawkConfigurationData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    mask_version: int = field(
        metadata={
            "name": "MaskVersion",
            "type": "Attribute",
        }
    )
    mgmt_descriptor01: None | bytes = field(
        default=None,
        metadata={
            "name": "MgmtDescriptor01",
            "type": "Attribute",
            "format": "base16",
        },
    )
    management_model: MaskVersionTManagementModel = field(
        metadata={
            "name": "ManagementModel",
            "type": "Attribute",
        }
    )
    medium_type_ref_id: str = field(
        metadata={
            "name": "MediumTypeRefId",
            "type": "Attribute",
        }
    )
    other_medium_type_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "OtherMediumTypeRefId",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class TopologyTArea:
    class Meta:
        global_type = False

    line: list[TopologyTAreaLine] = field(
        default_factory=list,
        metadata={
            "name": "Line",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 16,
        },
    )
    id: None | str = field(
        default=None,
        metadata={
            "name": "Id",
            "type": "Attribute",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    address: int = field(
        metadata={
            "name": "Address",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 15,
        }
    )
    comment: None | str = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        },
    )
    completion_status: None | CompletionStatusT = field(
        default=None,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturerApplicationPrograms:
    class Meta:
        global_type = False

    application_program: list[ApplicationProgramT] = field(
        default_factory=list,
        metadata={
            "name": "ApplicationProgram",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class MasterDataTMaskVersions:
    class Meta:
        global_type = False

    mask_version: list[MaskVersionT] = field(
        default_factory=list,
        metadata={
            "name": "MaskVersion",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class TopologyT:
    class Meta:
        name = "Topology_t"

    area: list[TopologyTArea] = field(
        default_factory=list,
        metadata={
            "name": "Area",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "max_occurs": 16,
        },
    )
    unassigned_devices: None | TopologyTUnassignedDevices = field(
        default=None,
        metadata={
            "name": "UnassignedDevices",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataTManufacturer:
    class Meta:
        global_type = False

    catalog: None | ManufacturerDataTManufacturerCatalog = field(
        default=None,
        metadata={
            "name": "Catalog",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    application_programs: None | ManufacturerDataTManufacturerApplicationPrograms = field(
        default=None,
        metadata={
            "name": "ApplicationPrograms",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    baggages: None | ManufacturerDataTManufacturerBaggages = field(
        default=None,
        metadata={
            "name": "Baggages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    hardware: None | ManufacturerDataTManufacturerHardware = field(
        default=None,
        metadata={
            "name": "Hardware",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    languages: None | ManufacturerDataTManufacturerLanguages = field(
        default=None,
        metadata={
            "name": "Languages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class MasterDataT:
    class Meta:
        name = "MasterData_t"

    datapoint_types: None | MasterDataTDatapointTypes = field(
        default=None,
        metadata={
            "name": "DatapointTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    medium_types: None | MasterDataTMediumTypes = field(
        default=None,
        metadata={
            "name": "MediumTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    mask_versions: None | MasterDataTMaskVersions = field(
        default=None,
        metadata={
            "name": "MaskVersions",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    manufacturers: None | MasterDataTManufacturers = field(
        default=None,
        metadata={
            "name": "Manufacturers",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    languages: None | MasterDataTLanguages = field(
        default=None,
        metadata={
            "name": "Languages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    version: int = field(
        metadata={
            "name": "Version",
            "type": "Attribute",
        }
    )
    signature: bytes = field(
        metadata={
            "name": "Signature",
            "type": "Attribute",
            "format": "base64",
        }
    )


@dataclass(slots=True, kw_only=True)
class ProjectTInstallationsInstallation:
    class Meta:
        global_type = False

    topology: TopologyT = field(
        metadata={
            "name": "Topology",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    buildings: BuildingsT = field(
        metadata={
            "name": "Buildings",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    group_addresses: GroupAddressesT = field(
        metadata={
            "name": "GroupAddresses",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        }
    )
    trades: None | TradesT = field(
        default=None,
        metadata={
            "name": "Trades",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    bus_access: None | BusAccessT = field(
        default=None,
        metadata={
            "name": "BusAccess",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    name: str = field(
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 50,
        }
    )
    installation_id: None | int = field(
        default=None,
        metadata={
            "name": "InstallationId",
            "type": "Attribute",
            "max_inclusive": 15,
        },
    )
    bcukey: int = field(
        default=4294967295,
        metadata={
            "name": "BCUKey",
            "type": "Attribute",
        },
    )
    iprouting_multicast_address: str = field(
        default="224.0.23.12",
        metadata={
            "name": "IPRoutingMulticastAddress",
            "type": "Attribute",
            "pattern": r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])",
        },
    )
    default_line: None | str = field(
        default=None,
        metadata={
            "name": "DefaultLine",
            "type": "Attribute",
        },
    )
    completion_status: CompletionStatusT = field(
        default=CompletionStatusT.UNDEFINED,
        metadata={
            "name": "CompletionStatus",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataT:
    class Meta:
        name = "ManufacturerData_t"

    manufacturer: list[ManufacturerDataTManufacturer] = field(
        default_factory=list,
        metadata={
            "name": "Manufacturer",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ProjectTInstallations:
    class Meta:
        global_type = False

    installation: list[ProjectTInstallationsInstallation] = field(
        default_factory=list,
        metadata={
            "name": "Installation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
            "min_occurs": 1,
            "max_occurs": 15,
        },
    )


@dataclass(slots=True, kw_only=True)
class ProjectT:
    class Meta:
        name = "Project_t"

    project_information: None | ProjectTProjectInformation = field(
        default=None,
        metadata={
            "name": "ProjectInformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    installations: None | ProjectTInstallations = field(
        default=None,
        metadata={
            "name": "Installations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    user_files: None | ProjectTUserFiles = field(
        default=None,
        metadata={
            "name": "UserFiles",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    add_in_data: None | ProjectTAddInData = field(
        default=None,
        metadata={
            "name": "AddInData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/10",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class Knx:
    class Meta:
        name = "KNX"
        namespace = "http://knx.org/xml/project/10"

    master_data: None | MasterDataT = field(
        default=None,
        metadata={
            "name": "MasterData",
            "type": "Element",
        },
    )
    manufacturer_data: None | ManufacturerDataT = field(
        default=None,
        metadata={
            "name": "ManufacturerData",
            "type": "Element",
        },
    )
    project: list[ProjectT] = field(
        default_factory=list,
        metadata={
            "name": "Project",
            "type": "Element",
        },
    )
    created_by: None | str = field(
        default=None,
        metadata={
            "name": "CreatedBy",
            "type": "Attribute",
        },
    )
    tool_version: None | str = field(
        default=None,
        metadata={
            "name": "ToolVersion",
            "type": "Attribute",
        },
    )
