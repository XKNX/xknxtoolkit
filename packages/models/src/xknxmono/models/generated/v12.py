from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "http://knx.org/xml/project/12"


class AccessT(Enum):
    NONE = "None"
    READ = "Read"
    READ_WRITE = "ReadWrite"


@dataclass(slots=True, kw_only=True)
class AddinDataT:
    class Meta:
        name = "AddinData_t"

    addin_id: str = field(
        metadata={
            "name": "AddinId",
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


class ApplicationProgramTypeT(Enum):
    APPLICATION_PROGRAM = "ApplicationProgram"
    PEI_PROGRAM = "PeiProgram"


@dataclass(slots=True, kw_only=True)
class AssignT:
    """
    :ivar target_param_ref_ref: registration-relevant
    :ivar source_param_ref_ref: registration-relevant
    :ivar value: registration-relevant
    :ivar internal_description:
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


class AttributeName(Enum):
    CATALOG_NAME = "CatalogName"
    SERIES = "Series"
    COLOUR = "Colour"


@dataclass(slots=True, kw_only=True)
class BinaryDataRefT:
    """
    :ivar data: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "BinaryDataRef_t"

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "format": "base64",
        },
    )
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
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
            "namespace": "http://knx.org/xml/project/12",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
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
class CatalogSectionT:
    class Meta:
        name = "CatalogSection_t"

    catalog_section: list[CatalogSectionT] = field(
        default_factory=list,
        metadata={
            "name": "CatalogSection",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    catalog_item: list[CatalogSectionT.CatalogItem] = field(
        default_factory=list,
        metadata={
            "name": "CatalogItem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class CatalogItem:
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
        non_reg_relevant_data_version: int = field(
            default=0,
            metadata={
                "name": "NonRegRelevantDataVersion",
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


class ComObjectPriorityT(Enum):
    LOW = "Low"
    HIGH = "High"
    ALERT = "Alert"


@dataclass(slots=True, kw_only=True)
class ComObjectRefRefT:
    """
    :ivar ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "ComObjectRefRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
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


class ComTableExpectationT(Enum):
    YES = "Yes"
    NO = "No"
    TRY = "Try"


class CompletionStatusT(Enum):
    UNDEFINED = "Undefined"
    EDITING = "Editing"
    FINISHED_DESIGN = "FinishedDesign"
    FINISHED_COMMISSIONING = "FinishedCommissioning"
    TESTED = "Tested"
    ACCEPTED = "Accepted"
    LOCKED = "Locked"


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


class DownloadBehaviorT(Enum):
    NONE = "None"
    BACKGROUND = "Background"
    DEFAULT_VALUE = "DefaultValue"


class EnableT(Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class FeatureName(Enum):
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
    INTERFACE_OBJECT_DISCOVERY_BY_IO_LIST = "InterfaceObjectDiscoveryByIoList"
    INTERFACE_OBJECT_DISCOVERY_BY_NETWORK_PARAMETER_READ = "InterfaceObjectDiscoveryByNetworkParameterRead"


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
            "namespace": "http://knx.org/xml/project/12",
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


@dataclass(slots=True, kw_only=True)
class GroupAddressRefT:
    class Meta:
        name = "GroupAddressRef_t"

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
    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    role: None | str = field(
        default=None,
        metadata={
            "name": "Role",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    puid: int = field(
        metadata={
            "name": "Puid",
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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )


class HorizontalAlignmentT(Enum):
    LEFT = "Left"
    MIDDLE = "Middle"
    RIGHT = "Right"


class IpconfigAssignT(Enum):
    FIXED = "Fixed"
    AUTO = "Auto"


class InstallationSplitType(Enum):
    NONE = "None"
    MASTER = "Master"
    SPLIT = "Split"


@dataclass(slots=True, kw_only=True)
class LanguageDataT:
    class Meta:
        name = "LanguageData_t"

    translation_unit: list[LanguageDataT.TranslationUnit] = field(
        default_factory=list,
        metadata={
            "name": "TranslationUnit",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    class TranslationUnit:
        translation_element: list[LanguageDataT.TranslationUnit.TranslationElement] = field(
            default_factory=list,
            metadata={
                "name": "TranslationElement",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
        class TranslationElement:
            translation: list[LanguageDataT.TranslationUnit.TranslationElement.Translation] = field(
                default_factory=list,
                metadata={
                    "name": "Translation",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            class Translation:
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


class ManufacturerImportRestriction(Enum):
    OWN = "Own"
    ANY = "Any"
    GROUP = "Group"


class MaskVersionTManagementModel(Enum):
    NONE = "None"
    BCU1 = "Bcu1"
    BIM_M112 = "BimM112"
    BCU2 = "Bcu2"
    PROPERTY_BASED = "PropertyBased"
    SYSTEM_B = "SystemB"


class MemoryTypeT(Enum):
    RAM = "RAM"
    EEPROM = "EEPROM"
    FLASH = "FLASH"


class OptionsParameterByteOrder(Enum):
    BIG_ENDIAN = "BigEndian"
    LITTLE_ENDIAN = "LittleEndian"


class OptionsTextParameterEncodingSelector(Enum):
    USE_WINDOWS_ANSI_CODE_PAGE = "UseWindowsAnsiCodePage"
    USE_PROJECT_CODE_PAGE = "UseProjectCodePage"
    USE_TEXT_PARAMETER_ENCODING_CODE_PAGE = "UseTextParameterEncodingCodePage"


class ParameterCalculationTLanguage(Enum):
    VBSCRIPT = "VBScript"
    JAVA_SCRIPT = "JavaScript"


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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ParameterRefRefT:
    """
    :ivar ref_id: registration-relevant
    :ivar indent_level:
    :ivar internal_description:
    """

    class Meta:
        name = "ParameterRefRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    indent_level: int = field(
        default=0,
        metadata={
            "name": "IndentLevel",
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


class ProcedureTypeT(Enum):
    LOAD = "Load"
    UNLOAD = "Unload"


class ProcedureValue(Enum):
    AP1 = "ap1"
    CFG = "cfg"


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


class RfdeviceModeT(Enum):
    MULTI = "Multi"
    READY = "Ready"


class RegistrationInfoTRegistrationKey(Enum):
    KNXCONV = "knxconv"
    KNXCERT = "knxcert"


class RegistrationStatusT(Enum):
    UNREGISTERED = "Unregistered"
    REGISTERED = "Registered"
    CERTIFIED = "Certified"
    FUTURE_USE_NOT_RECOMMENDED = "FutureUseNotRecommended"
    FUTURE_USE_NOT_ALLOWED = "FutureUseNotAllowed"


@dataclass(slots=True, kw_only=True)
class RenameT:
    """
    :ivar id: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar internal_description:
    """

    class Meta:
        name = "Rename_t"

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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


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
    RELATIVE_MEMORY_BY_OBJECT_TYPE = "RelativeMemoryByObjectType"


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
    MAX_APDU_LENGTH = "MaxApduLength"
    GROUP_FILTER_TABLE_LOAD_CONTROL = "GroupFilterTableLoadControl"
    GROUP_FILTER_TABLE_LOAD_STATUS = "GroupFilterTableLoadStatus"
    MAIN_LC_CONFIG = "MainLcConfig"
    SUB_LC_CONFIG = "SubLcConfig"
    MAIN_LC_GRP_CONFIG = "MainLcGrpConfig"
    SUB_LC_GRP_CONFIG = "SubLcGrpConfig"
    COUPL_SERV_CONTROL = "CouplServControl"
    MAX_ROUTING_APDU_LENGTH = "MaxRoutingApduLength"
    RF_DEVICE_MODE = "RfDeviceMode"
    GROUP_FILTER_TABLE_USE = "GroupFilterTableUse"


class ResourceTypeFlavour(Enum):
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
    LC_12 = "Lc_12"
    PL_MC = "PlMc"
    RE_CONFIG_RF = "ReConfig_Rf"


@dataclass(slots=True, kw_only=True)
class SplitInfoT:
    class Meta:
        name = "SplitInfo_t"

    object_path: str = field(
        metadata={
            "name": "ObjectPath",
            "type": "Attribute",
        }
    )
    cookie: str = field(
        metadata={
            "name": "Cookie",
            "type": "Attribute",
            "pattern": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        }
    )


class TextEncodingT(Enum):
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


class ToDoStatusT(Enum):
    OPEN = "Open"
    ACCOMPLISHED = "Accomplished"


class TypeColorSpace(Enum):
    RGB = "RGB"
    HSV = "HSV"


class TypeDateEncoding(Enum):
    DPT_11 = "DPT 11"


class TypeFloatEncoding(Enum):
    DPT_9 = "DPT 9"
    IEEE_754_SINGLE = "IEEE-754 Single"
    IEEE_754_DOUBLE = "IEEE-754 Double"


class TypeFloatUihint(Enum):
    SLIDER = "Slider"


class TypeIpaddressAddressType(Enum):
    HOST_ADDRESS = "HostAddress"
    GATEWAY_ADDRESS = "GatewayAddress"
    UNICAST_ADDRESS = "UnicastAddress"
    BROADCAST_ADDRESS = "BroadcastAddress"
    MULTICAST_ADDRESS = "MulticastAddress"
    SUBNET_MASK = "SubnetMask"


class TypeIpaddressVersion(Enum):
    IPV4 = "IPv4"
    IPV6 = "IPv6"


class TypeNumberType(Enum):
    SIGNED_INT = "signedInt"
    UNSIGNED_INT = "unsignedInt"


class TypeNumberUihint(Enum):
    SLIDER = "Slider"
    CHECK_BOX = "CheckBox"


class TypeRestrictionBase(Enum):
    VALUE = "Value"
    BINARY_VALUE = "BinaryValue"


class TypeTimeUihint(Enum):
    TIME_SS = "Time_ss"
    TIME_SSF = "Time_ssf"
    TIME_SSFF = "Time_ssff"
    TIME_SSFFF = "Time_ssfff"
    TIME_MMSS = "Time_mmss"
    TIME_MMSSF = "Time_mmssf"
    TIME_MMSSFF = "Time_mmssff"
    TIME_MMSSFFF = "Time_mmssfff"
    TIME_HHMM = "Time_hhmm"
    TIME_HHMMSS = "Time_hhmmss"
    TIME_HHMMSSF = "Time_hhmmssf"
    TIME_HHMMSSFF = "Time_hhmmssff"
    TIME_HHMMSSFFF = "Time_hhmmssfff"
    TIME_DHH = "Time_dhh"
    TIME_DHHMM = "Time_dhhmm"
    TIME_DHHMMSS = "Time_dhhmmss"
    DURATION_MMSS = "Duration_mmss"
    DURATION_MMSSF = "Duration_mmssf"
    DURATION_MMSSFF = "Duration_mmssff"
    DURATION_MMSSFFF = "Duration_mmssfff"
    DURATION_HHMM = "Duration_hhmm"
    DURATION_HHMMSS = "Duration_hhmmss"
    DURATION_HHMMSSF = "Duration_hhmmssf"
    DURATION_HHMMSSFF = "Duration_hhmmssff"
    DURATION_HHMMSSFFF = "Duration_hhmmssfff"


class TypeTimeUnit(Enum):
    HOURS = "Hours"
    MINUTES = "Minutes"
    SECONDS = "Seconds"
    HUNDRED_MILLISECONDS = "HundredMilliseconds"
    TEN_MILLISECONDS = "TenMilliseconds"
    MILLISECONDS = "Milliseconds"
    PACKED_SECONDS_AND_MILLISECONDS = "PackedSecondsAndMilliseconds"
    PACKED_DAYS_HOURS_MINUTES_AND_SECONDS = "PackedDaysHoursMinutesAndSeconds"
    PACKED_MINUTES_SECONDS_AND_MILLISECONDS = "PackedMinutesSecondsAndMilliseconds"


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
    :ivar internal_description:
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefT:
    class Meta:
        name = "ComObjectInstanceRef_t"

    connectors: None | ComObjectInstanceRefT.Connectors = field(
        default=None,
        metadata={
            "name": "Connectors",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class Connectors:
        send: ComObjectInstanceRefT.Connectors.Send = field(
            metadata={
                "name": "Send",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            }
        )
        receive: list[ComObjectInstanceRefT.Connectors.Receive] = field(
            default_factory=list,
            metadata={
                "name": "Receive",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Send:
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
        class Receive:
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
class ComObjectRefT:
    """
    :ivar id: registration-relevant
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar tag:
    :ivar function_text:
    :ivar priority:
    :ivar object_size: registration-relevant
    :ivar read_flag:
    :ivar write_flag:
    :ivar communication_flag:
    :ivar transmit_flag:
    :ivar update_flag:
    :ivar read_on_init_flag:
    :ivar datapoint_type:
    :ivar text_parameter_ref_id:
    :ivar internal_description:
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
    text_parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "TextParameterRefId",
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
class ComObjectT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar number: registration-relevant
    :ivar function_text:
    :ivar priority:
    :ivar object_size: registration-relevant
    :ivar read_flag:
    :ivar write_flag:
    :ivar communication_flag:
    :ivar transmit_flag:
    :ivar update_flag:
    :ivar read_on_init_flag:
    :ivar datapoint_type:
    :ivar internal_description:
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class FunctionT:
    class Meta:
        name = "Function_t"

    group_address_ref: list[GroupAddressRefT] = field(
        default_factory=list,
        metadata={
            "name": "GroupAddressRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    type_value: None | str = field(
        default=None,
        metadata={
            "name": "Type",
            "type": "Attribute",
            "max_length": 255,
        },
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
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
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
    default_group_range: None | str = field(
        default=None,
        metadata={
            "name": "DefaultGroupRange",
            "type": "Attribute",
        },
    )
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
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
            "namespace": "http://knx.org/xml/project/12",
            "max_occurs": 65535,
        },
    )
    group_address: list[GroupAddressT] = field(
        default_factory=list,
        metadata={
            "name": "GroupAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
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
class LoadProcedureT:
    class Meta:
        name = "LoadProcedure_t"

    ld_ctrl_unload: list[LoadProcedureT.LdCtrlUnload] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlUnload",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_load: list[LoadProcedureT.LdCtrlLoad] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoad",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_max_length: list[LoadProcedureT.LdCtrlMaxLength] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMaxLength",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_clear_cached_object_types: list[LoadProcedureT.LdCtrlClearCachedObjectTypes] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlClearCachedObjectTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_load_completed: list[LoadProcedureT.LdCtrlLoadCompleted] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadCompleted",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_abs_segment: list[LoadProcedureT.LdCtrlAbsSegment] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlAbsSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_rel_segment: list[LoadProcedureT.LdCtrlRelSegment] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlRelSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_task_segment: list[LoadProcedureT.LdCtrlTaskSegment] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_task_ptr: list[LoadProcedureT.LdCtrlTaskPtr] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskPtr",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_task_ctrl1: list[LoadProcedureT.LdCtrlTaskCtrl1] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskCtrl1",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_task_ctrl2: list[LoadProcedureT.LdCtrlTaskCtrl2] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskCtrl2",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_write_prop: list[LoadProcedureT.LdCtrlWriteProp] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_compare_prop: list[LoadProcedureT.LdCtrlCompareProp] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_load_image_prop: list[LoadProcedureT.LdCtrlLoadImageProp] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_invoke_function_prop: list[LoadProcedureT.LdCtrlInvokeFunctionProp] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlInvokeFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_read_function_prop: list[LoadProcedureT.LdCtrlReadFunctionProp] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlReadFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_write_mem: list[LoadProcedureT.LdCtrlWriteMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_compare_mem: list[LoadProcedureT.LdCtrlCompareMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_load_image_mem: list[LoadProcedureT.LdCtrlLoadImageMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_write_rel_mem: list[LoadProcedureT.LdCtrlWriteRelMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_compare_rel_mem: list[LoadProcedureT.LdCtrlCompareRelMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_load_image_rel_mem: list[LoadProcedureT.LdCtrlLoadImageRelMem] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_connect: list[LoadProcedureT.LdCtrlConnect] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlConnect",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_disconnect: list[LoadProcedureT.LdCtrlDisconnect] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDisconnect",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_restart: list[LoadProcedureT.LdCtrlRestart] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlRestart",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_master_reset: list[LoadProcedureT.LdCtrlMasterReset] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMasterReset",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_delay: list[LoadProcedureT.LdCtrlDelay] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDelay",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_set_control_variable: list[LoadProcedureT.LdCtrlSetControlVariable] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlSetControlVariable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_map_error: list[LoadProcedureT.LdCtrlMapError] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMapError",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_progress_text: list[LoadProcedureT.LdCtrlProgressText] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlProgressText",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_declare_prop_desc: list[LoadProcedureT.LdCtrlDeclarePropDesc] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDeclarePropDesc",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_clear_lcfilter_table: list[LoadProcedureT.LdCtrlClearLcfilterTable] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlClearLCFilterTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ld_ctrl_merge: list[LoadProcedureT.LdCtrlMerge] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMerge",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlUnload:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlLoad:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlMaxLength:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar size: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlClearCachedObjectTypes:
        """
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

        applies_to: LdCtrlProcTypeT = field(
            default=LdCtrlProcTypeT.AUTO,
            metadata={
                "name": "AppliesTo",
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
    class LdCtrlLoadCompleted:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlAbsSegment:
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
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlRelSegment:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar size: registration-relevant
        :ivar mode: registration-relevant
        :ivar fill: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlTaskSegment:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar address: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlTaskPtr:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar init_ptr: registration-relevant
        :ivar save_ptr: registration-relevant
        :ivar serial_ptr: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlTaskCtrl1:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar address: registration-relevant
        :ivar count: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlTaskCtrl2:
        """
        :ivar lsm_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar callback: registration-relevant
        :ivar address: registration-relevant
        :ivar seg0: registration-relevant
        :ivar seg1: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlWriteProp:
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
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlCompareProp:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar prop_id: registration-relevant
        :ivar start_element: registration-relevant
        :ivar count: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlLoadImageProp:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar prop_id: registration-relevant
        :ivar count: registration-relevant
        :ivar start_element: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlInvokeFunctionProp:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar prop_id: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlReadFunctionProp:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar prop_id: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlWriteMem:
        """
        :ivar address_space: registration-relevant
        :ivar address: registration-relevant
        :ivar size: registration-relevant
        :ivar verify: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlCompareMem:
        """
        :ivar address_space: registration-relevant
        :ivar address: registration-relevant
        :ivar size: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlLoadImageMem:
        """
        :ivar address_space: registration-relevant
        :ivar address: registration-relevant
        :ivar size: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlWriteRelMem:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar offset: registration-relevant
        :ivar size: registration-relevant
        :ivar verify: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlCompareRelMem:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar offset: registration-relevant
        :ivar size: registration-relevant
        :ivar inline_data: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlLoadImageRelMem:
        """
        :ivar obj_idx: registration-relevant
        :ivar obj_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar offset: registration-relevant
        :ivar size: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlConnect:
        """
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

        applies_to: LdCtrlProcTypeT = field(
            default=LdCtrlProcTypeT.AUTO,
            metadata={
                "name": "AppliesTo",
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
    class LdCtrlDisconnect:
        """
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

        applies_to: LdCtrlProcTypeT = field(
            default=LdCtrlProcTypeT.AUTO,
            metadata={
                "name": "AppliesTo",
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
    class LdCtrlRestart:
        """
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

        applies_to: LdCtrlProcTypeT = field(
            default=LdCtrlProcTypeT.AUTO,
            metadata={
                "name": "AppliesTo",
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
    class LdCtrlMasterReset:
        """
        :ivar erase_code: registration-relevant
        :ivar channel_number: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

        erase_code: int = field(
            metadata={
                "name": "EraseCode",
                "type": "Attribute",
            }
        )
        channel_number: int = field(
            metadata={
                "name": "ChannelNumber",
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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlDelay:
        """
        :ivar milli_seconds: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlSetControlVariable:
        """
        :ivar name: registration-relevant
        :ivar value: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlMapError:
        """
        :ivar ld_ctrl_filter: registration-relevant
        :ivar original_error: registration-relevant
        :ivar mapped_error: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlProgressText:
        """
        :ivar text_id: registration-relevant
        :ivar applies_to: registration-relevant
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlDeclarePropDesc:
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
        :ivar internal_description:
        """

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
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class LdCtrlClearLcfilterTable:
        """
        :ivar applies_to: registration-relevant
        :ivar use_function_prop: registration-relevant
        :ivar internal_description:
        """

        applies_to: LdCtrlProcTypeT = field(
            default=LdCtrlProcTypeT.AUTO,
            metadata={
                "name": "AppliesTo",
                "type": "Attribute",
            },
        )
        use_function_prop: bool = field(
            default=False,
            metadata={
                "name": "UseFunctionProp",
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
    class LdCtrlMerge:
        """
        :ivar merge_id: registration-relevant
        :ivar internal_description:
        """

        merge_id: int = field(
            metadata={
                "name": "MergeId",
                "type": "Attribute",
            }
        )
        internal_description: None | str = field(
            default=None,
            metadata={
                "name": "InternalDescription",
                "type": "Attribute",
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
    :ivar internal_description:
    """

    class Meta:
        name = "ParameterCalculation_t"

    rltransformation: str = field(
        metadata={
            "name": "RLTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        }
    )
    lrtransformation: str = field(
        metadata={
            "name": "LRTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        }
    )
    lparameters: ParameterCalculationT.Lparameters = field(
        metadata={
            "name": "LParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        }
    )
    rparameters: ParameterCalculationT.Rparameters = field(
        metadata={
            "name": "RParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Lparameters:
        """
        :ivar parameter_ref_ref: registration-relevant set
        """

        parameter_ref_ref: list[ParameterCalculationT.Lparameters.ParameterRefRef] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class ParameterRefRef(ParameterRefRefT):
            """
            :ivar alias_name: registration-relevant
            """

            alias_name: None | str = field(
                default=None,
                metadata={
                    "name": "AliasName",
                    "type": "Attribute",
                    "max_length": 50,
                },
            )

    @dataclass(slots=True, kw_only=True)
    class Rparameters:
        """
        :ivar parameter_ref_ref: registration-relevant set
        """

        parameter_ref_ref: list[ParameterCalculationT.Rparameters.ParameterRefRef] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class ParameterRefRef(ParameterRefRefT):
            """
            :ivar alias_name: registration-relevant
            """

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
    :ivar suffix_text:
    :ivar tag:
    :ivar display_order:
    :ivar access:
    :ivar value: registration-relevant
    :ivar text_parameter_ref_id:
    :ivar internal_description:
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
    suffix_text: None | str = field(
        default=None,
        metadata={
            "name": "SuffixText",
            "type": "Attribute",
            "max_length": 20,
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
    text_parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "TextParameterRefId",
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
class ParameterSeparatorT:
    """
    :ivar id: registration-relevant
    :ivar text:
    :ivar access:
    :ivar horizontal_ruler:
    :ivar text_parameter_ref_id:
    :ivar internal_description:
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
    horizontal_ruler: bool = field(
        default=False,
        metadata={
            "name": "HorizontalRuler",
            "type": "Attribute",
        },
    )
    text_parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "TextParameterRefId",
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
class ParameterTypeT:
    """
    :ivar type_number:
    :ivar type_float:
    :ivar type_restriction:
    :ivar type_text:
    :ivar type_time:
    :ivar type_date:
    :ivar type_ipaddress:
    :ivar type_picture:
    :ivar type_color:
    :ivar type_none:
    :ivar id: registration-relevant
    :ivar name: registration-relevant
    :ivar internal_description:
    :ivar plugin:
    """

    class Meta:
        name = "ParameterType_t"

    type_number: None | ParameterTypeT.TypeNumber = field(
        default=None,
        metadata={
            "name": "TypeNumber",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_float: None | ParameterTypeT.TypeFloat = field(
        default=None,
        metadata={
            "name": "TypeFloat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_restriction: None | ParameterTypeT.TypeRestriction = field(
        default=None,
        metadata={
            "name": "TypeRestriction",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_text: None | ParameterTypeT.TypeText = field(
        default=None,
        metadata={
            "name": "TypeText",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_time: None | ParameterTypeT.TypeTime = field(
        default=None,
        metadata={
            "name": "TypeTime",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_date: None | ParameterTypeT.TypeDate = field(
        default=None,
        metadata={
            "name": "TypeDate",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_ipaddress: None | ParameterTypeT.TypeIpaddress = field(
        default=None,
        metadata={
            "name": "TypeIPAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_picture: None | ParameterTypeT.TypePicture = field(
        default=None,
        metadata={
            "name": "TypePicture",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_color: None | ParameterTypeT.TypeColor = field(
        default=None,
        metadata={
            "name": "TypeColor",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    type_none: None | object = field(
        default=None,
        metadata={
            "name": "TypeNone",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    class TypeNumber:
        """
        :ivar size_in_bit: registration-relevant
        :ivar type_value: registration-relevant
        :ivar min_inclusive: registration-relevant
        :ivar max_inclusive: registration-relevant
        :ivar uihint:
        """

        size_in_bit: int = field(
            metadata={
                "name": "SizeInBit",
                "type": "Attribute",
                "min_inclusive": 1,
                "max_inclusive": 32,
            }
        )
        type_value: TypeNumberType = field(
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
        uihint: None | TypeNumberUihint = field(
            default=None,
            metadata={
                "name": "UIHint",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeFloat:
        """
        :ivar encoding: registration-relevant
        :ivar min_inclusive: registration-relevant
        :ivar max_inclusive: registration-relevant
        :ivar uihint:
        :ivar display_format:
        """

        encoding: TypeFloatEncoding = field(
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
        uihint: None | TypeFloatUihint = field(
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
                "pattern": r"[#,]*[0,]+(\.0*)?([eE][+-]?0+)?",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeRestriction:
        """
        :ivar enumeration: registration-relevant set
        :ivar base: registration-relevant
        :ivar size_in_bit: registration-relevant
        """

        enumeration: list[ParameterTypeT.TypeRestriction.Enumeration] = field(
            default_factory=list,
            metadata={
                "name": "Enumeration",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        base: TypeRestrictionBase = field(
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
        class Enumeration:
            """
            :ivar text:
            :ivar value: registration-relevant
            :ivar id: registration-relevant
            :ivar display_order:
            :ivar binary_value: registration-relevant
            """

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
    class TypeText:
        """
        :ivar size_in_bit: registration-relevant
        :ivar pattern:
        """

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

    @dataclass(slots=True, kw_only=True)
    class TypeTime:
        """
        :ivar size_in_bit: registration-relevant
        :ivar unit: registration-relevant
        :ivar min_inclusive: registration-relevant
        :ivar max_inclusive: registration-relevant
        :ivar uihint:
        """

        size_in_bit: int = field(
            metadata={
                "name": "SizeInBit",
                "type": "Attribute",
                "min_inclusive": 8,
                "max_inclusive": 64,
            }
        )
        unit: TypeTimeUnit = field(
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
        uihint: None | TypeTimeUihint = field(
            default=None,
            metadata={
                "name": "UIHint",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeDate:
        """
        :ivar encoding: registration-relevant
        :ivar display_the_year: registration-relevant
        """

        encoding: TypeDateEncoding = field(
            metadata={
                "name": "Encoding",
                "type": "Attribute",
            }
        )
        display_the_year: bool = field(
            default=True,
            metadata={
                "name": "DisplayTheYear",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeIpaddress:
        """
        :ivar address_type: registration-relevant
        :ivar version: registration-relevant
        """

        address_type: TypeIpaddressAddressType = field(
            metadata={
                "name": "AddressType",
                "type": "Attribute",
            }
        )
        version: TypeIpaddressVersion = field(
            default=TypeIpaddressVersion.IPV4,
            metadata={
                "name": "Version",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypePicture:
        ref_id: str = field(
            metadata={
                "name": "RefId",
                "type": "Attribute",
            }
        )
        horizontal_alignment: None | HorizontalAlignmentT = field(
            default=None,
            metadata={
                "name": "HorizontalAlignment",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeColor:
        """
        :ivar space: registration-relevant
        """

        space: TypeColorSpace = field(
            metadata={
                "name": "Space",
                "type": "Attribute",
            }
        )


@dataclass(slots=True, kw_only=True)
class ParameterT:
    """
    :ivar memory:
    :ivar property:
    :ivar legacy_patch_always: registration-relevant
    :ivar id: registration-relevant
    :ivar name:
    :ivar parameter_type: registration-relevant
    :ivar text:
    :ivar suffix_text:
    :ivar access:
    :ivar value: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "Parameter_t"

    memory: None | ParameterT.Memory = field(
        default=None,
        metadata={
            "name": "Memory",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    property: None | ParameterT.Property = field(
        default=None,
        metadata={
            "name": "Property",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    suffix_text: None | str = field(
        default=None,
        metadata={
            "name": "SuffixText",
            "type": "Attribute",
            "max_length": 20,
        },
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Memory:
        """
        :ivar code_segment: registration-relevant
        :ivar offset: registration-relevant
        :ivar bit_offset: registration-relevant
        """

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
    class Property:
        """
        :ivar object_index: registration-relevant
        :ivar object_type: registration-relevant
        :ivar occurrence: registration-relevant
        :ivar property_id: registration-relevant
        :ivar offset: registration-relevant
        :ivar bit_offset: registration-relevant
        """

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
class SplitInfosT:
    class Meta:
        name = "SplitInfos_t"

    split_info: list[SplitInfoT] = field(
        default_factory=list,
        metadata={
            "name": "SplitInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
class TradeT:
    class Meta:
        name = "Trade_t"

    trade: list[TradeT] = field(
        default_factory=list,
        metadata={
            "name": "Trade",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
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
    :ivar suffix_text:
    :ivar access:
    :ivar value: registration-relevant
    :ivar default_union_parameter: registration-relevant
    :ivar internal_description:
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
    suffix_text: None | str = field(
        default=None,
        metadata={
            "name": "SuffixText",
            "type": "Attribute",
            "max_length": 20,
        },
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
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
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    function: list[FunctionT] = field(
        default_factory=list,
        metadata={
            "name": "Function",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
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
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "ComObjectParameterChoose_t"

    when: list[ComObjectParameterChooseT.When] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class When(WhenT):
        parameter_block: list[ComObjectParameterBlockT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterBlock",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        parameter_separator: list[ParameterSeparatorT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterSeparator",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        parameter_ref_ref: list[ParameterRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        choose: list[ComObjectParameterChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        binary_data_ref: list[BinaryDataRefT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryDataRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        com_object_ref_ref: list[ComObjectRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        assign: list[AssignT] = field(
            default_factory=list,
            metadata={
                "name": "Assign",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )


@dataclass(slots=True, kw_only=True)
class DeviceInstanceT:
    class Meta:
        name = "DeviceInstance_t"

    parameter_instance_refs: None | DeviceInstanceT.ParameterInstanceRefs = field(
        default=None,
        metadata={
            "name": "ParameterInstanceRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    com_object_instance_refs: None | DeviceInstanceT.ComObjectInstanceRefs = field(
        default=None,
        metadata={
            "name": "ComObjectInstanceRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    additional_addresses: None | DeviceInstanceT.AdditionalAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalAddresses",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    binary_data: None | DeviceInstanceT.BinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    ipconfig: None | IpconfigT = field(
        default=None,
        metadata={
            "name": "IPConfig",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    name: None | str = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
            "max_length": 255,
        },
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
    last_used_apdulength: None | int = field(
        default=None,
        metadata={
            "name": "LastUsedAPDULength",
            "type": "Attribute",
        },
    )
    read_max_apdulength: None | int = field(
        default=None,
        metadata={
            "name": "ReadMaxAPDULength",
            "type": "Attribute",
        },
    )
    read_max_routing_apdulength: None | int = field(
        default=None,
        metadata={
            "name": "ReadMaxRoutingAPDULength",
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
    broken: bool = field(
        default=False,
        metadata={
            "name": "Broken",
            "type": "Attribute",
        },
    )
    serial_number: None | bytes = field(
        default=None,
        metadata={
            "name": "SerialNumber",
            "type": "Attribute",
            "format": "base64",
        },
    )
    unique_id: None | str = field(
        default=None,
        metadata={
            "name": "UniqueId",
            "type": "Attribute",
            "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        },
    )
    is_rfretransmitter: bool = field(
        default=False,
        metadata={
            "name": "IsRFRetransmitter",
            "type": "Attribute",
        },
    )
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class ParameterInstanceRefs:
        parameter_instance_ref: list[ParameterInstanceRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterInstanceRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ComObjectInstanceRefs:
        com_object_instance_ref: list[ComObjectInstanceRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectInstanceRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class AdditionalAddresses:
        address: list[DeviceInstanceT.AdditionalAddresses.Address] = field(
            default_factory=list,
            metadata={
                "name": "Address",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
                "max_occurs": 254,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Address:
            address: int = field(
                metadata={
                    "name": "Address",
                    "type": "Attribute",
                    "min_inclusive": 1,
                    "max_inclusive": 255,
                }
            )

    @dataclass(slots=True, kw_only=True)
    class BinaryData:
        binary_data: list[DeviceInstanceT.BinaryData.BinaryDataInner] = field(
            default_factory=list,
            metadata={
                "name": "BinaryData",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class BinaryDataInner:
            data: None | bytes = field(
                default=None,
                metadata={
                    "name": "Data",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            puid: int = field(
                metadata={
                    "name": "Puid",
                    "type": "Attribute",
                }
            )


@dataclass(slots=True, kw_only=True)
class GroupAddressesT:
    class Meta:
        name = "GroupAddresses_t"

    group_ranges: GroupAddressesT.GroupRanges = field(
        metadata={
            "name": "GroupRanges",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class GroupRanges:
        group_range: list[GroupRangeT] = field(
            default_factory=list,
            metadata={
                "name": "GroupRange",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
    :ivar check_sums: registration-relevant
    :ivar loaded_image: registration-relevant
    """

    class Meta:
        name = "Hardware2Program_t"

    application_program_ref: list[ApplicationProgramRefT] = field(
        default_factory=list,
        metadata={
            "name": "ApplicationProgramRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "max_occurs": 2,
        },
    )
    registration_info: None | RegistrationInfoT = field(
        default=None,
        metadata={
            "name": "RegistrationInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    check_sums: None | bytes = field(
        default=None,
        metadata={
            "name": "CheckSums",
            "type": "Attribute",
            "format": "base64",
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


@dataclass(slots=True, kw_only=True)
class HawkConfigurationDataT:
    class Meta:
        name = "HawkConfigurationData_t"

    features: None | HawkConfigurationDataT.Features = field(
        default=None,
        metadata={
            "name": "Features",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    resources: None | HawkConfigurationDataT.Resources = field(
        default=None,
        metadata={
            "name": "Resources",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    procedures: None | HawkConfigurationDataT.Procedures = field(
        default=None,
        metadata={
            "name": "Procedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    memory_segments: None | HawkConfigurationDataT.MemorySegments = field(
        default=None,
        metadata={
            "name": "MemorySegments",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    interface_objects: None | HawkConfigurationDataT.InterfaceObjects = field(
        default=None,
        metadata={
            "name": "InterfaceObjects",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    class Features:
        feature: list[HawkConfigurationDataT.Features.Feature] = field(
            default_factory=list,
            metadata={
                "name": "Feature",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Feature:
            name: FeatureName = field(
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
    class Resources:
        resource: list[HawkConfigurationDataT.Resources.Resource] = field(
            default_factory=list,
            metadata={
                "name": "Resource",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Resource:
            location: None | ResourceLocationT = field(
                default=None,
                metadata={
                    "name": "Location",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            img_location: None | ResourceLocationT = field(
                default=None,
                metadata={
                    "name": "ImgLocation",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            resource_type: HawkConfigurationDataT.Resources.Resource.ResourceType = field(
                metadata={
                    "name": "ResourceType",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                }
            )
            access_rights: HawkConfigurationDataT.Resources.Resource.AccessRights = field(
                metadata={
                    "name": "AccessRights",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            class ResourceType:
                length: int = field(
                    metadata={
                        "name": "Length",
                        "type": "Attribute",
                    }
                )
                flavour: None | ResourceTypeFlavour = field(
                    default=None,
                    metadata={
                        "name": "Flavour",
                        "type": "Attribute",
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class AccessRights:
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
    class Procedures:
        procedure: list[HawkConfigurationDataT.Procedures.Procedure] = field(
            default_factory=list,
            metadata={
                "name": "Procedure",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Procedure(LoadProcedureT):
            procedure_type: ProcedureTypeT = field(
                metadata={
                    "name": "ProcedureType",
                    "type": "Attribute",
                }
            )
            procedure_sub_type: LdCtrlProcTypeT | ProcedureValue = field(
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
    class MemorySegments:
        memory_segment: list[HawkConfigurationDataT.MemorySegments.MemorySegment] = field(
            default_factory=list,
            metadata={
                "name": "MemorySegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class MemorySegment:
            location: ResourceLocationT = field(
                metadata={
                    "name": "Location",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                }
            )
            access_rights: HawkConfigurationDataT.MemorySegments.MemorySegment.AccessRights = field(
                metadata={
                    "name": "AccessRights",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            class AccessRights:
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
    class InterfaceObjects:
        interface_object: list[HawkConfigurationDataT.InterfaceObjects.InterfaceObject] = field(
            default_factory=list,
            metadata={
                "name": "InterfaceObject",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class InterfaceObject:
            property: list[HawkConfigurationDataT.InterfaceObjects.InterfaceObject.Property] = field(
                default_factory=list,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            class Property:
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
class LoadProceduresT:
    """
    :ivar load_procedure: registration-relevant set
    """

    class Meta:
        name = "LoadProcedures_t"

    load_procedure: list[LoadProceduresT.LoadProcedure] = field(
        default_factory=list,
        metadata={
            "name": "LoadProcedure",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )

    @dataclass(slots=True, kw_only=True)
    class LoadProcedure(LoadProcedureT):
        """
        :ivar merge_id: registration-relevant
        """

        merge_id: None | int = field(
            default=None,
            metadata={
                "name": "MergeId",
                "type": "Attribute",
            },
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
            "namespace": "http://knx.org/xml/project/12",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticT:
    class Meta:
        name = "ApplicationProgramStatic_t"

    code: None | ApplicationProgramStaticT.Code = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameter_types: None | ApplicationProgramStaticT.ParameterTypes = field(
        default=None,
        metadata={
            "name": "ParameterTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameters: None | ApplicationProgramStaticT.Parameters = field(
        default=None,
        metadata={
            "name": "Parameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameter_refs: None | ApplicationProgramStaticT.ParameterRefs = field(
        default=None,
        metadata={
            "name": "ParameterRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameter_calculations: None | ApplicationProgramStaticT.ParameterCalculations = field(
        default=None,
        metadata={
            "name": "ParameterCalculations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    com_object_table: None | ApplicationProgramStaticT.ComObjectTable = field(
        default=None,
        metadata={
            "name": "ComObjectTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    com_object_refs: None | ApplicationProgramStaticT.ComObjectRefs = field(
        default=None,
        metadata={
            "name": "ComObjectRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    address_table: None | ApplicationProgramStaticT.AddressTable = field(
        default=None,
        metadata={
            "name": "AddressTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    association_table: None | ApplicationProgramStaticT.AssociationTable = field(
        default=None,
        metadata={
            "name": "AssociationTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    fixup_list: None | ApplicationProgramStaticT.FixupList = field(
        default=None,
        metadata={
            "name": "FixupList",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    load_procedures: None | LoadProceduresT = field(
        default=None,
        metadata={
            "name": "LoadProcedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    extension: None | ApplicationProgramStaticT.Extension = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    binary_data: None | ApplicationProgramStaticT.BinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    device_compare: None | ApplicationProgramStaticT.DeviceCompare = field(
        default=None,
        metadata={
            "name": "DeviceCompare",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    options: None | ApplicationProgramStaticT.Options = field(
        default=None,
        metadata={
            "name": "Options",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Code:
        """
        :ivar absolute_segment: registration-relevant set
        :ivar relative_segment: registration-relevant set
        """

        absolute_segment: list[ApplicationProgramStaticT.Code.AbsoluteSegment] = field(
            default_factory=list,
            metadata={
                "name": "AbsoluteSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        relative_segment: list[ApplicationProgramStaticT.Code.RelativeSegment] = field(
            default_factory=list,
            metadata={
                "name": "RelativeSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class AbsoluteSegment:
            """
            :ivar data: registration-relevant
            :ivar mask: registration-relevant
            :ivar id: registration-relevant
            :ivar name:
            :ivar memory_type:
            :ivar address: registration-relevant
            :ivar size: registration-relevant
            :ivar user_memory: registration-relevant
            :ivar internal_description:
            """

            data: None | bytes = field(
                default=None,
                metadata={
                    "name": "Data",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "format": "base64",
                },
            )
            mask: None | bytes = field(
                default=None,
                metadata={
                    "name": "Mask",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )

        @dataclass(slots=True, kw_only=True)
        class RelativeSegment:
            """
            :ivar data: registration-relevant
            :ivar mask: registration-relevant
            :ivar id: registration-relevant
            :ivar name:
            :ivar offset: registration-relevant
            :ivar size: registration-relevant
            :ivar load_state_machine: registration-relevant
            :ivar internal_description:
            """

            data: None | bytes = field(
                default=None,
                metadata={
                    "name": "Data",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "format": "base64",
                },
            )
            mask: None | bytes = field(
                default=None,
                metadata={
                    "name": "Mask",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class ParameterTypes:
        """
        :ivar parameter_type: registration-relevant set
        """

        parameter_type: list[ParameterTypeT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Parameters:
        parameter: list[ParameterT] = field(
            default_factory=list,
            metadata={
                "name": "Parameter",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        union: list[ApplicationProgramStaticT.Parameters.UnionType] = field(
            default_factory=list,
            metadata={
                "name": "Union",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class UnionType:
            """
            :ivar memory:
            :ivar property:
            :ivar parameter: registration-relevant set
            :ivar size_in_bit:
            """

            memory: None | ApplicationProgramStaticT.Parameters.UnionType.Memory = field(
                default=None,
                metadata={
                    "name": "Memory",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            property: None | ApplicationProgramStaticT.Parameters.UnionType.Property = field(
                default=None,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            parameter: list[UnionParameterT] = field(
                default_factory=list,
                metadata={
                    "name": "Parameter",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            class Memory:
                """
                :ivar code_segment: registration-relevant
                :ivar offset: registration-relevant
                :ivar bit_offset: registration-relevant
                """

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
            class Property:
                """
                :ivar object_index: registration-relevant
                :ivar object_type: registration-relevant
                :ivar occurrence: registration-relevant
                :ivar property_id: registration-relevant
                :ivar offset: registration-relevant
                :ivar bit_offset: registration-relevant
                """

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

    @dataclass(slots=True, kw_only=True)
    class ParameterRefs:
        """
        :ivar parameter_ref: registration-relevant list This is a list
            to ensure deterministic behaviour in case of multiple active
            parameter refs
        """

        parameter_ref: list[ParameterRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ParameterCalculations:
        """
        :ivar parameter_calculation: registration-relevant set
        """

        parameter_calculation: list[ParameterCalculationT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterCalculation",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ComObjectTable:
        """
        :ivar com_object: registration-relevant set
        :ivar code_segment: registration-relevant
        :ivar offset: registration-relevant
        """

        com_object: list[ComObjectT] = field(
            default_factory=list,
            metadata={
                "name": "ComObject",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
    class ComObjectRefs:
        """
        :ivar com_object_ref: registration-relevant set This is a list
            to ensure deterministic behaviour in case of multiple active
            communication object refs
        """

        com_object_ref: list[ComObjectRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class AddressTable:
        """
        :ivar code_segment: registration-relevant
        :ivar offset: registration-relevant
        :ivar max_entries: registration-relevant
        """

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
    class AssociationTable:
        """
        :ivar code_segment: registration-relevant
        :ivar offset: registration-relevant
        :ivar max_entries: registration-relevant
        """

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
    class FixupList:
        """
        :ivar fixup: registration-relevant set
        """

        fixup: list[FixupT] = field(
            default_factory=list,
            metadata={
                "name": "Fixup",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Extension:
        baggage: list[ApplicationProgramStaticT.Extension.Baggage] = field(
            default_factory=list,
            metadata={
                "name": "Baggage",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
        class Baggage:
            ref_id: str = field(
                metadata={
                    "name": "RefId",
                    "type": "Attribute",
                }
            )

    @dataclass(slots=True, kw_only=True)
    class BinaryData:
        binary_data: list[BinaryDataT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryData",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class DeviceCompare:
        exclude_memory: list[ApplicationProgramStaticT.DeviceCompare.ExcludeMemory] = field(
            default_factory=list,
            metadata={
                "name": "ExcludeMemory",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        exclude_property: list[ApplicationProgramStaticT.DeviceCompare.ExcludeProperty] = field(
            default_factory=list,
            metadata={
                "name": "ExcludeProperty",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        standard_com_tables_expectable: ComTableExpectationT = field(
            default=ComTableExpectationT.TRY,
            metadata={
                "name": "StandardComTablesExpectable",
                "type": "Attribute",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class ExcludeMemory:
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )

        @dataclass(slots=True, kw_only=True)
        class ExcludeProperty:
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class Options:
        """
        :ivar prefer_partial_download_if_application_loaded:
        :ivar easy_ctrl_mode_mode_style_empty_group_com_tables:
        :ivar set_object_table_length_always_to_one:
        :ivar text_parameter_encoding:
        :ivar text_parameter_encoding_selector:
        :ivar text_parameter_zero_terminate:
        :ivar parameter_byte_order:
        :ivar partial_download_only_visible_parameters:
        :ivar legacy_no_partial_download:
        :ivar legacy_no_memory_verify_mode:
        :ivar legacy_no_optimistic_write:
        :ivar legacy_do_not_report_property_write_errors:
        :ivar legacy_no_background_download:
        :ivar legacy_do_not_check_manufacturer_id:
        :ivar legacy_always_reload_app_if_co_visibility_changed:
        :ivar legacy_never_reload_app_if_co_visibility_changed:
        :ivar legacy_do_not_support_undo_delete:
        :ivar legacy_allow_partial_download_if_ap2_mismatch:
        :ivar legacy_keep_object_table_gaps:
        :ivar legacy_proxy_communication_objects:
        :ivar device_info_ignore_run_state:
        :ivar device_info_ignore_loaded_state:
        :ivar device_compare_allow_compatible_manufacturer_id:
        :ivar line_coupler0912_new_programming_style: registration-
            relevant
        :ivar comparable:
        :ivar reconstructable:
        :ivar download_invisible_parameters:
        """

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
        text_parameter_encoding: None | TextEncodingT = field(
            default=None,
            metadata={
                "name": "TextParameterEncoding",
                "type": "Attribute",
            },
        )
        text_parameter_encoding_selector: OptionsTextParameterEncodingSelector = field(
            default=OptionsTextParameterEncodingSelector.USE_TEXT_PARAMETER_ENCODING_CODE_PAGE,
            metadata={
                "name": "TextParameterEncodingSelector",
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
        parameter_byte_order: OptionsParameterByteOrder = field(
            default=OptionsParameterByteOrder.BIG_ENDIAN,
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
        line_coupler0912_new_programming_style: bool = field(
            default=False,
            metadata={
                "name": "LineCoupler0912NewProgrammingStyle",
                "type": "Attribute",
            },
        )
        comparable: None | bool = field(
            default=None,
            metadata={
                "name": "Comparable",
                "type": "Attribute",
            },
        )
        reconstructable: None | bool = field(
            default=None,
            metadata={
                "name": "Reconstructable",
                "type": "Attribute",
            },
        )
        download_invisible_parameters: DownloadBehaviorT = field(
            default=DownloadBehaviorT.DEFAULT_VALUE,
            metadata={
                "name": "DownloadInvisibleParameters",
                "type": "Attribute",
            },
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
            "namespace": "http://knx.org/xml/project/12",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterBlockT:
    """
    :ivar parameter_block:
    :ivar parameter_separator:
    :ivar parameter_ref_ref:
    :ivar choose:
    :ivar binary_data_ref:
    :ivar com_object_ref_ref:
    :ivar assign:
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar help_topic:
    :ivar internal_description:
    :ivar param_ref_id: registration-relevant
    :ivar text_parameter_ref_id:
    """

    class Meta:
        name = "ComObjectParameterBlock_t"

    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameter_separator: list[ParameterSeparatorT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterSeparator",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    parameter_ref_ref: list[ParameterRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    choose: list[ComObjectParameterChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    binary_data_ref: list[BinaryDataRefT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryDataRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    com_object_ref_ref: list[ComObjectRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    assign: list[AssignT] = field(
        default_factory=list,
        metadata={
            "name": "Assign",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    text_parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "TextParameterRefId",
            "type": "Attribute",
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
    :ivar is_rfretransmitter: registration-relevant
    :ivar runtime_unidirectional: registration-relevant
    :ivar original_manufacturer: registration-relevant
    :ivar rfdevice_mode: registration-relevant
    :ivar no_download_without_plugin:
    :ivar non_reg_relevant_data_version:
    :ivar internal_description:
    """

    class Meta:
        name = "Hardware_t"

    products: None | HardwareT.Products = field(
        default=None,
        metadata={
            "name": "Products",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    hardware2_programs: None | HardwareT.Hardware2Programs = field(
        default=None,
        metadata={
            "name": "Hardware2Programs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    is_rfretransmitter: bool = field(
        default=False,
        metadata={
            "name": "IsRFRetransmitter",
            "type": "Attribute",
        },
    )
    runtime_unidirectional: bool = field(
        default=False,
        metadata={
            "name": "RuntimeUnidirectional",
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
    rfdevice_mode: RfdeviceModeT = field(
        default=RfdeviceModeT.READY,
        metadata={
            "name": "RFDeviceMode",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Products:
        product: list[HardwareT.Products.Product] = field(
            default_factory=list,
            metadata={
                "name": "Product",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Product:
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
            :ivar internal_description:
            """

            baggages: None | HardwareT.Products.Product.Baggages = field(
                default=None,
                metadata={
                    "name": "Baggages",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            attributes: None | HardwareT.Products.Product.Attributes = field(
                default=None,
                metadata={
                    "name": "Attributes",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            registration_info: None | RegistrationInfoT = field(
                default=None,
                metadata={
                    "name": "RegistrationInfo",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )

            @dataclass(slots=True, kw_only=True)
            class Baggages:
                baggage: list[HardwareT.Products.Product.Baggages.Baggage] = field(
                    default_factory=list,
                    metadata={
                        "name": "Baggage",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                        "min_occurs": 1,
                    },
                )

                @dataclass(slots=True, kw_only=True)
                class Baggage:
                    ref_id: str = field(
                        metadata={
                            "name": "RefId",
                            "type": "Attribute",
                        }
                    )

            @dataclass(slots=True, kw_only=True)
            class Attributes:
                attribute: list[HardwareT.Products.Product.Attributes.Attribute] = field(
                    default_factory=list,
                    metadata={
                        "name": "Attribute",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                        "min_occurs": 1,
                    },
                )

                @dataclass(slots=True, kw_only=True)
                class Attribute:
                    id: None | str = field(
                        default=None,
                        metadata={
                            "name": "Id",
                            "type": "Attribute",
                        },
                    )
                    name: AttributeName = field(
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
    class Hardware2Programs:
        hardware2_program: list[Hardware2ProgramT] = field(
            default_factory=list,
            metadata={
                "name": "Hardware2Program",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class MaskVersionT:
    class Meta:
        name = "MaskVersion_t"

    downward_compatible_masks: None | MaskVersionT.DownwardCompatibleMasks = field(
        default=None,
        metadata={
            "name": "DownwardCompatibleMasks",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    mask_entries: None | MaskVersionT.MaskEntries = field(
        default=None,
        metadata={
            "name": "MaskEntries",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    hawk_configuration_data: list[HawkConfigurationDataT] = field(
        default_factory=list,
        metadata={
            "name": "HawkConfigurationData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    class DownwardCompatibleMasks:
        downward_compatible_mask: list[MaskVersionT.DownwardCompatibleMasks.DownwardCompatibleMask] = field(
            default_factory=list,
            metadata={
                "name": "DownwardCompatibleMask",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class DownwardCompatibleMask:
            ref_id: str = field(
                metadata={
                    "name": "RefId",
                    "type": "Attribute",
                }
            )

    @dataclass(slots=True, kw_only=True)
    class MaskEntries:
        mask_entry: list[MaskVersionT.MaskEntries.MaskEntry] = field(
            default_factory=list,
            metadata={
                "name": "MaskEntry",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class MaskEntry:
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
class TopologyT:
    class Meta:
        name = "Topology_t"

    area: list[TopologyT.Area] = field(
        default_factory=list,
        metadata={
            "name": "Area",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "max_occurs": 16,
        },
    )
    unassigned_devices: None | TopologyT.UnassignedDevices = field(
        default=None,
        metadata={
            "name": "UnassignedDevices",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Area:
        line: list[TopologyT.Area.Line] = field(
            default_factory=list,
            metadata={
                "name": "Line",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
        puid: int = field(
            metadata={
                "name": "Puid",
                "type": "Attribute",
            }
        )

        @dataclass(slots=True, kw_only=True)
        class Line:
            device_instance: list[DeviceInstanceT] = field(
                default_factory=list,
                metadata={
                    "name": "DeviceInstance",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            bus_access: None | BusAccessT = field(
                default=None,
                metadata={
                    "name": "BusAccess",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            additional_group_addresses: None | TopologyT.Area.Line.AdditionalGroupAddresses = field(
                default=None,
                metadata={
                    "name": "AdditionalGroupAddresses",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            puid: int = field(
                metadata={
                    "name": "Puid",
                    "type": "Attribute",
                }
            )

            @dataclass(slots=True, kw_only=True)
            class AdditionalGroupAddresses:
                group_address: list[TopologyT.Area.Line.AdditionalGroupAddresses.GroupAddress] = field(
                    default_factory=list,
                    metadata={
                        "name": "GroupAddress",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                        "min_occurs": 1,
                    },
                )

                @dataclass(slots=True, kw_only=True)
                class GroupAddress:
                    address: int = field(
                        metadata={
                            "name": "Address",
                            "type": "Attribute",
                        }
                    )

    @dataclass(slots=True, kw_only=True)
    class UnassignedDevices:
        device_instance: list[DeviceInstanceT] = field(
            default_factory=list,
            metadata={
                "name": "DeviceInstance",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ChannelChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "ChannelChoose_t"

    when: list[ChannelChooseT.When] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class When(WhenT):
        parameter_block: list[ComObjectParameterBlockT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterBlock",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        com_object_ref_ref: list[ComObjectRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        binary_data_ref: list[BinaryDataRefT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryDataRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        choose: list[ChannelChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )


@dataclass(slots=True, kw_only=True)
class MasterDataT:
    class Meta:
        name = "MasterData_t"

    datapoint_types: None | MasterDataT.DatapointTypes = field(
        default=None,
        metadata={
            "name": "DatapointTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    interface_object_types: None | MasterDataT.InterfaceObjectTypes = field(
        default=None,
        metadata={
            "name": "InterfaceObjectTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    interface_object_properties: None | MasterDataT.InterfaceObjectProperties = field(
        default=None,
        metadata={
            "name": "InterfaceObjectProperties",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    property_data_types: None | MasterDataT.PropertyDataTypes = field(
        default=None,
        metadata={
            "name": "PropertyDataTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    medium_types: None | MasterDataT.MediumTypes = field(
        default=None,
        metadata={
            "name": "MediumTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    mask_versions: None | MasterDataT.MaskVersions = field(
        default=None,
        metadata={
            "name": "MaskVersions",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    functional_blocks: None | MasterDataT.FunctionalBlocks = field(
        default=None,
        metadata={
            "name": "FunctionalBlocks",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    product_languages: None | MasterDataT.ProductLanguages = field(
        default=None,
        metadata={
            "name": "ProductLanguages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    manufacturers: None | MasterDataT.Manufacturers = field(
        default=None,
        metadata={
            "name": "Manufacturers",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    languages: None | MasterDataT.Languages = field(
        default=None,
        metadata={
            "name": "Languages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class DatapointTypes:
        datapoint_type: list[MasterDataT.DatapointTypes.DatapointType] = field(
            default_factory=list,
            metadata={
                "name": "DatapointType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class DatapointType:
            datapoint_subtypes: None | MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes = field(
                default=None,
                metadata={
                    "name": "DatapointSubtypes",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            default: None | bool = field(
                default=None,
                metadata={
                    "name": "Default",
                    "type": "Attribute",
                },
            )
            pdt: None | str = field(
                default=None,
                metadata={
                    "name": "PDT",
                    "type": "Attribute",
                },
            )

            @dataclass(slots=True, kw_only=True)
            class DatapointSubtypes:
                datapoint_subtype: list[MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype] = (
                    field(
                        default_factory=list,
                        metadata={
                            "name": "DatapointSubtype",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/12",
                            "min_occurs": 1,
                        },
                    )
                )

                @dataclass(slots=True, kw_only=True)
                class DatapointSubtype:
                    format: (
                        None | MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format
                    ) = field(
                        default=None,
                        metadata={
                            "name": "Format",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/12",
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
                    default: bool = field(
                        default=False,
                        metadata={
                            "name": "Default",
                            "type": "Attribute",
                        },
                    )
                    pdt: None | str = field(
                        default=None,
                        metadata={
                            "name": "PDT",
                            "type": "Attribute",
                        },
                    )

                    @dataclass(slots=True, kw_only=True)
                    class Format:
                        bit: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.Bit
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "Bit",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        unsigned_integer: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.UnsignedInteger
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "UnsignedInteger",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        signed_integer: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.SignedInteger
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "SignedInteger",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        string: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.String
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "String",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        float_value: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.Float
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "Float",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        enumeration: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.Enumeration
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "Enumeration",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        reserved: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.Reserved
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "Reserved",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )
                        ref_type: list[
                            MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.RefType
                        ] = field(
                            default_factory=list,
                            metadata={
                                "name": "RefType",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                            },
                        )

                        @dataclass(slots=True, kw_only=True)
                        class Bit:
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
                                },
                            )
                            set: str = field(
                                metadata={
                                    "name": "Set",
                                    "type": "Attribute",
                                }
                            )
                            cleared: str = field(
                                metadata={
                                    "name": "Cleared",
                                    "type": "Attribute",
                                }
                            )

                        @dataclass(slots=True, kw_only=True)
                        class UnsignedInteger:
                            id: str = field(
                                metadata={
                                    "name": "Id",
                                    "type": "Attribute",
                                }
                            )
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )
                            name: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Name",
                                    "type": "Attribute",
                                },
                            )
                            unit: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Unit",
                                    "type": "Attribute",
                                },
                            )
                            min_inclusive: None | int = field(
                                default=None,
                                metadata={
                                    "name": "MinInclusive",
                                    "type": "Attribute",
                                },
                            )
                            max_inclusive: None | int = field(
                                default=None,
                                metadata={
                                    "name": "MaxInclusive",
                                    "type": "Attribute",
                                },
                            )
                            coefficient: None | float = field(
                                default=None,
                                metadata={
                                    "name": "Coefficient",
                                    "type": "Attribute",
                                },
                            )

                        @dataclass(slots=True, kw_only=True)
                        class SignedInteger:
                            id: str = field(
                                metadata={
                                    "name": "Id",
                                    "type": "Attribute",
                                }
                            )
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )
                            name: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Name",
                                    "type": "Attribute",
                                },
                            )
                            unit: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Unit",
                                    "type": "Attribute",
                                },
                            )
                            min_inclusive: None | int = field(
                                default=None,
                                metadata={
                                    "name": "MinInclusive",
                                    "type": "Attribute",
                                },
                            )
                            max_inclusive: None | int = field(
                                default=None,
                                metadata={
                                    "name": "MaxInclusive",
                                    "type": "Attribute",
                                },
                            )
                            coefficient: None | float = field(
                                default=None,
                                metadata={
                                    "name": "Coefficient",
                                    "type": "Attribute",
                                },
                            )

                        @dataclass(slots=True, kw_only=True)
                        class String:
                            id: str = field(
                                metadata={
                                    "name": "Id",
                                    "type": "Attribute",
                                }
                            )
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )
                            name: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Name",
                                    "type": "Attribute",
                                },
                            )
                            unit: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Unit",
                                    "type": "Attribute",
                                },
                            )
                            encoding: None | TextEncodingT = field(
                                default=None,
                                metadata={
                                    "name": "Encoding",
                                    "type": "Attribute",
                                },
                            )

                        @dataclass(slots=True, kw_only=True)
                        class Float:
                            id: str = field(
                                metadata={
                                    "name": "Id",
                                    "type": "Attribute",
                                }
                            )
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )
                            name: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Name",
                                    "type": "Attribute",
                                },
                            )
                            unit: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Unit",
                                    "type": "Attribute",
                                },
                            )
                            coefficient: None | float = field(
                                default=None,
                                metadata={
                                    "name": "Coefficient",
                                    "type": "Attribute",
                                },
                            )
                            min_value: None | float = field(
                                default=None,
                                metadata={
                                    "name": "MinValue",
                                    "type": "Attribute",
                                },
                            )
                            max_value: None | float = field(
                                default=None,
                                metadata={
                                    "name": "MaxValue",
                                    "type": "Attribute",
                                },
                            )

                        @dataclass(slots=True, kw_only=True)
                        class Enumeration:
                            enum_value: list[
                                MasterDataT.DatapointTypes.DatapointType.DatapointSubtypes.DatapointSubtype.Format.Enumeration.EnumValue
                            ] = field(
                                default_factory=list,
                                metadata={
                                    "name": "EnumValue",
                                    "type": "Element",
                                    "namespace": "http://knx.org/xml/project/12",
                                    "min_occurs": 1,
                                },
                            )
                            id: str = field(
                                metadata={
                                    "name": "Id",
                                    "type": "Attribute",
                                }
                            )
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )
                            name: None | str = field(
                                default=None,
                                metadata={
                                    "name": "Name",
                                    "type": "Attribute",
                                },
                            )

                            @dataclass(slots=True, kw_only=True)
                            class EnumValue:
                                id: str = field(
                                    metadata={
                                        "name": "Id",
                                        "type": "Attribute",
                                    }
                                )
                                value: int = field(
                                    metadata={
                                        "name": "Value",
                                        "type": "Attribute",
                                    }
                                )
                                text: str = field(
                                    metadata={
                                        "name": "Text",
                                        "type": "Attribute",
                                    }
                                )

                        @dataclass(slots=True, kw_only=True)
                        class Reserved:
                            width: int = field(
                                metadata={
                                    "name": "Width",
                                    "type": "Attribute",
                                }
                            )

                        @dataclass(slots=True, kw_only=True)
                        class RefType:
                            ref_id: str = field(
                                metadata={
                                    "name": "RefId",
                                    "type": "Attribute",
                                }
                            )

    @dataclass(slots=True, kw_only=True)
    class InterfaceObjectTypes:
        interface_object_type: list[MasterDataT.InterfaceObjectTypes.InterfaceObjectType] = field(
            default_factory=list,
            metadata={
                "name": "InterfaceObjectType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class InterfaceObjectType:
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
    class InterfaceObjectProperties:
        interface_object_property: list[MasterDataT.InterfaceObjectProperties.InterfaceObjectProperty] = field(
            default_factory=list,
            metadata={
                "name": "InterfaceObjectProperty",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class InterfaceObjectProperty:
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
            object_type: None | str = field(
                default=None,
                metadata={
                    "name": "ObjectType",
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
            text: None | str = field(
                default=None,
                metadata={
                    "name": "Text",
                    "type": "Attribute",
                    "max_length": 255,
                },
            )
            pdt: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "PDT",
                    "type": "Attribute",
                    "tokens": True,
                },
            )
            dpt: None | str = field(
                default=None,
                metadata={
                    "name": "DPT",
                    "type": "Attribute",
                },
            )
            array: bool = field(
                default=False,
                metadata={
                    "name": "Array",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class PropertyDataTypes:
        property_data_type: list[MasterDataT.PropertyDataTypes.PropertyDataType] = field(
            default_factory=list,
            metadata={
                "name": "PropertyDataType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class PropertyDataType:
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
            size: None | int = field(
                default=None,
                metadata={
                    "name": "Size",
                    "type": "Attribute",
                },
            )
            read_size: None | int = field(
                default=None,
                metadata={
                    "name": "ReadSize",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class MediumTypes:
        medium_type: list[MasterDataT.MediumTypes.MediumType] = field(
            default_factory=list,
            metadata={
                "name": "MediumType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class MediumType:
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

    @dataclass(slots=True, kw_only=True)
    class MaskVersions:
        mask_version: list[MaskVersionT] = field(
            default_factory=list,
            metadata={
                "name": "MaskVersion",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class FunctionalBlocks:
        functional_block: list[MasterDataT.FunctionalBlocks.FunctionalBlock] = field(
            default_factory=list,
            metadata={
                "name": "FunctionalBlock",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class FunctionalBlock:
            parameters: list[MasterDataT.FunctionalBlocks.FunctionalBlock.Parameters] = field(
                default_factory=list,
                metadata={
                    "name": "Parameters",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            name: str = field(
                metadata={
                    "name": "Name",
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
            class Parameters:
                parameter: list[MasterDataT.FunctionalBlocks.FunctionalBlock.Parameters.Parameter] = field(
                    default_factory=list,
                    metadata={
                        "name": "Parameter",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                        "min_occurs": 1,
                    },
                )
                object_type: str = field(
                    metadata={
                        "name": "ObjectType",
                        "type": "Attribute",
                    }
                )

                @dataclass(slots=True, kw_only=True)
                class Parameter:
                    property: str = field(
                        metadata={
                            "name": "Property",
                            "type": "Attribute",
                        }
                    )
                    description: None | str = field(
                        default=None,
                        metadata={
                            "name": "Description",
                            "type": "Attribute",
                        },
                    )

    @dataclass(slots=True, kw_only=True)
    class ProductLanguages:
        language: list[MasterDataT.ProductLanguages.Language] = field(
            default_factory=list,
            metadata={
                "name": "Language",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Language:
            identifier: None | str = field(
                default=None,
                metadata={
                    "name": "Identifier",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class Manufacturers:
        manufacturer: list[MasterDataT.Manufacturers.Manufacturer] = field(
            default_factory=list,
            metadata={
                "name": "Manufacturer",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Manufacturer:
            order_number_formatting_script: None | str = field(
                default=None,
                metadata={
                    "name": "OrderNumberFormattingScript",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            public_keys: None | MasterDataT.Manufacturers.Manufacturer.PublicKeys = field(
                default=None,
                metadata={
                    "name": "PublicKeys",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            import_restriction: ManufacturerImportRestriction = field(
                default=ManufacturerImportRestriction.OWN,
                metadata={
                    "name": "ImportRestriction",
                    "type": "Attribute",
                },
            )
            import_group: list[str] = field(
                default_factory=list,
                metadata={
                    "name": "ImportGroup",
                    "type": "Attribute",
                    "tokens": True,
                },
            )

            @dataclass(slots=True, kw_only=True)
            class PublicKeys:
                public_key: list[MasterDataT.Manufacturers.Manufacturer.PublicKeys.PublicKey] = field(
                    default_factory=list,
                    metadata={
                        "name": "PublicKey",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                    },
                )

                @dataclass(slots=True, kw_only=True)
                class PublicKey:
                    rsakey_value: MasterDataT.Manufacturers.Manufacturer.PublicKeys.PublicKey.RsakeyValue = field(
                        metadata={
                            "name": "RSAKeyValue",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/12",
                        }
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
                    revoked: bool = field(
                        default=False,
                        metadata={
                            "name": "Revoked",
                            "type": "Attribute",
                        },
                    )

                    @dataclass(slots=True, kw_only=True)
                    class RsakeyValue:
                        modulus: bytes = field(
                            metadata={
                                "name": "Modulus",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                                "format": "base64",
                            }
                        )
                        exponent: bytes = field(
                            metadata={
                                "name": "Exponent",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/12",
                                "format": "base64",
                            }
                        )

    @dataclass(slots=True, kw_only=True)
    class Languages:
        language: list[LanguageDataT] = field(
            default_factory=list,
            metadata={
                "name": "Language",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ProjectT:
    class Meta:
        name = "Project_t"

    project_information: None | ProjectT.ProjectInformation = field(
        default=None,
        metadata={
            "name": "ProjectInformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    installations: None | ProjectT.Installations = field(
        default=None,
        metadata={
            "name": "Installations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    user_files: None | ProjectT.UserFiles = field(
        default=None,
        metadata={
            "name": "UserFiles",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    addin_data: None | ProjectT.AddinData = field(
        default=None,
        metadata={
            "name": "AddinData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class ProjectInformation:
        history_entries: None | ProjectT.ProjectInformation.HistoryEntries = field(
            default=None,
            metadata={
                "name": "HistoryEntries",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        to_do_items: None | ProjectT.ProjectInformation.ToDoItems = field(
            default=None,
            metadata={
                "name": "ToDoItems",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        project_traces: None | ProjectT.ProjectInformation.ProjectTraces = field(
            default=None,
            metadata={
                "name": "ProjectTraces",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
        project_tracing_password: None | str = field(
            default=None,
            metadata={
                "name": "ProjectTracingPassword",
                "type": "Attribute",
                "max_length": 20,
            },
        )
        hide16_bit_groups_from_legacy_plugins: bool = field(
            default=False,
            metadata={
                "name": "Hide16BitGroupsFromLegacyPlugins",
                "type": "Attribute",
            },
        )
        code_page: None | TextEncodingT = field(
            default=None,
            metadata={
                "name": "CodePage",
                "type": "Attribute",
            },
        )
        bus_access_legacy_mode: bool = field(
            default=False,
            metadata={
                "name": "BusAccessLegacyMode",
                "type": "Attribute",
            },
        )
        guid: str = field(
            metadata={
                "name": "Guid",
                "type": "Attribute",
            }
        )
        last_used_puid: int = field(
            metadata={
                "name": "LastUsedPuid",
                "type": "Attribute",
            }
        )

        @dataclass(slots=True, kw_only=True)
        class HistoryEntries:
            history_entry: list[ProjectT.ProjectInformation.HistoryEntries.HistoryEntry] = field(
                default_factory=list,
                metadata={
                    "name": "HistoryEntry",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

            @dataclass(slots=True, kw_only=True)
            class HistoryEntry:
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

        @dataclass(slots=True, kw_only=True)
        class ToDoItems:
            to_do_item: list[ToDoItemT] = field(
                default_factory=list,
                metadata={
                    "name": "ToDoItem",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

        @dataclass(slots=True, kw_only=True)
        class ProjectTraces:
            project_trace: list[ProjectTraceT] = field(
                default_factory=list,
                metadata={
                    "name": "ProjectTrace",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

    @dataclass(slots=True, kw_only=True)
    class Installations:
        installation: list[ProjectT.Installations.Installation] = field(
            default_factory=list,
            metadata={
                "name": "Installation",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
                "min_occurs": 1,
                "max_occurs": 16,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Installation:
            topology: TopologyT = field(
                metadata={
                    "name": "Topology",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                }
            )
            buildings: BuildingsT = field(
                metadata={
                    "name": "Buildings",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                }
            )
            group_addresses: GroupAddressesT = field(
                metadata={
                    "name": "GroupAddresses",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                }
            )
            trades: None | TradesT = field(
                default=None,
                metadata={
                    "name": "Trades",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            bus_access: None | BusAccessT = field(
                default=None,
                metadata={
                    "name": "BusAccess",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                },
            )
            split_infos: None | SplitInfosT = field(
                default=None,
                metadata={
                    "name": "SplitInfos",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
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
            multicast_ttl: int = field(
                default=16,
                metadata={
                    "name": "MulticastTTL",
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
            completion_status: CompletionStatusT = field(
                default=CompletionStatusT.UNDEFINED,
                metadata={
                    "name": "CompletionStatus",
                    "type": "Attribute",
                },
            )
            split_type: None | InstallationSplitType = field(
                default=None,
                metadata={
                    "name": "SplitType",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class UserFiles:
        user_file: list[UserFileT] = field(
            default_factory=list,
            metadata={
                "name": "UserFile",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class AddinData:
        addin_data: list[AddinDataT] = field(
            default_factory=list,
            metadata={
                "name": "AddinData",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramChannelT:
    """
    :ivar parameter_block:
    :ivar com_object_ref_ref:
    :ivar binary_data_ref:
    :ivar choose:
    :ivar name:
    :ivar text:
    :ivar number: registration-relevant
    :ivar id: registration-relevant
    :ivar text_parameter_ref_id:
    :ivar internal_description:
    """

    class Meta:
        name = "ApplicationProgramChannel_t"

    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    com_object_ref_ref: list[ComObjectRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    binary_data_ref: list[BinaryDataRefT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryDataRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    choose: list[ChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
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
    text_parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "TextParameterRefId",
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
class DependentChannelChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "DependentChannelChoose_t"

    when: list[DependentChannelChooseT.When] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )
    param_ref_id: str = field(
        metadata={
            "name": "ParamRefId",
            "type": "Attribute",
        }
    )
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class When(WhenT):
        channel: list[ApplicationProgramChannelT] = field(
            default_factory=list,
            metadata={
                "name": "Channel",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        choose: list[DependentChannelChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramDynamicT:
    class Meta:
        name = "ApplicationProgramDynamic_t"

    channel_independent_block: list[ApplicationProgramDynamicT.ChannelIndependentBlock] = field(
        default_factory=list,
        metadata={
            "name": "ChannelIndependentBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    channel: list[ApplicationProgramChannelT] = field(
        default_factory=list,
        metadata={
            "name": "Channel",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )
    choose: list[DependentChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class ChannelIndependentBlock:
        parameter_block: list[ComObjectParameterBlockT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterBlock",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        choose: list[ChannelChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        binary_data_ref: list[BinaryDataRefT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryDataRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        com_object_ref_ref: list[ComObjectRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
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
    :ivar created_from_legacy_schema_version:
    :ivar ipconfig: registration-relevant
    :ivar additional_addresses_count: registration-relevant
    :ivar non_reg_relevant_data_version:
    :ivar broken:
    :ivar download_info_incomplete:
    :ivar replaces_versions: registration-relevant
    :ivar hash:
    :ivar internal_description:
    """

    class Meta:
        name = "ApplicationProgram_t"

    static: ApplicationProgramStaticT = field(
        metadata={
            "name": "Static",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
        }
    )
    dynamic: None | ApplicationProgramDynamicT = field(
        default=None,
        metadata={
            "name": "Dynamic",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
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
    min_ets_version: None | str = field(
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
    created_from_legacy_schema_version: bool = field(
        default=False,
        metadata={
            "name": "CreatedFromLegacySchemaVersion",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ManufacturerDataT:
    class Meta:
        name = "ManufacturerData_t"

    manufacturer: list[ManufacturerDataT.Manufacturer] = field(
        default_factory=list,
        metadata={
            "name": "Manufacturer",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/12",
            "min_occurs": 1,
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Manufacturer:
        catalog: None | ManufacturerDataT.Manufacturer.Catalog = field(
            default=None,
            metadata={
                "name": "Catalog",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        application_programs: None | ManufacturerDataT.Manufacturer.ApplicationPrograms = field(
            default=None,
            metadata={
                "name": "ApplicationPrograms",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        baggages: None | ManufacturerDataT.Manufacturer.Baggages = field(
            default=None,
            metadata={
                "name": "Baggages",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        hardware: None | ManufacturerDataT.Manufacturer.Hardware = field(
            default=None,
            metadata={
                "name": "Hardware",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        languages: None | ManufacturerDataT.Manufacturer.Languages = field(
            default=None,
            metadata={
                "name": "Languages",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/12",
            },
        )
        ref_id: str = field(
            metadata={
                "name": "RefId",
                "type": "Attribute",
            }
        )

        @dataclass(slots=True, kw_only=True)
        class Catalog:
            catalog_section: list[CatalogSectionT] = field(
                default_factory=list,
                metadata={
                    "name": "CatalogSection",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

        @dataclass(slots=True, kw_only=True)
        class ApplicationPrograms:
            application_program: list[ApplicationProgramT] = field(
                default_factory=list,
                metadata={
                    "name": "ApplicationProgram",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

        @dataclass(slots=True, kw_only=True)
        class Baggages:
            baggage: list[ManufacturerDataT.Manufacturer.Baggages.Baggage] = field(
                default_factory=list,
                metadata={
                    "name": "Baggage",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

            @dataclass(slots=True, kw_only=True)
            class Baggage:
                file_info: ManufacturerDataT.Manufacturer.Baggages.Baggage.FileInfo = field(
                    metadata={
                        "name": "FileInfo",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/12",
                    }
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
                file_integrity: str = field(
                    default="00000000",
                    metadata={
                        "name": "FileIntegrity",
                        "type": "Attribute",
                    },
                )
                id: str = field(
                    metadata={
                        "name": "Id",
                        "type": "Attribute",
                    }
                )

                @dataclass(slots=True, kw_only=True)
                class FileInfo:
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
        class Hardware:
            hardware: list[HardwareT] = field(
                default_factory=list,
                metadata={
                    "name": "Hardware",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )

        @dataclass(slots=True, kw_only=True)
        class Languages:
            language: list[LanguageDataT] = field(
                default_factory=list,
                metadata={
                    "name": "Language",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/12",
                    "min_occurs": 1,
                },
            )


@dataclass(slots=True, kw_only=True)
class Knx:
    class Meta:
        name = "KNX"
        namespace = "http://knx.org/xml/project/12"

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
