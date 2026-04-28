from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from xsdata.models.datatype import XmlDate, XmlDateTime

__NAMESPACE__ = "http://knx.org/xml/project/22"


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


@dataclass(slots=True, kw_only=True)
class AllocatorT:
    """
    :ivar id:
    :ivar name: registration-relevant
    :ivar internal_description:
    :ivar start: registration-relevant
    :ivar max_inclusive: registration-relevant
    :ivar error_message_ref:
    """

    class Meta:
        name = "Allocator_t"

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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    start: int = field(
        metadata={
            "name": "Start",
            "type": "Attribute",
        }
    )
    max_inclusive: int = field(
        metadata={
            "name": "maxInclusive",
            "type": "Attribute",
        }
    )
    error_message_ref: None | str = field(
        default=None,
        metadata={
            "name": "ErrorMessageRef",
            "type": "Attribute",
        },
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


class ArgumentAlignment(Enum):
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_4 = 4
    VALUE_8 = 8


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
            "namespace": "http://knx.org/xml/project/22",
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
            "namespace": "http://knx.org/xml/project/22",
            "format": "base64",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )


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
    parameter: str = field(
        metadata={
            "name": "Parameter",
            "type": "Attribute",
        }
    )


class BusInterfaceAccessType(Enum):
    TUNNELING = "Tunneling"
    USB = "USB"
    ROUTING = "Routing"
    INTERNAL = "Internal"


@dataclass(slots=True, kw_only=True)
class BusInterfaceT:
    class Meta:
        name = "BusInterface_t"

    connectors: None | BusInterfaceT.Connectors = field(
        default=None,
        metadata={
            "name": "Connectors",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
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
            "max_length": 255,
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
    password: None | str = field(
        default=None,
        metadata={
            "name": "Password",
            "type": "Attribute",
            "max_length": 20,
        },
    )
    password_hash: None | bytes = field(
        default=None,
        metadata={
            "name": "PasswordHash",
            "type": "Attribute",
            "format": "base64",
        },
    )
    is_secure_enabled: bool = field(
        default=True,
        metadata={
            "name": "IsSecureEnabled",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Connectors:
        connector: list[BusInterfaceT.Connectors.Connector] = field(
            default_factory=list,
            metadata={
                "name": "Connector",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Connector:
            group_address_ref_id: str = field(
                metadata={
                    "name": "GroupAddressRefId",
                    "type": "Attribute",
                }
            )


class ButtonTEventHandlerOnline(Enum):
    CONNECTION_LESS = "ConnectionLess"
    CONNECTION_ORIENTED = "ConnectionOriented"


@dataclass(slots=True, kw_only=True)
class CalculationParameterRefT:
    """
    :ivar ref_id: registration-relevant
    :ivar internal_description:
    :ivar alias_name: registration-relevant
    """

    class Meta:
        name = "CalculationParameterRef_t"

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
    alias_name: None | str = field(
        default=None,
        metadata={
            "name": "AliasName",
            "type": "Attribute",
            "max_length": 50,
        },
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    catalog_item: list[CatalogSectionT.CatalogItem] = field(
        default_factory=list,
        metadata={
            "name": "CatalogItem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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


@dataclass(slots=True, kw_only=True)
class ChannelInstanceT:
    class Meta:
        name = "ChannelInstance_t"

    id: str = field(
        metadata={
            "name": "Id",
            "type": "Attribute",
        }
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
            "max_length": 255,
        },
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    is_active: None | bool = field(
        default=None,
        metadata={
            "name": "IsActive",
            "type": "Attribute",
        },
    )
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
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


class ComObjectSecurityRequirementsT(Enum):
    NONE = "None"
    AUTH = "Auth"
    AUTH_AND_CONF = "AuthAndConf"


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
    VALUE_13_BYTES = "13 Bytes"
    VALUE_15_BYTES = "15 Bytes"
    VALUE_16_BYTES = "16 Bytes"
    VALUE_17_BYTES = "17 Bytes"
    VALUE_18_BYTES = "18 Bytes"
    VALUE_19_BYTES = "19 Bytes"
    VALUE_20_BYTES = "20 Bytes"
    VALUE_21_BYTES = "21 Bytes"
    VALUE_22_BYTES = "22 Bytes"
    VALUE_23_BYTES = "23 Bytes"
    VALUE_24_BYTES = "24 Bytes"
    VALUE_25_BYTES = "25 Bytes"
    VALUE_26_BYTES = "26 Bytes"
    VALUE_27_BYTES = "27 Bytes"
    VALUE_28_BYTES = "28 Bytes"
    VALUE_29_BYTES = "29 Bytes"
    VALUE_30_BYTES = "30 Bytes"
    VALUE_31_BYTES = "31 Bytes"
    VALUE_32_BYTES = "32 Bytes"
    VALUE_33_BYTES = "33 Bytes"
    VALUE_34_BYTES = "34 Bytes"
    VALUE_35_BYTES = "35 Bytes"
    VALUE_36_BYTES = "36 Bytes"
    VALUE_37_BYTES = "37 Bytes"
    VALUE_38_BYTES = "38 Bytes"
    VALUE_39_BYTES = "39 Bytes"
    VALUE_40_BYTES = "40 Bytes"
    VALUE_41_BYTES = "41 Bytes"
    VALUE_42_BYTES = "42 Bytes"
    VALUE_43_BYTES = "43 Bytes"
    VALUE_44_BYTES = "44 Bytes"
    VALUE_45_BYTES = "45 Bytes"
    VALUE_46_BYTES = "46 Bytes"
    VALUE_47_BYTES = "47 Bytes"
    VALUE_48_BYTES = "48 Bytes"
    VALUE_49_BYTES = "49 Bytes"
    VALUE_50_BYTES = "50 Bytes"


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


class CouplerCapabilityT(Enum):
    RF_READY = "RfReady"
    RF_MULTI_FAST = "RfMultiFast"
    RF_MULTI_SLOW = "RfMultiSlow"
    SECURITY_PROXY = "SecurityProxy"
    SEGMENT_COUPLER = "SegmentCoupler"


class DeprecationStatusT(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass(slots=True, kw_only=True)
class DeviceCertificateT:
    class Meta:
        name = "DeviceCertificate_t"

    serial_number: bytes = field(
        metadata={
            "name": "SerialNumber",
            "type": "Attribute",
            "format": "base64",
        }
    )
    fdsk: None | str = field(
        default=None,
        metadata={
            "name": "FDSK",
            "type": "Attribute",
            "max_length": 100,
        },
    )
    password: None | str = field(
        default=None,
        metadata={
            "name": "Password",
            "type": "Attribute",
        },
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
    SUPPORTS_CONFIRMED_RESTART = "SupportsConfirmedRestart"
    SUPPORTS_INTERFACE_OBJECTS = "SupportsInterfaceObjects"
    MAY_SUPPORT_LONG_FRAMES = "MaySupportLongFrames"


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
            "namespace": "http://knx.org/xml/project/22",
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
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
            "type": "Attribute",
        },
    )


class GroupAddressStyleT(Enum):
    TWO_LEVEL = "TwoLevel"
    THREE_LEVEL = "ThreeLevel"
    FREE = "Free"


class HorizontalAlignmentT(Enum):
    LEFT = "Left"
    MIDDLE = "Middle"
    RIGHT = "Right"
    STRETCH = "Stretch"
    REPEAT = "Repeat"


class IpconfigAssignT(Enum):
    FIXED = "Fixed"
    AUTO = "Auto"


class InstallationSplitType(Enum):
    NONE = "None"
    MASTER = "Master"
    SPLIT = "Split"


@dataclass(slots=True, kw_only=True)
class IoTpointParameterT:
    """
    :ivar point_reference: registration-relevant
    """

    class Meta:
        name = "IoTPointParameter_t"

    point_reference: str = field(
        metadata={
            "name": "PointReference",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LanguageDataT:
    class Meta:
        name = "LanguageData_t"

    translation_unit: list[LanguageDataT.TranslationUnit] = field(
        default_factory=list,
        metadata={
            "name": "TranslationUnit",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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


class LdCtrlErrorCauseT(Enum):
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    COMPARE_MISMATCH = "CompareMismatch"


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


class MemberStatusT(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


@dataclass(slots=True, kw_only=True)
class MemoryParameterT:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        name = "MemoryParameter_t"

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


class MemoryTypeT(Enum):
    RAM = "RAM"
    EEPROM = "EEPROM"
    FLASH = "FLASH"


@dataclass(slots=True, kw_only=True)
class MemoryUnionT:
    """
    :ivar code_segment: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        name = "MemoryUnion_t"

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
class ModuleArgT:
    """
    :ivar ref_id: registration-relevant
    """

    class Meta:
        name = "ModuleArg_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )


class ModuleDefArgTypeT(Enum):
    NUMERIC = "Numeric"
    TEXT = "Text"


@dataclass(slots=True, kw_only=True)
class ModuleInstanceT:
    class Meta:
        name = "ModuleInstance_t"

    arguments: None | ModuleInstanceT.Arguments = field(
        default=None,
        metadata={
            "name": "Arguments",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    repeat_index: list[str] = field(
        default_factory=list,
        metadata={
            "name": "RepeatIndex",
            "type": "Attribute",
            "pattern": r"\d+x\d+",
            "tokens": True,
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Arguments:
        argument: list[ModuleInstanceT.Arguments.Argument] = field(
            default_factory=list,
            metadata={
                "name": "Argument",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Argument:
            ref_id: str = field(
                metadata={
                    "name": "RefId",
                    "type": "Attribute",
                }
            )
            value: str = field(
                metadata={
                    "name": "Value",
                    "type": "Attribute",
                }
            )


class NodeTType(Enum):
    FOLDER = "Folder"
    CHANNEL = "Channel"


class OptionsCustomerAdjustableParameters(Enum):
    WRITE = "Write"
    SYNC = "Sync"


class OptionsNotLoadable(Enum):
    SKIP_SILENTLY = "SkipSilently"
    DISPLAY_ERROR = "DisplayError"


class OptionsParameterByteOrder(Enum):
    BIG_ENDIAN = "BigEndian"
    LITTLE_ENDIAN = "LittleEndian"


class OptionsTextParameterEncodingSelector(Enum):
    USE_WINDOWS_ANSI_CODE_PAGE = "UseWindowsAnsiCodePage"
    USE_PROJECT_CODE_PAGE = "UseProjectCodePage"
    USE_TEXT_PARAMETER_ENCODING_CODE_PAGE = "UseTextParameterEncodingCodePage"


@dataclass(slots=True, kw_only=True)
class P2PlinkEndpointT:
    class Meta:
        name = "P2PLinkEndpoint_t"

    device_ref_id: str = field(
        metadata={
            "name": "DeviceRefId",
            "type": "Attribute",
        }
    )


class ParameterBlockLayoutT(Enum):
    TABLE = "Table"
    GRID = "Grid"
    LIST = "List"


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
    grant_use_by_customer: bool = field(
        default=False,
        metadata={
            "name": "GrantUseByCustomer",
            "type": "Attribute",
        },
    )
    customized_text: None | str = field(
        default=None,
        metadata={
            "name": "CustomizedText",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterRefRefT:
    """
    :ivar ref_id: registration-relevant
    :ivar help_context:
    :ivar indent_level:
    :ivar internal_description:
    :ivar cell:
    :ivar icon:
    """

    class Meta:
        name = "ParameterRefRef_t"

    ref_id: str = field(
        metadata={
            "name": "RefId",
            "type": "Attribute",
        }
    )
    help_context: None | str = field(
        default=None,
        metadata={
            "name": "HelpContext",
            "type": "Attribute",
        },
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
    cell: None | str = field(
        default=None,
        metadata={
            "name": "Cell",
            "type": "Attribute",
            "pattern": r"\d+,\d+",
        },
    )
    icon: None | str = field(
        default=None,
        metadata={
            "name": "Icon",
            "type": "Attribute",
        },
    )


class ParameterSeparatorTUihint(Enum):
    HORIZONTAL_RULER = "HorizontalRuler"
    HEADLINE = "Headline"
    INFORMATION = "Information"
    ERROR = "Error"


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


class ProjectTypeT(Enum):
    APARTMENT = "Apartment"
    FAMILY_HOUSE = "Family House"
    VILLA = "Villa"
    OTHER_RESIDENTIAL = "Other (Residential)"
    HOTEL = "Hotel"
    AIRPORT = "Airport"
    OFFICE_BUILDING = "Office Building"
    EDUCATIONAL = "Educational"
    LEISURE = "Leisure"
    ENTERTAINMENT = "Entertainment"
    PUBLIC_BUILDING = "Public Building"
    HEALTH_CARE = "Health Care"
    OTHER_COMMERCIAL = "Other (Commercial)"
    MANUFACTURER = "Manufacturer"
    CITY_PROJECT = "City Project"
    TRANSPORTATION = "Transportation"
    OTHER_OTHER = "Other (Other)"


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


@dataclass(slots=True, kw_only=True)
class PropertyParameterT:
    """
    :ivar object_index: registration-relevant
    :ivar object_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar property_id: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        name = "PropertyParameter_t"

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
class PropertyUnionT:
    """
    :ivar object_index: registration-relevant
    :ivar object_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar property_id: registration-relevant
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    """

    class Meta:
        name = "PropertyUnion_t"

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


class RfrxCapabilitiesT(Enum):
    READY = "Ready"
    READY_FAST = "ReadyFast"
    SLOW = "Slow"


class RftxCapabilitiesT(Enum):
    READY = "Ready"
    READY_FAST_SLOW = "ReadyFastSlow"


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
            "max_length": 255,
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


class SecurityModeT(Enum):
    AUTO = "Auto"
    ON = "On"
    OFF = "Off"


@dataclass(slots=True, kw_only=True)
class SegmentBaseT:
    """
    :ivar data: registration-relevant
    :ivar mask: registration-relevant
    :ivar id: registration-relevant
    :ivar name:
    :ivar size: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "SegmentBase_t"

    data: None | bytes = field(
        default=None,
        metadata={
            "name": "Data",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "format": "base64",
        },
    )
    mask: None | bytes = field(
        default=None,
        metadata={
            "name": "Mask",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
            "max_length": 255,
        },
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


class SpaceTypeT(Enum):
    BUILDING = "Building"
    BUILDING_PART = "BuildingPart"
    FLOOR = "Floor"
    ROOM = "Room"
    DISTRIBUTION_BOARD = "DistributionBoard"
    STAIRWAY = "Stairway"
    CORRIDOR = "Corridor"
    AREA = "Area"
    GROUND = "Ground"
    SEGMENT = "Segment"


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


class TextAlignmentT(Enum):
    LEFT = "Left"
    CENTER = "Center"
    RIGHT = "Right"


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
    RGBW = "RGBW"


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
    PROGRESS_BAR = "ProgressBar"


class TypeRestrictionBase(Enum):
    VALUE = "Value"
    BINARY_VALUE = "BinaryValue"


class TypeRestrictionUihint(Enum):
    TEXT = "Text"
    DROP_DOWN = "DropDown"
    BUTTONS = "Buttons"
    SEGMENTED = "Segmented"


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
class ButtonT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar text_parameter_ref_id:
    :ivar internal_description:
    :ivar cell:
    :ivar icon:
    :ivar event_handler: registration-relevant
    :ivar event_handler_parameters: registration-relevant
    :ivar event_handler_online: registration-relevant
    """

    class Meta:
        name = "Button_t"

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
            "max_length": 255,
        },
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
    cell: None | str = field(
        default=None,
        metadata={
            "name": "Cell",
            "type": "Attribute",
            "pattern": r"\d+,\d+",
        },
    )
    icon: None | str = field(
        default=None,
        metadata={
            "name": "Icon",
            "type": "Attribute",
        },
    )
    event_handler: None | str = field(
        default=None,
        metadata={
            "name": "EventHandler",
            "type": "Attribute",
        },
    )
    event_handler_parameters: None | str = field(
        default=None,
        metadata={
            "name": "EventHandlerParameters",
            "type": "Attribute",
        },
    )
    event_handler_online: None | ButtonTEventHandlerOnline = field(
        default=None,
        metadata={
            "name": "EventHandlerOnline",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ComObjectInstanceRefT:
    class Meta:
        name = "ComObjectInstanceRef_t"

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
    channel_id: None | str = field(
        default=None,
        metadata={
            "name": "ChannelId",
            "type": "Attribute",
        },
    )
    links: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Links",
            "type": "Attribute",
            "tokens": True,
        },
    )
    acknowledges: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Acknowledges",
            "type": "Attribute",
            "tokens": True,
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
    :ivar roles:
    :ivar security_required: registration-relevant
    :ivar may_read: registration-relevant
    :ivar read_flag_locked: registration-relevant
    :ivar write_flag_locked: registration-relevant
    :ivar transmit_flag_locked: registration-relevant
    :ivar update_flag_locked: registration-relevant
    :ivar read_on_init_flag_locked: registration-relevant
    :ivar semantics:
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
            "max_length": 255,
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
    roles: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Roles",
            "type": "Attribute",
            "tokens": True,
        },
    )
    security_required: None | ComObjectSecurityRequirementsT = field(
        default=None,
        metadata={
            "name": "SecurityRequired",
            "type": "Attribute",
        },
    )
    may_read: None | bool = field(
        default=None,
        metadata={
            "name": "MayRead",
            "type": "Attribute",
        },
    )
    read_flag_locked: None | bool = field(
        default=None,
        metadata={
            "name": "ReadFlagLocked",
            "type": "Attribute",
        },
    )
    write_flag_locked: None | bool = field(
        default=None,
        metadata={
            "name": "WriteFlagLocked",
            "type": "Attribute",
        },
    )
    transmit_flag_locked: None | bool = field(
        default=None,
        metadata={
            "name": "TransmitFlagLocked",
            "type": "Attribute",
        },
    )
    update_flag_locked: None | bool = field(
        default=None,
        metadata={
            "name": "UpdateFlagLocked",
            "type": "Attribute",
        },
    )
    read_on_init_flag_locked: None | bool = field(
        default=None,
        metadata={
            "name": "ReadOnInitFlagLocked",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
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
    :ivar security_required: registration-relevant
    :ivar may_read: registration-relevant
    :ivar read_flag_locked: registration-relevant
    :ivar write_flag_locked: registration-relevant
    :ivar transmit_flag_locked: registration-relevant
    :ivar update_flag_locked: registration-relevant
    :ivar read_on_init_flag_locked: registration-relevant
    :ivar io_tpoint_reference: registration-relevant
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
            "max_length": 255,
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
    security_required: ComObjectSecurityRequirementsT = field(
        default=ComObjectSecurityRequirementsT.NONE,
        metadata={
            "name": "SecurityRequired",
            "type": "Attribute",
        },
    )
    may_read: None | bool = field(
        default=None,
        metadata={
            "name": "MayRead",
            "type": "Attribute",
        },
    )
    read_flag_locked: bool = field(
        default=False,
        metadata={
            "name": "ReadFlagLocked",
            "type": "Attribute",
        },
    )
    write_flag_locked: bool = field(
        default=False,
        metadata={
            "name": "WriteFlagLocked",
            "type": "Attribute",
        },
    )
    transmit_flag_locked: bool = field(
        default=False,
        metadata={
            "name": "TransmitFlagLocked",
            "type": "Attribute",
        },
    )
    update_flag_locked: bool = field(
        default=False,
        metadata={
            "name": "UpdateFlagLocked",
            "type": "Attribute",
        },
    )
    read_on_init_flag_locked: bool = field(
        default=False,
        metadata={
            "name": "ReadOnInitFlagLocked",
            "type": "Attribute",
        },
    )
    io_tpoint_reference: None | str = field(
        default=None,
        metadata={
            "name": "IoTPointReference",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class DatapointRoleT:
    class Meta:
        name = "DatapointRole_t"

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
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
        },
    )
    status: DeprecationStatusT = field(
        default=DeprecationStatusT.ACTIVE,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class DatapointTypeT:
    class Meta:
        name = "DatapointType_t"

    datapoint_subtypes: None | DatapointTypeT.DatapointSubtypes = field(
        default=None,
        metadata={
            "name": "DatapointSubtypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    variable_length: bool = field(
        default=False,
        metadata={
            "name": "VariableLength",
            "type": "Attribute",
        },
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
        datapoint_subtype: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype] = field(
            default_factory=list,
            metadata={
                "name": "DatapointSubtype",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class DatapointSubtype:
            format: None | DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format = field(
                default=None,
                metadata={
                    "name": "Format",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
                bit: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.Bit] = field(
                    default_factory=list,
                    metadata={
                        "name": "Bit",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                unsigned_integer: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.UnsignedInteger] = (
                    field(
                        default_factory=list,
                        metadata={
                            "name": "UnsignedInteger",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/22",
                        },
                    )
                )
                signed_integer: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.SignedInteger] = field(
                    default_factory=list,
                    metadata={
                        "name": "SignedInteger",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                string: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.String] = field(
                    default_factory=list,
                    metadata={
                        "name": "String",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                float_value: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.Float] = field(
                    default_factory=list,
                    metadata={
                        "name": "Float",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                enumeration: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.Enumeration] = field(
                    default_factory=list,
                    metadata={
                        "name": "Enumeration",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                reserved: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.Reserved] = field(
                    default_factory=list,
                    metadata={
                        "name": "Reserved",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                ref_type: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.RefType] = field(
                    default_factory=list,
                    metadata={
                        "name": "RefType",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
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
                    offset: None | int = field(
                        default=None,
                        metadata={
                            "name": "Offset",
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
                    offset: None | int = field(
                        default=None,
                        metadata={
                            "name": "Offset",
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
                    variable_length: bool = field(
                        default=False,
                        metadata={
                            "name": "VariableLength",
                            "type": "Attribute",
                        },
                    )
                    null_terminated: bool = field(
                        default=False,
                        metadata={
                            "name": "NullTerminated",
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
                    offset: None | float = field(
                        default=None,
                        metadata={
                            "name": "Offset",
                            "type": "Attribute",
                        },
                    )

                @dataclass(slots=True, kw_only=True)
                class Enumeration:
                    enum_value: list[DatapointTypeT.DatapointSubtypes.DatapointSubtype.Format.Enumeration.EnumValue] = (
                        field(
                            default_factory=list,
                            metadata={
                                "name": "EnumValue",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/22",
                                "min_occurs": 1,
                            },
                        )
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
class FunctionTypeT:
    class Meta:
        name = "FunctionType_t"

    function_point: list[FunctionTypeT.FunctionPoint] = field(
        default_factory=list,
        metadata={
            "name": "FunctionPoint",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    status: DeprecationStatusT = field(
        default=DeprecationStatusT.ACTIVE,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class FunctionPoint:
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
        role: str = field(
            metadata={
                "name": "Role",
                "type": "Attribute",
            }
        )
        datapoint_type: str = field(
            metadata={
                "name": "DatapointType",
                "type": "Attribute",
            }
        )
        characteristics: list[str] = field(
            default_factory=list,
            metadata={
                "name": "Characteristics",
                "type": "Attribute",
                "tokens": True,
            },
        )
        semantics: None | str = field(
            default=None,
            metadata={
                "name": "Semantics",
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
            "namespace": "http://knx.org/xml/project/22",
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
    implements: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Implements",
            "type": "Attribute",
            "tokens": True,
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
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
            "type": "Attribute",
        },
    )


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
    datapoint_type: None | str = field(
        default=None,
        metadata={
            "name": "DatapointType",
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
    key: None | str = field(
        default=None,
        metadata={
            "name": "Key",
            "type": "Attribute",
            "max_length": 100,
        },
    )
    security: SecurityModeT = field(
        default=SecurityModeT.AUTO,
        metadata={
            "name": "Security",
            "type": "Attribute",
        },
    )
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
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
class LdCtrlBaseT:
    """
    :ivar on_error: registration-relevant set
    :ivar applies_to: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "LdCtrlBase_t"

    on_error: list[LdCtrlBaseT.OnError] = field(
        default_factory=list,
        metadata={
            "name": "OnError",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    class OnError:
        """
        :ivar cause: registration-relevant
        :ivar ignore: registration-relevant
        :ivar message_ref:
        """

        cause: LdCtrlErrorCauseT = field(
            metadata={
                "name": "Cause",
                "type": "Attribute",
            }
        )
        ignore: bool = field(
            default=False,
            metadata={
                "name": "Ignore",
                "type": "Attribute",
            },
        )
        message_ref: None | str = field(
            default=None,
            metadata={
                "name": "MessageRef",
                "type": "Attribute",
            },
        )


@dataclass(slots=True, kw_only=True)
class ModuleT:
    """
    :ivar numeric_arg:
    :ivar text_arg:
    :ivar id:
    :ivar ref_id: registration-relevant
    :ivar name:
    :ivar internal_description:
    """

    class Meta:
        name = "Module_t"

    numeric_arg: list[ModuleT.NumericArg] = field(
        default_factory=list,
        metadata={
            "name": "NumericArg",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    text_arg: list[ModuleT.TextArg] = field(
        default_factory=list,
        metadata={
            "name": "TextArg",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
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
            "max_length": 255,
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
    class NumericArg(ModuleArgT):
        """
        :ivar value: registration-relevant
        :ivar allocator_ref_id: registration-relevant
        :ivar base_value: registration-relevant
        """

        value: None | int = field(
            default=None,
            metadata={
                "name": "Value",
                "type": "Attribute",
            },
        )
        allocator_ref_id: None | str = field(
            default=None,
            metadata={
                "name": "AllocatorRefId",
                "type": "Attribute",
            },
        )
        base_value: None | str = field(
            default=None,
            metadata={
                "name": "BaseValue",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TextArg(ModuleArgT):
        id: str = field(
            metadata={
                "name": "Id",
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
class NodeT:
    class Meta:
        name = "Node_t"

    nodes: None | NodeT.Nodes = field(
        default=None,
        metadata={
            "name": "Nodes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_value: NodeTType = field(
        metadata={
            "name": "Type",
            "type": "Attribute",
        }
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
        },
    )
    group_object_instances: list[str] = field(
        default_factory=list,
        metadata={
            "name": "GroupObjectInstances",
            "type": "Attribute",
            "tokens": True,
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Nodes:
        node: list[NodeT] = field(
            default_factory=list,
            metadata={
                "name": "Node",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class P2PlinkBusInterfaceEndpointT(P2PlinkEndpointT):
    class Meta:
        name = "P2PLinkBusInterfaceEndpoint_t"

    bus_interface_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "BusInterfaceRefId",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class P2PlinkDeviceEndpointT(P2PlinkEndpointT):
    class Meta:
        name = "P2PLinkDeviceEndpoint_t"

    security_roles: list[str] = field(
        default_factory=list,
        metadata={
            "name": "SecurityRoles",
            "type": "Attribute",
            "tokens": True,
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterBaseT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar parameter_type: registration-relevant
    :ivar parameter_type_params:
    :ivar text:
    :ivar suffix_text:
    :ivar access:
    :ivar value: registration-relevant
    :ivar initial_value:
    :ivar customer_adjustable: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "ParameterBase_t"

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
    parameter_type: str = field(
        metadata={
            "name": "ParameterType",
            "type": "Attribute",
        }
    )
    parameter_type_params: list[str] = field(
        default_factory=list,
        metadata={
            "name": "ParameterTypeParams",
            "type": "Attribute",
            "tokens": True,
        },
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
    initial_value: None | str = field(
        default=None,
        metadata={
            "name": "InitialValue",
            "type": "Attribute",
        },
    )
    customer_adjustable: bool = field(
        default=False,
        metadata={
            "name": "CustomerAdjustable",
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
    :ivar rltransformation_func: registration-relevant
    :ivar rltransformation_parameters: registration-relevant
    :ivar lrtransformation_func: registration-relevant
    :ivar lrtransformation_parameters: registration-relevant
    """

    class Meta:
        name = "ParameterCalculation_t"

    rltransformation: None | str = field(
        default=None,
        metadata={
            "name": "RLTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    lrtransformation: None | str = field(
        default=None,
        metadata={
            "name": "LRTransformation",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    lparameters: ParameterCalculationT.Lparameters = field(
        metadata={
            "name": "LParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        }
    )
    rparameters: ParameterCalculationT.Rparameters = field(
        metadata={
            "name": "RParameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    rltransformation_func: None | str = field(
        default=None,
        metadata={
            "name": "RLTransformationFunc",
            "type": "Attribute",
        },
    )
    rltransformation_parameters: None | str = field(
        default=None,
        metadata={
            "name": "RLTransformationParameters",
            "type": "Attribute",
        },
    )
    lrtransformation_func: None | str = field(
        default=None,
        metadata={
            "name": "LRTransformationFunc",
            "type": "Attribute",
        },
    )
    lrtransformation_parameters: None | str = field(
        default=None,
        metadata={
            "name": "LRTransformationParameters",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Lparameters:
        """
        :ivar parameter_ref_ref: registration-relevant set
        """

        parameter_ref_ref: list[CalculationParameterRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Rparameters:
        """
        :ivar parameter_ref_ref: registration-relevant set
        """

        parameter_ref_ref: list[CalculationParameterRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
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
    :ivar initial_value:
    :ivar customer_adjustable: registration-relevant
    :ivar text_parameter_ref_id:
    :ivar internal_description:
    :ivar forbid_granting_use_by_customer:
    :ivar semantics:
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
            "max_length": 255,
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
    initial_value: None | str = field(
        default=None,
        metadata={
            "name": "InitialValue",
            "type": "Attribute",
        },
    )
    customer_adjustable: None | bool = field(
        default=None,
        metadata={
            "name": "CustomerAdjustable",
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
    forbid_granting_use_by_customer: bool = field(
        default=False,
        metadata={
            "name": "ForbidGrantingUseByCustomer",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ParameterSeparatorT:
    """
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar uihint:
    :ivar text_parameter_ref_id:
    :ivar internal_description:
    :ivar cell:
    :ivar icon:
    :ivar text_alignment:
    """

    class Meta:
        name = "ParameterSeparator_t"

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
            "max_length": 255,
        },
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
    uihint: None | ParameterSeparatorTUihint = field(
        default=None,
        metadata={
            "name": "UIHint",
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
    cell: None | str = field(
        default=None,
        metadata={
            "name": "Cell",
            "type": "Attribute",
            "pattern": r"\d+,\d+",
        },
    )
    icon: None | str = field(
        default=None,
        metadata={
            "name": "Icon",
            "type": "Attribute",
        },
    )
    text_alignment: None | TextAlignmentT = field(
        default=None,
        metadata={
            "name": "TextAlignment",
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
    :ivar type_raw_data:
    :ivar type_none:
    :ivar id: registration-relevant
    :ivar name: registration-relevant
    :ivar internal_description:
    :ivar plugin:
    :ivar validation_error_ref:
    :ivar text_alignment:
    :ivar io_tencoding: registration-relevant
    """

    class Meta:
        name = "ParameterType_t"

    type_number: None | ParameterTypeT.TypeNumber = field(
        default=None,
        metadata={
            "name": "TypeNumber",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_float: None | ParameterTypeT.TypeFloat = field(
        default=None,
        metadata={
            "name": "TypeFloat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_restriction: None | ParameterTypeT.TypeRestriction = field(
        default=None,
        metadata={
            "name": "TypeRestriction",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_text: None | ParameterTypeT.TypeText = field(
        default=None,
        metadata={
            "name": "TypeText",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_time: None | ParameterTypeT.TypeTime = field(
        default=None,
        metadata={
            "name": "TypeTime",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_date: None | ParameterTypeT.TypeDate = field(
        default=None,
        metadata={
            "name": "TypeDate",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_ipaddress: None | ParameterTypeT.TypeIpaddress = field(
        default=None,
        metadata={
            "name": "TypeIPAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_picture: None | ParameterTypeT.TypePicture = field(
        default=None,
        metadata={
            "name": "TypePicture",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_color: None | ParameterTypeT.TypeColor = field(
        default=None,
        metadata={
            "name": "TypeColor",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_raw_data: None | ParameterTypeT.TypeRawData = field(
        default=None,
        metadata={
            "name": "TypeRawData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    type_none: None | object = field(
        default=None,
        metadata={
            "name": "TypeNone",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    validation_error_ref: None | str = field(
        default=None,
        metadata={
            "name": "ValidationErrorRef",
            "type": "Attribute",
        },
    )
    text_alignment: None | TextAlignmentT = field(
        default=None,
        metadata={
            "name": "TextAlignment",
            "type": "Attribute",
        },
    )
    io_tencoding: None | str = field(
        default=None,
        metadata={
            "name": "IoTEncoding",
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
        :ivar increment: registration-relevant
        :ivar uihint:
        :ivar display_offset:
        :ivar display_factor:
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
        increment: int = field(
            default=1,
            metadata={
                "name": "Increment",
                "type": "Attribute",
            },
        )
        uihint: None | TypeNumberUihint = field(
            default=None,
            metadata={
                "name": "UIHint",
                "type": "Attribute",
            },
        )
        display_offset: None | float = field(
            default=None,
            metadata={
                "name": "DisplayOffset",
                "type": "Attribute",
            },
        )
        display_factor: None | float = field(
            default=None,
            metadata={
                "name": "DisplayFactor",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeFloat:
        """
        :ivar encoding: registration-relevant
        :ivar min_inclusive: registration-relevant
        :ivar max_inclusive: registration-relevant
        :ivar increment: registration-relevant
        :ivar uihint:
        :ivar display_format:
        :ivar display_offset:
        :ivar display_factor:
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
        increment: None | float = field(
            default=None,
            metadata={
                "name": "Increment",
                "type": "Attribute",
            },
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
        display_offset: None | float = field(
            default=None,
            metadata={
                "name": "DisplayOffset",
                "type": "Attribute",
            },
        )
        display_factor: None | float = field(
            default=None,
            metadata={
                "name": "DisplayFactor",
                "type": "Attribute",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class TypeRestriction:
        """
        :ivar enumeration: registration-relevant set
        :ivar base: registration-relevant
        :ivar size_in_bit: registration-relevant
        :ivar uihint:
        """

        enumeration: list[ParameterTypeT.TypeRestriction.Enumeration] = field(
            default_factory=list,
            metadata={
                "name": "Enumeration",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
        uihint: None | TypeRestrictionUihint = field(
            default=None,
            metadata={
                "name": "UIHint",
                "type": "Attribute",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Enumeration:
            """
            :ivar text:
            :ivar icon:
            :ivar picture_alignment:
            :ivar value: registration-relevant
            :ivar id: registration-relevant
            :ivar display_order:
            :ivar binary_value: registration-relevant
            """

            text: None | str = field(
                default=None,
                metadata={
                    "name": "Text",
                    "type": "Attribute",
                    "max_length": 255,
                },
            )
            icon: None | str = field(
                default=None,
                metadata={
                    "name": "Icon",
                    "type": "Attribute",
                },
            )
            picture_alignment: HorizontalAlignmentT = field(
                default=HorizontalAlignmentT.LEFT,
                metadata={
                    "name": "PictureAlignment",
                    "type": "Attribute",
                },
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
        horizontal_alignment: HorizontalAlignmentT = field(
            default=HorizontalAlignmentT.LEFT,
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
    class TypeRawData:
        """
        :ivar max_size: registration-relevant
        """

        max_size: int = field(
            metadata={
                "name": "MaxSize",
                "type": "Attribute",
                "min_inclusive": 1,
                "max_inclusive": 1048572,
            }
        )


@dataclass(slots=True, kw_only=True)
class ParameterValidationT:
    """
    :ivar parameters:
    :ivar id: registration-relevant
    :ivar name:
    :ivar internal_description:
    :ivar validation_func: registration-relevant
    :ivar validation_parameters: registration-relevant
    """

    class Meta:
        name = "ParameterValidation_t"

    parameters: ParameterValidationT.Parameters = field(
        metadata={
            "name": "Parameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        }
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    validation_func: str = field(
        metadata={
            "name": "ValidationFunc",
            "type": "Attribute",
        }
    )
    validation_parameters: None | str = field(
        default=None,
        metadata={
            "name": "ValidationParameters",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Parameters:
        """
        :ivar parameter_ref_ref: registration-relevant set
        """

        parameter_ref_ref: list[CalculationParameterRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
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
class SecurityT:
    class Meta:
        name = "Security_t"

    loaded_iprouting_backbone_key: None | str = field(
        default=None,
        metadata={
            "name": "LoadedIPRoutingBackboneKey",
            "type": "Attribute",
            "max_length": 100,
        },
    )
    device_authentication_code: None | str = field(
        default=None,
        metadata={
            "name": "DeviceAuthenticationCode",
            "type": "Attribute",
            "max_length": 20,
        },
    )
    device_authentication_code_hash: None | bytes = field(
        default=None,
        metadata={
            "name": "DeviceAuthenticationCodeHash",
            "type": "Attribute",
            "format": "base64",
        },
    )
    loaded_device_authentication_code_hash: None | bytes = field(
        default=None,
        metadata={
            "name": "LoadedDeviceAuthenticationCodeHash",
            "type": "Attribute",
            "format": "base64",
        },
    )
    device_management_password: None | str = field(
        default=None,
        metadata={
            "name": "DeviceManagementPassword",
            "type": "Attribute",
            "max_length": 20,
        },
    )
    device_management_password_hash: None | bytes = field(
        default=None,
        metadata={
            "name": "DeviceManagementPasswordHash",
            "type": "Attribute",
            "format": "base64",
        },
    )
    loaded_device_management_password_hash: None | bytes = field(
        default=None,
        metadata={
            "name": "LoadedDeviceManagementPasswordHash",
            "type": "Attribute",
            "format": "base64",
        },
    )
    tool_key: None | str = field(
        default=None,
        metadata={
            "name": "ToolKey",
            "type": "Attribute",
            "max_length": 100,
        },
    )
    loaded_tool_key: None | str = field(
        default=None,
        metadata={
            "name": "LoadedToolKey",
            "type": "Attribute",
            "max_length": 100,
        },
    )
    sequence_number: None | int = field(
        default=None,
        metadata={
            "name": "SequenceNumber",
            "type": "Attribute",
        },
    )
    sequence_number_timestamp: None | XmlDateTime = field(
        default=None,
        metadata={
            "name": "SequenceNumberTimestamp",
            "type": "Attribute",
        },
    )
    unicast_broadcast_blocking: SecurityModeT = field(
        default=SecurityModeT.AUTO,
        metadata={
            "name": "UnicastBroadcastBlocking",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class SpaceUsageT:
    class Meta:
        name = "SpaceUsage_t"

    space_usage: list[SpaceUsageT] = field(
        default_factory=list,
        metadata={
            "name": "SpaceUsage",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    relations: list[str] = field(
        default_factory=list,
        metadata={
            "name": "Relations",
            "type": "Attribute",
            "tokens": True,
        },
    )
    status: DeprecationStatusT = field(
        default=DeprecationStatusT.ACTIVE,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
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
            "namespace": "http://knx.org/xml/project/22",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
            "type": "Attribute",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_instance_refs: None | DeviceInstanceT.ComObjectInstanceRefs = field(
        default=None,
        metadata={
            "name": "ComObjectInstanceRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    channel_instances: None | DeviceInstanceT.ChannelInstances = field(
        default=None,
        metadata={
            "name": "ChannelInstances",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module_instances: None | DeviceInstanceT.ModuleInstances = field(
        default=None,
        metadata={
            "name": "ModuleInstances",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    group_object_tree: None | DeviceInstanceT.GroupObjectTree = field(
        default=None,
        metadata={
            "name": "GroupObjectTree",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    additional_addresses: None | DeviceInstanceT.AdditionalAddresses = field(
        default=None,
        metadata={
            "name": "AdditionalAddresses",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    binary_data: None | DeviceInstanceT.BinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    ipconfig: None | IpconfigT = field(
        default=None,
        metadata={
            "name": "IPConfig",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    security: None | SecurityT = field(
        default=None,
        metadata={
            "name": "Security",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    bus_interfaces: None | DeviceInstanceT.BusInterfaces = field(
        default=None,
        metadata={
            "name": "BusInterfaces",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    rf_fast_ack_slots: None | DeviceInstanceT.RfFastAckSlots = field(
        default=None,
        metadata={
            "name": "RfFastAckSlots",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    download_counter: None | int = field(
        default=None,
        metadata={
            "name": "DownloadCounter",
            "type": "Attribute",
        },
    )
    is_activity_calculated: None | bool = field(
        default=None,
        metadata={
            "name": "IsActivityCalculated",
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
    is_slow_resender: bool = field(
        default=False,
        metadata={
            "name": "IsSlowResender",
            "type": "Attribute",
        },
    )
    puid: int = field(
        metadata={
            "name": "Puid",
            "type": "Attribute",
        }
    )
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class ParameterInstanceRefs:
        parameter_instance_ref: list[ParameterInstanceRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterInstanceRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ChannelInstances:
        channel_instance: list[ChannelInstanceT] = field(
            default_factory=list,
            metadata={
                "name": "ChannelInstance",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ModuleInstances:
        module_instance: list[ModuleInstanceT] = field(
            default_factory=list,
            metadata={
                "name": "ModuleInstance",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class GroupObjectTree:
        nodes: None | DeviceInstanceT.GroupObjectTree.Nodes = field(
            default=None,
            metadata={
                "name": "Nodes",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        group_object_instances: list[str] = field(
            default_factory=list,
            metadata={
                "name": "GroupObjectInstances",
                "type": "Attribute",
                "tokens": True,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Nodes:
            node: list[NodeT] = field(
                default_factory=list,
                metadata={
                    "name": "Node",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
                "max_occurs": 254,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Address:
            address: None | int = field(
                default=None,
                metadata={
                    "name": "Address",
                    "type": "Attribute",
                    "min_inclusive": 1,
                    "max_inclusive": 255,
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
    class BinaryData:
        binary_data: list[DeviceInstanceT.BinaryData.BinaryDataInner] = field(
            default_factory=list,
            metadata={
                "name": "BinaryData",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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
                    "max_length": 255,
                },
            )
            do_not_copy: bool = field(
                default=False,
                metadata={
                    "name": "DoNotCopy",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class BusInterfaces:
        bus_interface: list[BusInterfaceT] = field(
            default_factory=list,
            metadata={
                "name": "BusInterface",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class RfFastAckSlots:
        slot: list[DeviceInstanceT.RfFastAckSlots.Slot] = field(
            default_factory=list,
            metadata={
                "name": "Slot",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Slot:
            group_address_ref_id: str = field(
                metadata={
                    "name": "GroupAddressRefId",
                    "type": "Attribute",
                }
            )
            number: int = field(
                metadata={
                    "name": "Number",
                    "type": "Attribute",
                    "max_inclusive": 63,
                }
            )


@dataclass(slots=True, kw_only=True)
class FunctionsGroupT:
    class Meta:
        name = "FunctionsGroup_t"

    functions_group: list[FunctionsGroupT] = field(
        default_factory=list,
        metadata={
            "name": "FunctionsGroup",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    function_type: list[FunctionTypeT] = field(
        default_factory=list,
        metadata={
            "name": "FunctionType",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    text: str = field(
        metadata={
            "name": "Text",
            "type": "Attribute",
            "max_length": 255,
        }
    )
    description: None | str = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Attribute",
            "max_length": 255,
        },
    )
    status: DeprecationStatusT = field(
        default=DeprecationStatusT.ACTIVE,
        metadata={
            "name": "Status",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
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
            "namespace": "http://knx.org/xml/project/22",
            "max_occurs": 65535,
        },
    )
    group_address: list[GroupAddressT] = field(
        default_factory=list,
        metadata={
            "name": "GroupAddress",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    security: SecurityModeT = field(
        default=SecurityModeT.AUTO,
        metadata={
            "name": "Security",
            "type": "Attribute",
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
    :ivar coupler_capabilities: registration-relevant
    :ivar rfrx_capabilities: registration-relevant
    :ivar rftx_capabilities: registration-relevant
    :ivar semantics:
    :ivar sleep_cycle_time_seconds: registration-relevant
    """

    class Meta:
        name = "Hardware2Program_t"

    application_program_ref: list[ApplicationProgramRefT] = field(
        default_factory=list,
        metadata={
            "name": "ApplicationProgramRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "max_occurs": 2,
        },
    )
    registration_info: None | RegistrationInfoT = field(
        default=None,
        metadata={
            "name": "RegistrationInfo",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    coupler_capabilities: list[CouplerCapabilityT] = field(
        default_factory=list,
        metadata={
            "name": "CouplerCapabilities",
            "type": "Attribute",
            "tokens": True,
        },
    )
    rfrx_capabilities: None | RfrxCapabilitiesT = field(
        default=None,
        metadata={
            "name": "RFRxCapabilities",
            "type": "Attribute",
        },
    )
    rftx_capabilities: None | RftxCapabilitiesT = field(
        default=None,
        metadata={
            "name": "RFTxCapabilities",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )
    sleep_cycle_time_seconds: None | int = field(
        default=None,
        metadata={
            "name": "SleepCycleTimeSeconds",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlAbsSegmentT(LdCtrlBaseT):
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
    """

    class Meta:
        name = "LdCtrlAbsSegment_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlClearCachedObjectTypesT(LdCtrlBaseT):
    class Meta:
        name = "LdCtrlClearCachedObjectTypes_t"


@dataclass(slots=True, kw_only=True)
class LdCtrlClearLcfilterTableT(LdCtrlBaseT):
    """
    :ivar use_function_prop: registration-relevant
    """

    class Meta:
        name = "LdCtrlClearLCFilterTable_t"

    use_function_prop: bool = field(
        default=False,
        metadata={
            "name": "UseFunctionProp",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlCompareBaseT(LdCtrlBaseT):
    """
    :ivar allow_cached_value: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar mask: registration-relevant
    :ivar range: registration-relevant
    :ivar invert: registration-relevant
    :ivar retry_interval: registration-relevant
    :ivar time_out: registration-relevant
    """

    class Meta:
        name = "LdCtrlCompareBase_t"

    allow_cached_value: bool = field(
        default=False,
        metadata={
            "name": "AllowCachedValue",
            "type": "Attribute",
        },
    )
    inline_data: None | bytes = field(
        default=None,
        metadata={
            "name": "InlineData",
            "type": "Attribute",
            "format": "base16",
        },
    )
    mask: None | bytes = field(
        default=None,
        metadata={
            "name": "Mask",
            "type": "Attribute",
            "format": "base16",
        },
    )
    range: None | str = field(
        default=None,
        metadata={
            "name": "Range",
            "type": "Attribute",
            "pattern": r"[\[\(](-?\d+)?,(-?\d+)?[\)\]][su]?",
        },
    )
    invert: bool = field(
        default=False,
        metadata={
            "name": "Invert",
            "type": "Attribute",
        },
    )
    retry_interval: int = field(
        default=0,
        metadata={
            "name": "RetryInterval",
            "type": "Attribute",
        },
    )
    time_out: int = field(
        default=0,
        metadata={
            "name": "TimeOut",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlConnectT(LdCtrlBaseT):
    class Meta:
        name = "LdCtrlConnect_t"


@dataclass(slots=True, kw_only=True)
class LdCtrlDeclarePropDescT(LdCtrlBaseT):
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
    """

    class Meta:
        name = "LdCtrlDeclarePropDesc_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlDelayT(LdCtrlBaseT):
    """
    :ivar milli_seconds: registration-relevant
    """

    class Meta:
        name = "LdCtrlDelay_t"

    milli_seconds: int = field(
        metadata={
            "name": "MilliSeconds",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlDisconnectT(LdCtrlBaseT):
    class Meta:
        name = "LdCtrlDisconnect_t"


@dataclass(slots=True, kw_only=True)
class LdCtrlInvokeFunctionPropT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar inline_data: registration-relevant
    """

    class Meta:
        name = "LdCtrlInvokeFunctionProp_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlLoadCompletedT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    """

    class Meta:
        name = "LdCtrlLoadCompleted_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlLoadImageMemT(LdCtrlBaseT):
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        name = "LdCtrlLoadImageMem_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlLoadImagePropT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar start_element: registration-relevant
    :ivar count: registration-relevant
    """

    class Meta:
        name = "LdCtrlLoadImageProp_t"

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
        },
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlLoadImageRelMemT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        name = "LdCtrlLoadImageRelMem_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlLoadT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    """

    class Meta:
        name = "LdCtrlLoad_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlMapErrorT(LdCtrlBaseT):
    """
    :ivar ld_ctrl_filter: registration-relevant
    :ivar original_error: registration-relevant
    :ivar mapped_error: registration-relevant
    """

    class Meta:
        name = "LdCtrlMapError_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlMasterResetT(LdCtrlBaseT):
    """
    :ivar erase_code: registration-relevant
    :ivar channel_number: registration-relevant
    """

    class Meta:
        name = "LdCtrlMasterReset_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlMaxLengthT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        name = "LdCtrlMaxLength_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlMergeT(LdCtrlBaseT):
    """
    :ivar merge_id: registration-relevant
    """

    class Meta:
        name = "LdCtrlMerge_t"

    merge_id: int = field(
        metadata={
            "name": "MergeId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlProgressTextT(LdCtrlBaseT):
    class Meta:
        name = "LdCtrlProgressText_t"

    text_id: None | int = field(
        default=None,
        metadata={
            "name": "TextId",
            "type": "Attribute",
        },
    )
    message_ref: None | str = field(
        default=None,
        metadata={
            "name": "MessageRef",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlReadFunctionPropT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    """

    class Meta:
        name = "LdCtrlReadFunctionProp_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlRelSegmentT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar size: registration-relevant
    :ivar mode: registration-relevant
    :ivar fill: registration-relevant
    """

    class Meta:
        name = "LdCtrlRelSegment_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlRestartT(LdCtrlBaseT):
    class Meta:
        name = "LdCtrlRestart_t"


@dataclass(slots=True, kw_only=True)
class LdCtrlSetControlVariableT(LdCtrlBaseT):
    """
    :ivar name: registration-relevant
    :ivar value: registration-relevant
    """

    class Meta:
        name = "LdCtrlSetControlVariable_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlTaskCtrl1T(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar address: registration-relevant
    :ivar count: registration-relevant
    """

    class Meta:
        name = "LdCtrlTaskCtrl1_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlTaskCtrl2T(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar callback: registration-relevant
    :ivar address: registration-relevant
    :ivar seg0: registration-relevant
    :ivar seg1: registration-relevant
    """

    class Meta:
        name = "LdCtrlTaskCtrl2_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlTaskPtrT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar init_ptr: registration-relevant
    :ivar save_ptr: registration-relevant
    :ivar serial_ptr: registration-relevant
    """

    class Meta:
        name = "LdCtrlTaskPtr_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlTaskSegmentT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar address: registration-relevant
    """

    class Meta:
        name = "LdCtrlTaskSegment_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlUnloadT(LdCtrlBaseT):
    """
    :ivar lsm_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    """

    class Meta:
        name = "LdCtrlUnload_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlWriteMemT(LdCtrlBaseT):
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    """

    class Meta:
        name = "LdCtrlWriteMem_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlWritePropT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar start_element: registration-relevant
    :ivar count: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    :ivar trim: registration-relevant
    """

    class Meta:
        name = "LdCtrlWriteProp_t"

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
        },
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
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
    trim: None | bool = field(
        default=None,
        metadata={
            "name": "Trim",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlWriteRelMemT(LdCtrlBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    :ivar verify: registration-relevant
    :ivar inline_data: registration-relevant
    """

    class Meta:
        name = "LdCtrlWriteRelMem_t"

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


@dataclass(slots=True, kw_only=True)
class P2PlinksT:
    class Meta:
        name = "P2PLinks_t"

    p2_plink: list[P2PlinksT.P2Plink] = field(
        default_factory=list,
        metadata={
            "name": "P2PLink",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "min_occurs": 1,
        },
    )

    @dataclass(slots=True, kw_only=True)
    class P2Plink:
        device_endpoint: list[P2PlinkDeviceEndpointT] = field(
            default_factory=list,
            metadata={
                "name": "DeviceEndpoint",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "max_occurs": 2,
                "sequence": 1,
            },
        )
        bus_interface_endpoint: list[P2PlinkBusInterfaceEndpointT] = field(
            default_factory=list,
            metadata={
                "name": "BusInterfaceEndpoint",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "max_occurs": 2,
                "sequence": 1,
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
                "max_length": 255,
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
        key: None | str = field(
            default=None,
            metadata={
                "name": "Key",
                "type": "Attribute",
                "max_length": 100,
            },
        )


@dataclass(slots=True, kw_only=True)
class RepeatT:
    """
    :ivar choose:
    :ivar module:
    :ivar repeat:
    :ivar id:
    :ivar name:
    :ivar internal_description:
    :ivar parameter_ref_id: registration-relevant
    :ivar count: registration-relevant
    """

    class Meta:
        name = "Repeat_t"

    choose: list[ComObjectParameterChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    parameter_ref_id: None | str = field(
        default=None,
        metadata={
            "name": "ParameterRefId",
            "type": "Attribute",
        },
    )
    count: int = field(
        default=0,
        metadata={
            "name": "Count",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class SpaceT:
    class Meta:
        name = "Space_t"

    space: list[SpaceT] = field(
        default_factory=list,
        metadata={
            "name": "Space",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    device_instance_ref: list[DeviceInstanceRefT] = field(
        default_factory=list,
        metadata={
            "name": "DeviceInstanceRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    function: list[FunctionT] = field(
        default_factory=list,
        metadata={
            "name": "Function",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    type_value: SpaceTypeT = field(
        metadata={
            "name": "Type",
            "type": "Attribute",
        }
    )
    usage: None | str = field(
        default=None,
        metadata={
            "name": "Usage",
            "type": "Attribute",
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
    context: None | str = field(
        default=None,
        metadata={
            "name": "Context",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )


@dataclass(slots=True, kw_only=True)
class UnionParameterT(ParameterBaseT):
    """
    :ivar offset: registration-relevant
    :ivar bit_offset: registration-relevant
    :ivar default_union_parameter: registration-relevant
    """

    class Meta:
        name = "UnionParameter_t"

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
    default_union_parameter: bool = field(
        default=False,
        metadata={
            "name": "DefaultUnionParameter",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramChannelT:
    """
    :ivar parameter_block:
    :ivar com_object_ref_ref:
    :ivar binary_data_ref:
    :ivar module:
    :ivar repeat:
    :ivar choose:
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar number: registration-relevant
    :ivar text_parameter_ref_id:
    :ivar internal_description:
    :ivar icon:
    :ivar help_context:
    :ivar semantics:
    :ivar is_semantic:
    """

    class Meta:
        name = "ApplicationProgramChannel_t"

    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_ref_ref: list[ComObjectRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    binary_data_ref: list[BinaryDataRefT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryDataRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    choose: list[ChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    icon: None | str = field(
        default=None,
        metadata={
            "name": "Icon",
            "type": "Attribute",
        },
    )
    help_context: None | str = field(
        default=None,
        metadata={
            "name": "HelpContext",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )
    is_semantic: None | bool = field(
        default=None,
        metadata={
            "name": "IsSemantic",
            "type": "Attribute",
        },
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
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        parameter_separator: list[ParameterSeparatorT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterSeparator",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        parameter_ref_ref: list[ParameterRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        button: list[ButtonT] = field(
            default_factory=list,
            metadata={
                "name": "Button",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        choose: list[ComObjectParameterChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        binary_data_ref: list[BinaryDataRefT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryDataRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        com_object_ref_ref: list[ComObjectRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        module: list[ModuleT] = field(
            default_factory=list,
            metadata={
                "name": "Module",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        repeat: list[RepeatT] = field(
            default_factory=list,
            metadata={
                "name": "Repeat",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        assign: list[AssignT] = field(
            default_factory=list,
            metadata={
                "name": "Assign",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )


@dataclass(slots=True, kw_only=True)
class GroupAddressesT:
    class Meta:
        name = "GroupAddresses_t"

    group_ranges: GroupAddressesT.GroupRanges = field(
        metadata={
            "name": "GroupRanges",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        }
    )

    @dataclass(slots=True, kw_only=True)
    class GroupRanges:
        group_range: list[GroupRangeT] = field(
            default_factory=list,
            metadata={
                "name": "GroupRange",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "max_occurs": 65535,
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
    :ivar tp256:
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
    :ivar original_manufacturer: registration-relevant
    :ivar no_download_without_plugin:
    :ivar non_reg_relevant_data_version:
    :ivar internal_description:
    :ivar semantics:
    """

    class Meta:
        name = "Hardware_t"

    products: None | HardwareT.Products = field(
        default=None,
        metadata={
            "name": "Products",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    hardware2_programs: None | HardwareT.Hardware2Programs = field(
        default=None,
        metadata={
            "name": "Hardware2Programs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    tp256: None | bool = field(
        default=None,
        metadata={
            "name": "Tp256",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
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
                "namespace": "http://knx.org/xml/project/22",
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
            :ivar semantics:
            """

            baggages: None | HardwareT.Products.Product.Baggages = field(
                default=None,
                metadata={
                    "name": "Baggages",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            attributes: None | HardwareT.Products.Product.Attributes = field(
                default=None,
                metadata={
                    "name": "Attributes",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            registration_info: None | RegistrationInfoT = field(
                default=None,
                metadata={
                    "name": "RegistrationInfo",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            semantics: None | str = field(
                default=None,
                metadata={
                    "name": "Semantics",
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
                        "namespace": "http://knx.org/xml/project/22",
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
                        "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class LdCtrlCompareMemT(LdCtrlCompareBaseT):
    """
    :ivar address_space: registration-relevant
    :ivar address: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        name = "LdCtrlCompareMem_t"

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


@dataclass(slots=True, kw_only=True)
class LdCtrlComparePropT(LdCtrlCompareBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar prop_id: registration-relevant
    :ivar start_element: registration-relevant
    :ivar count: registration-relevant
    """

    class Meta:
        name = "LdCtrlCompareProp_t"

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
        },
    )
    count: int = field(
        default=1,
        metadata={
            "name": "Count",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class LdCtrlCompareRelMemT(LdCtrlCompareBaseT):
    """
    :ivar obj_idx: registration-relevant
    :ivar obj_type: registration-relevant
    :ivar occurrence: registration-relevant
    :ivar offset: registration-relevant
    :ivar size: registration-relevant
    """

    class Meta:
        name = "LdCtrlCompareRelMem_t"

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


@dataclass(slots=True, kw_only=True)
class LocationsT:
    class Meta:
        name = "Locations_t"

    space: list[SpaceT] = field(
        default_factory=list,
        metadata={
            "name": "Space",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )


@dataclass(slots=True, kw_only=True)
class ModuleDefLdCtrlInvokeFunctionPropT(LdCtrlInvokeFunctionPropT):
    """
    :ivar base_obj_idx: registration-relevant
    :ivar base_occurrence: registration-relevant
    """

    class Meta:
        name = "ModuleDefLdCtrlInvokeFunctionProp_t"

    base_obj_idx: None | str = field(
        default=None,
        metadata={
            "name": "BaseObjIdx",
            "type": "Attribute",
        },
    )
    base_occurrence: None | str = field(
        default=None,
        metadata={
            "name": "BaseOccurrence",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ModuleDefLdCtrlReadFunctionPropT(LdCtrlReadFunctionPropT):
    """
    :ivar base_obj_idx: registration-relevant
    :ivar base_occurrence: registration-relevant
    """

    class Meta:
        name = "ModuleDefLdCtrlReadFunctionProp_t"

    base_obj_idx: None | str = field(
        default=None,
        metadata={
            "name": "BaseObjIdx",
            "type": "Attribute",
        },
    )
    base_occurrence: None | str = field(
        default=None,
        metadata={
            "name": "BaseOccurrence",
            "type": "Attribute",
        },
    )


@dataclass(slots=True, kw_only=True)
class ModuleDefLdCtrlWritePropT(LdCtrlWritePropT):
    """
    :ivar base_obj_idx: registration-relevant
    :ivar base_occurrence: registration-relevant
    :ivar base_start_element: registration-relevant
    """

    class Meta:
        name = "ModuleDefLdCtrlWriteProp_t"

    base_obj_idx: None | str = field(
        default=None,
        metadata={
            "name": "BaseObjIdx",
            "type": "Attribute",
        },
    )
    base_occurrence: None | str = field(
        default=None,
        metadata={
            "name": "BaseOccurrence",
            "type": "Attribute",
        },
    )
    base_start_element: None | str = field(
        default=None,
        metadata={
            "name": "BaseStartElement",
            "type": "Attribute",
        },
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
            "namespace": "http://knx.org/xml/project/22",
            "max_occurs": 16,
        },
    )
    unassigned_devices: None | TopologyT.UnassignedDevices = field(
        default=None,
        metadata={
            "name": "UnassignedDevices",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Area:
        line: list[TopologyT.Area.Line] = field(
            default_factory=list,
            metadata={
                "name": "Line",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "max_occurs": 16,
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
                "max_length": 255,
            },
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
            segment: list[TopologyT.Area.Line.Segment] = field(
                default_factory=list,
                metadata={
                    "name": "Segment",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                    "min_occurs": 1,
                    "max_occurs": 128,
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
                    "max_length": 255,
                },
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
            class Segment:
                device_instance: list[DeviceInstanceT] = field(
                    default_factory=list,
                    metadata={
                        "name": "DeviceInstance",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                bus_access: None | BusAccessT = field(
                    default=None,
                    metadata={
                        "name": "BusAccess",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                additional_group_addresses: None | TopologyT.Area.Line.Segment.AdditionalGroupAddresses = field(
                    default=None,
                    metadata={
                        "name": "AdditionalGroupAddresses",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
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
                        "max_length": 255,
                    },
                )
                number: int = field(
                    metadata={
                        "name": "Number",
                        "type": "Attribute",
                        "min_inclusive": 0,
                        "max_inclusive": 127,
                    }
                )
                medium_type_ref_id: str = field(
                    metadata={
                        "name": "MediumTypeRefId",
                        "type": "Attribute",
                    }
                )
                domain_address: None | int = field(
                    default=None,
                    metadata={
                        "name": "DomainAddress",
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
                    group_address: list[TopologyT.Area.Line.Segment.AdditionalGroupAddresses.GroupAddress] = field(
                        default_factory=list,
                        metadata={
                            "name": "GroupAddress",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ComObjectParameterBlockT:
    """
    :ivar rows:
    :ivar columns:
    :ivar parameter_block:
    :ivar parameter_separator:
    :ivar parameter_ref_ref:
    :ivar button:
    :ivar choose:
    :ivar binary_data_ref:
    :ivar com_object_ref_ref:
    :ivar module:
    :ivar repeat:
    :ivar assign:
    :ivar channel:
    :ivar id: registration-relevant
    :ivar name:
    :ivar text:
    :ivar access:
    :ivar help_topic:
    :ivar internal_description:
    :ivar param_ref_id: registration-relevant
    :ivar text_parameter_ref_id:
    :ivar inline:
    :ivar layout:
    :ivar cell:
    :ivar icon:
    :ivar help_context:
    :ivar show_in_com_object_tree:
    :ivar semantics:
    """

    class Meta:
        name = "ComObjectParameterBlock_t"

    rows: None | ComObjectParameterBlockT.Rows = field(
        default=None,
        metadata={
            "name": "Rows",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    columns: None | ComObjectParameterBlockT.Columns = field(
        default=None,
        metadata={
            "name": "Columns",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_separator: list[ParameterSeparatorT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterSeparator",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_ref_ref: list[ParameterRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    button: list[ButtonT] = field(
        default_factory=list,
        metadata={
            "name": "Button",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    choose: list[ComObjectParameterChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    binary_data_ref: list[BinaryDataRefT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryDataRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_ref_ref: list[ComObjectRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    assign: list[AssignT] = field(
        default_factory=list,
        metadata={
            "name": "Assign",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    channel: list[ApplicationProgramChannelT] = field(
        default_factory=list,
        metadata={
            "name": "Channel",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
            "max_length": 255,
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
    inline: bool = field(
        default=False,
        metadata={
            "name": "Inline",
            "type": "Attribute",
        },
    )
    layout: ParameterBlockLayoutT = field(
        default=ParameterBlockLayoutT.LIST,
        metadata={
            "name": "Layout",
            "type": "Attribute",
        },
    )
    cell: None | str = field(
        default=None,
        metadata={
            "name": "Cell",
            "type": "Attribute",
            "pattern": r"\d+,\d+",
        },
    )
    icon: None | str = field(
        default=None,
        metadata={
            "name": "Icon",
            "type": "Attribute",
        },
    )
    help_context: None | str = field(
        default=None,
        metadata={
            "name": "HelpContext",
            "type": "Attribute",
        },
    )
    show_in_com_object_tree: bool = field(
        default=False,
        metadata={
            "name": "ShowInComObjectTree",
            "type": "Attribute",
        },
    )
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Rows:
        row: list[ComObjectParameterBlockT.Rows.Row] = field(
            default_factory=list,
            metadata={
                "name": "Row",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Row:
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
                    "max_length": 255,
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
            text_parameter_ref_id: None | str = field(
                default=None,
                metadata={
                    "name": "TextParameterRefId",
                    "type": "Attribute",
                },
            )
            collapse_if_empty: bool = field(
                default=False,
                metadata={
                    "name": "CollapseIfEmpty",
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
    class Columns:
        column: list[ComObjectParameterBlockT.Columns.Column] = field(
            default_factory=list,
            metadata={
                "name": "Column",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Column:
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
                    "max_length": 255,
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
            text_parameter_ref_id: None | str = field(
                default=None,
                metadata={
                    "name": "TextParameterRefId",
                    "type": "Attribute",
                },
            )
            width: str = field(
                metadata={
                    "name": "Width",
                    "type": "Attribute",
                    "pattern": r"(100|\d\d|\d)%",
                }
            )
            text_alignment: None | TextAlignmentT = field(
                default=None,
                metadata={
                    "name": "TextAlignment",
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
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        choose: list[DependentChannelChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        module: list[ModuleT] = field(
            default_factory=list,
            metadata={
                "name": "Module",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        repeat: list[RepeatT] = field(
            default_factory=list,
            metadata={
                "name": "Repeat",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )


@dataclass(slots=True, kw_only=True)
class LdCtrlBaseChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "LdCtrlBaseChoose_t"

    when: list[LdCtrlBaseChooseT.When] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
        ld_ctrl_unload: list[LdCtrlUnloadT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlUnload",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_load: list[LdCtrlLoadT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlLoad",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_max_length: list[LdCtrlMaxLengthT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlMaxLength",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_clear_cached_object_types: list[LdCtrlClearCachedObjectTypesT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlClearCachedObjectTypes",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_load_completed: list[LdCtrlLoadCompletedT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlLoadCompleted",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_abs_segment: list[LdCtrlAbsSegmentT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlAbsSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_rel_segment: list[LdCtrlRelSegmentT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlRelSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_task_segment: list[LdCtrlTaskSegmentT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlTaskSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_task_ptr: list[LdCtrlTaskPtrT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlTaskPtr",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_task_ctrl1: list[LdCtrlTaskCtrl1T] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlTaskCtrl1",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_task_ctrl2: list[LdCtrlTaskCtrl2T] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlTaskCtrl2",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_write_prop: list[LdCtrlWritePropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlWriteProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_compare_prop: list[LdCtrlComparePropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlCompareProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_load_image_prop: list[LdCtrlLoadImagePropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlLoadImageProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_invoke_function_prop: list[LdCtrlInvokeFunctionPropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlInvokeFunctionProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_read_function_prop: list[LdCtrlReadFunctionPropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlReadFunctionProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_write_mem: list[LdCtrlWriteMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlWriteMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_compare_mem: list[LdCtrlCompareMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlCompareMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_load_image_mem: list[LdCtrlLoadImageMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlLoadImageMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_write_rel_mem: list[LdCtrlWriteRelMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlWriteRelMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_compare_rel_mem: list[LdCtrlCompareRelMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlCompareRelMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_load_image_rel_mem: list[LdCtrlLoadImageRelMemT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlLoadImageRelMem",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_connect: list[LdCtrlConnectT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlConnect",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_disconnect: list[LdCtrlDisconnectT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlDisconnect",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_restart: list[LdCtrlRestartT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlRestart",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_master_reset: list[LdCtrlMasterResetT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlMasterReset",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_delay: list[LdCtrlDelayT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlDelay",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_set_control_variable: list[LdCtrlSetControlVariableT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlSetControlVariable",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_map_error: list[LdCtrlMapErrorT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlMapError",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_progress_text: list[LdCtrlProgressTextT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlProgressText",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_declare_prop_desc: list[LdCtrlDeclarePropDescT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlDeclarePropDesc",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_clear_lcfilter_table: list[LdCtrlClearLcfilterTableT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlClearLCFilterTable",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_merge: list[LdCtrlMergeT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlMerge",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        choose: list[LdCtrlBaseChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ModuleDefLdCtrlComparePropT(LdCtrlComparePropT):
    """
    :ivar base_obj_idx: registration-relevant
    :ivar base_occurrence: registration-relevant
    :ivar base_start_element: registration-relevant
    """

    class Meta:
        name = "ModuleDefLdCtrlCompareProp_t"

    base_obj_idx: None | str = field(
        default=None,
        metadata={
            "name": "BaseObjIdx",
            "type": "Attribute",
        },
    )
    base_occurrence: None | str = field(
        default=None,
        metadata={
            "name": "BaseOccurrence",
            "type": "Attribute",
        },
    )
    base_start_element: None | str = field(
        default=None,
        metadata={
            "name": "BaseStartElement",
            "type": "Attribute",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    installations: None | ProjectT.Installations = field(
        default=None,
        metadata={
            "name": "Installations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    user_files: None | ProjectT.UserFiles = field(
        default=None,
        metadata={
            "name": "UserFiles",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    addin_data: None | ProjectT.AddinData = field(
        default=None,
        metadata={
            "name": "AddinData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
        tags: None | ProjectT.ProjectInformation.Tags = field(
            default=None,
            metadata={
                "name": "Tags",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        history_entries: None | ProjectT.ProjectInformation.HistoryEntries = field(
            default=None,
            metadata={
                "name": "HistoryEntries",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        to_do_items: None | ProjectT.ProjectInformation.ToDoItems = field(
            default=None,
            metadata={
                "name": "ToDoItems",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        project_traces: None | ProjectT.ProjectInformation.ProjectTraces = field(
            default=None,
            metadata={
                "name": "ProjectTraces",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        device_certificates: None | ProjectT.ProjectInformation.DeviceCertificates = field(
            default=None,
            metadata={
                "name": "DeviceCertificates",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
        archived_version: None | XmlDateTime = field(
            default=None,
            metadata={
                "name": "ArchivedVersion",
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
        project_type: ProjectTypeT = field(
            default=ProjectTypeT.OTHER_COMMERCIAL,
            metadata={
                "name": "ProjectType",
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
        security: SecurityModeT = field(
            default=SecurityModeT.AUTO,
            metadata={
                "name": "Security",
                "type": "Attribute",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Tags:
            tag: list[ProjectT.ProjectInformation.Tags.Tag] = field(
                default_factory=list,
                metadata={
                    "name": "Tag",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                    "min_occurs": 1,
                },
            )

            @dataclass(slots=True, kw_only=True)
            class Tag:
                text: str = field(
                    metadata={
                        "name": "Text",
                        "type": "Attribute",
                        "max_length": 20,
                    }
                )
                color: str = field(
                    metadata={
                        "name": "Color",
                        "type": "Attribute",
                        "length": 7,
                        "pattern": r"#[0-9A-F]{6}",
                    }
                )

        @dataclass(slots=True, kw_only=True)
        class HistoryEntries:
            history_entry: list[ProjectT.ProjectInformation.HistoryEntries.HistoryEntry] = field(
                default_factory=list,
                metadata={
                    "name": "HistoryEntry",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
                        "max_length": 255,
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
                    "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                    "min_occurs": 1,
                },
            )

        @dataclass(slots=True, kw_only=True)
        class DeviceCertificates:
            device_certificate: list[DeviceCertificateT] = field(
                default_factory=list,
                metadata={
                    "name": "DeviceCertificate",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                }
            )
            locations: LocationsT = field(
                metadata={
                    "name": "Locations",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                }
            )
            group_addresses: GroupAddressesT = field(
                metadata={
                    "name": "GroupAddresses",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                }
            )
            p2_plinks: None | P2PlinksT = field(
                default=None,
                metadata={
                    "name": "P2PLinks",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            trades: None | TradesT = field(
                default=None,
                metadata={
                    "name": "Trades",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            split_infos: None | SplitInfosT = field(
                default=None,
                metadata={
                    "name": "SplitInfos",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            iprouting_backbone_key: None | str = field(
                default=None,
                metadata={
                    "name": "IPRoutingBackboneKey",
                    "type": "Attribute",
                    "max_length": 100,
                },
            )
            iprouting_latency_tolerance: None | int = field(
                default=None,
                metadata={
                    "name": "IPRoutingLatencyTolerance",
                    "type": "Attribute",
                },
            )
            ipsync_latency_fraction: float = field(
                default=0.1,
                metadata={
                    "name": "IPSyncLatencyFraction",
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
            iprouting_backbone_security: SecurityModeT = field(
                default=SecurityModeT.AUTO,
                metadata={
                    "name": "IPRoutingBackboneSecurity",
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
            context: None | str = field(
                default=None,
                metadata={
                    "name": "Context",
                    "type": "Attribute",
                },
            )
            ipv6_installation_id: None | int = field(
                default=None,
                metadata={
                    "name": "Ipv6InstallationId",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class AddinData:
        addin_data: list[AddinDataT] = field(
            default_factory=list,
            metadata={
                "name": "AddinData",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        com_object_ref_ref: list[ComObjectRefRefT] = field(
            default_factory=list,
            metadata={
                "name": "ComObjectRefRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        binary_data_ref: list[BinaryDataRefT] = field(
            default_factory=list,
            metadata={
                "name": "BinaryDataRef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        module: list[ModuleT] = field(
            default_factory=list,
            metadata={
                "name": "Module",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        repeat: list[RepeatT] = field(
            default_factory=list,
            metadata={
                "name": "Repeat",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        choose: list[ChannelChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        rename: list[RenameT] = field(
            default_factory=list,
            metadata={
                "name": "Rename",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )


@dataclass(slots=True, kw_only=True)
class LoadProcedureT:
    class Meta:
        name = "LoadProcedure_t"

    ld_ctrl_unload: list[LdCtrlUnloadT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlUnload",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_load: list[LdCtrlLoadT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoad",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_max_length: list[LdCtrlMaxLengthT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMaxLength",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_clear_cached_object_types: list[LdCtrlClearCachedObjectTypesT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlClearCachedObjectTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_load_completed: list[LdCtrlLoadCompletedT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadCompleted",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_abs_segment: list[LdCtrlAbsSegmentT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlAbsSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_rel_segment: list[LdCtrlRelSegmentT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlRelSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_task_segment: list[LdCtrlTaskSegmentT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskSegment",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_task_ptr: list[LdCtrlTaskPtrT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskPtr",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_task_ctrl1: list[LdCtrlTaskCtrl1T] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskCtrl1",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_task_ctrl2: list[LdCtrlTaskCtrl2T] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlTaskCtrl2",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_write_prop: list[LdCtrlWritePropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_compare_prop: list[LdCtrlComparePropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_load_image_prop: list[LdCtrlLoadImagePropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_invoke_function_prop: list[LdCtrlInvokeFunctionPropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlInvokeFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_read_function_prop: list[LdCtrlReadFunctionPropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlReadFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_write_mem: list[LdCtrlWriteMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_compare_mem: list[LdCtrlCompareMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_load_image_mem: list[LdCtrlLoadImageMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_write_rel_mem: list[LdCtrlWriteRelMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_compare_rel_mem: list[LdCtrlCompareRelMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_load_image_rel_mem: list[LdCtrlLoadImageRelMemT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlLoadImageRelMem",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_connect: list[LdCtrlConnectT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlConnect",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_disconnect: list[LdCtrlDisconnectT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDisconnect",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_restart: list[LdCtrlRestartT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlRestart",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_master_reset: list[LdCtrlMasterResetT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMasterReset",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_delay: list[LdCtrlDelayT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDelay",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_set_control_variable: list[LdCtrlSetControlVariableT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlSetControlVariable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_map_error: list[LdCtrlMapErrorT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMapError",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_progress_text: list[LdCtrlProgressTextT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlProgressText",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_declare_prop_desc: list[LdCtrlDeclarePropDescT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDeclarePropDesc",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_clear_lcfilter_table: list[LdCtrlClearLcfilterTableT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlClearLCFilterTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_merge: list[LdCtrlMergeT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMerge",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    choose: list[LdCtrlBaseChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )


@dataclass(slots=True, kw_only=True)
class ModuleDefLdCtrlBaseChooseT:
    """
    :ivar when: registration-relevant list
    :ivar param_ref_id: registration-relevant
    :ivar internal_description:
    """

    class Meta:
        name = "ModuleDefLdCtrlBaseChoose_t"

    when: list[ModuleDefLdCtrlBaseChooseT.When] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
        ld_ctrl_write_prop: list[ModuleDefLdCtrlWritePropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlWriteProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_compare_prop: list[ModuleDefLdCtrlComparePropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlCompareProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_invoke_function_prop: list[ModuleDefLdCtrlInvokeFunctionPropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlInvokeFunctionProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_read_function_prop: list[ModuleDefLdCtrlReadFunctionPropT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlReadFunctionProp",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_delay: list[LdCtrlDelayT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlDelay",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_progress_text: list[LdCtrlProgressTextT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlProgressText",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_declare_prop_desc: list[LdCtrlDeclarePropDescT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlDeclarePropDesc",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        ld_ctrl_merge: list[LdCtrlMergeT] = field(
            default_factory=list,
            metadata={
                "name": "LdCtrlMerge",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )
        choose: list[LdCtrlBaseChooseT] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "sequence": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ChannelIndependentBlockT:
    class Meta:
        name = "ChannelIndependentBlock_t"

    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    choose: list[ChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    binary_data_ref: list[BinaryDataRefT] = field(
        default_factory=list,
        metadata={
            "name": "BinaryDataRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_ref_ref: list[ComObjectRefRefT] = field(
        default_factory=list,
        metadata={
            "name": "ComObjectRefRef",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    resources: None | HawkConfigurationDataT.Resources = field(
        default=None,
        metadata={
            "name": "Resources",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    procedures: None | HawkConfigurationDataT.Procedures = field(
        default=None,
        metadata={
            "name": "Procedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    memory_segments: None | HawkConfigurationDataT.MemorySegments = field(
        default=None,
        metadata={
            "name": "MemorySegments",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    interface_objects: None | HawkConfigurationDataT.InterfaceObjects = field(
        default=None,
        metadata={
            "name": "InterfaceObjects",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            img_location: None | ResourceLocationT = field(
                default=None,
                metadata={
                    "name": "ImgLocation",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            resource_type: HawkConfigurationDataT.Resources.Resource.ResourceType = field(
                metadata={
                    "name": "ResourceType",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                }
            )
            access_rights: HawkConfigurationDataT.Resources.Resource.AccessRights = field(
                metadata={
                    "name": "AccessRights",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            optional: bool = field(
                default=False,
                metadata={
                    "name": "Optional",
                    "type": "Attribute",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class MemorySegment:
            location: ResourceLocationT = field(
                metadata={
                    "name": "Location",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                }
            )
            access_rights: HawkConfigurationDataT.MemorySegments.MemorySegment.AccessRights = field(
                metadata={
                    "name": "AccessRights",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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
            "namespace": "http://knx.org/xml/project/22",
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
class ModuleDefLoadProcedureT:
    """
    :ivar ld_ctrl_write_prop:
    :ivar ld_ctrl_compare_prop:
    :ivar ld_ctrl_invoke_function_prop:
    :ivar ld_ctrl_read_function_prop:
    :ivar ld_ctrl_delay:
    :ivar ld_ctrl_progress_text:
    :ivar ld_ctrl_declare_prop_desc:
    :ivar ld_ctrl_merge:
    :ivar choose:
    :ivar merge_id: registration-relevant
    """

    class Meta:
        name = "ModuleDefLoadProcedure_t"

    ld_ctrl_write_prop: list[ModuleDefLdCtrlWritePropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlWriteProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_compare_prop: list[ModuleDefLdCtrlComparePropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlCompareProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_invoke_function_prop: list[ModuleDefLdCtrlInvokeFunctionPropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlInvokeFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_read_function_prop: list[ModuleDefLdCtrlReadFunctionPropT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlReadFunctionProp",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_delay: list[LdCtrlDelayT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDelay",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_progress_text: list[LdCtrlProgressTextT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlProgressText",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_declare_prop_desc: list[LdCtrlDeclarePropDescT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlDeclarePropDesc",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    ld_ctrl_merge: list[LdCtrlMergeT] = field(
        default_factory=list,
        metadata={
            "name": "LdCtrlMerge",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    choose: list[ModuleDefLdCtrlBaseChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "sequence": 1,
        },
    )
    merge_id: int = field(
        metadata={
            "name": "MergeId",
            "type": "Attribute",
        }
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramDynamicT:
    class Meta:
        name = "ApplicationProgramDynamic_t"

    channel_independent_block: list[ChannelIndependentBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ChannelIndependentBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    channel: list[ApplicationProgramChannelT] = field(
        default_factory=list,
        metadata={
            "name": "Channel",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    choose: list[DependentChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramStaticT:
    """
    :ivar code:
    :ivar parameter_types:
    :ivar parameters:
    :ivar parameter_refs:
    :ivar parameter_calculations:
    :ivar parameter_validations:
    :ivar com_object_table:
    :ivar com_object_refs:
    :ivar address_table:
    :ivar association_table:
    :ivar fixup_list:
    :ivar load_procedures:
    :ivar extension:
    :ivar binary_data:
    :ivar device_compare:
    :ivar messages:
    :ivar script: registration-relevant
    :ivar security_roles: registration-relevant set
    :ivar bus_interfaces: registration-relevant set
    :ivar allocators: registration-relevant set
    :ivar options:
    """

    class Meta:
        name = "ApplicationProgramStatic_t"

    code: None | ApplicationProgramStaticT.Code = field(
        default=None,
        metadata={
            "name": "Code",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_types: None | ApplicationProgramStaticT.ParameterTypes = field(
        default=None,
        metadata={
            "name": "ParameterTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameters: None | ApplicationProgramStaticT.Parameters = field(
        default=None,
        metadata={
            "name": "Parameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_refs: None | ApplicationProgramStaticT.ParameterRefs = field(
        default=None,
        metadata={
            "name": "ParameterRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_calculations: None | ApplicationProgramStaticT.ParameterCalculations = field(
        default=None,
        metadata={
            "name": "ParameterCalculations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_validations: None | ApplicationProgramStaticT.ParameterValidations = field(
        default=None,
        metadata={
            "name": "ParameterValidations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_table: None | ApplicationProgramStaticT.ComObjectTable = field(
        default=None,
        metadata={
            "name": "ComObjectTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_refs: None | ApplicationProgramStaticT.ComObjectRefs = field(
        default=None,
        metadata={
            "name": "ComObjectRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    address_table: None | ApplicationProgramStaticT.AddressTable = field(
        default=None,
        metadata={
            "name": "AddressTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    association_table: None | ApplicationProgramStaticT.AssociationTable = field(
        default=None,
        metadata={
            "name": "AssociationTable",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    fixup_list: None | ApplicationProgramStaticT.FixupList = field(
        default=None,
        metadata={
            "name": "FixupList",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    load_procedures: None | LoadProceduresT = field(
        default=None,
        metadata={
            "name": "LoadProcedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    extension: None | ApplicationProgramStaticT.Extension = field(
        default=None,
        metadata={
            "name": "Extension",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    binary_data: None | ApplicationProgramStaticT.BinaryData = field(
        default=None,
        metadata={
            "name": "BinaryData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    device_compare: None | ApplicationProgramStaticT.DeviceCompare = field(
        default=None,
        metadata={
            "name": "DeviceCompare",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    messages: None | ApplicationProgramStaticT.Messages = field(
        default=None,
        metadata={
            "name": "Messages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    script: None | str = field(
        default=None,
        metadata={
            "name": "Script",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    security_roles: None | ApplicationProgramStaticT.SecurityRoles = field(
        default=None,
        metadata={
            "name": "SecurityRoles",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    bus_interfaces: None | ApplicationProgramStaticT.BusInterfaces = field(
        default=None,
        metadata={
            "name": "BusInterfaces",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    allocators: None | ApplicationProgramStaticT.Allocators = field(
        default=None,
        metadata={
            "name": "Allocators",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    options: None | ApplicationProgramStaticT.Options = field(
        default=None,
        metadata={
            "name": "Options",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        relative_segment: list[ApplicationProgramStaticT.Code.RelativeSegment] = field(
            default_factory=list,
            metadata={
                "name": "RelativeSegment",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class AbsoluteSegment(SegmentBaseT):
            """
            :ivar memory_type:
            :ivar address: registration-relevant
            :ivar user_memory: registration-relevant
            """

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
            user_memory: bool = field(
                default=False,
                metadata={
                    "name": "UserMemory",
                    "type": "Attribute",
                },
            )

        @dataclass(slots=True, kw_only=True)
        class RelativeSegment(SegmentBaseT):
            """
            :ivar load_state_machine: registration-relevant
            :ivar offset: registration-relevant
            """

            load_state_machine: int = field(
                metadata={
                    "name": "LoadStateMachine",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Parameters:
        parameter: list[ApplicationProgramStaticT.Parameters.Parameter] = field(
            default_factory=list,
            metadata={
                "name": "Parameter",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        union: list[ApplicationProgramStaticT.Parameters.UnionType] = field(
            default_factory=list,
            metadata={
                "name": "Union",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Parameter(ParameterBaseT):
            """
            :ivar memory:
            :ivar property:
            :ivar io_tpoint:
            :ivar legacy_patch_always: registration-relevant
            """

            memory: None | MemoryParameterT = field(
                default=None,
                metadata={
                    "name": "Memory",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            property: None | PropertyParameterT = field(
                default=None,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            io_tpoint: None | IoTpointParameterT = field(
                default=None,
                metadata={
                    "name": "IoTPoint",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            legacy_patch_always: bool = field(
                default=False,
                metadata={
                    "name": "LegacyPatchAlways",
                    "type": "Attribute",
                },
            )

        @dataclass(slots=True, kw_only=True)
        class UnionType:
            """
            :ivar memory:
            :ivar property:
            :ivar parameter: registration-relevant set
            :ivar size_in_bit:
            :ivar internal_description:
            """

            memory: None | MemoryUnionT = field(
                default=None,
                metadata={
                    "name": "Memory",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            property: None | PropertyUnionT = field(
                default=None,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            parameter: list[UnionParameterT] = field(
                default_factory=list,
                metadata={
                    "name": "Parameter",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ParameterValidations:
        """
        :ivar parameter_validation: registration-relevant set
        """

        parameter_validation: list[ParameterValidationT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterValidation",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        exclude_property: list[ApplicationProgramStaticT.DeviceCompare.ExcludeProperty] = field(
            default_factory=list,
            metadata={
                "name": "ExcludeProperty",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
    class Messages:
        message: list[ApplicationProgramStaticT.Messages.Message] = field(
            default_factory=list,
            metadata={
                "name": "Message",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Message:
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
            internal_description: None | str = field(
                default=None,
                metadata={
                    "name": "InternalDescription",
                    "type": "Attribute",
                },
            )
            text: str = field(
                metadata={
                    "name": "Text",
                    "type": "Attribute",
                    "max_length": 255,
                }
            )

    @dataclass(slots=True, kw_only=True)
    class SecurityRoles:
        security_role: list[ApplicationProgramStaticT.SecurityRoles.SecurityRole] = field(
            default_factory=list,
            metadata={
                "name": "SecurityRole",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class SecurityRole:
            """
            :ivar id: registration-relevant
            :ivar text:
            :ivar mask: registration-relevant
            :ivar role_id:
            """

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
            mask: int = field(
                metadata={
                    "name": "Mask",
                    "type": "Attribute",
                }
            )
            role_id: None | int = field(
                default=None,
                metadata={
                    "name": "RoleID",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class BusInterfaces:
        bus_interface: list[ApplicationProgramStaticT.BusInterfaces.BusInterface] = field(
            default_factory=list,
            metadata={
                "name": "BusInterface",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class BusInterface:
            """
            :ivar id: registration-relevant
            :ivar address_index: registration-relevant
            :ivar access_type: registration-relevant
            :ivar text:
            """

            id: str = field(
                metadata={
                    "name": "Id",
                    "type": "Attribute",
                }
            )
            address_index: int = field(
                metadata={
                    "name": "AddressIndex",
                    "type": "Attribute",
                }
            )
            access_type: BusInterfaceAccessType = field(
                metadata={
                    "name": "AccessType",
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

    @dataclass(slots=True, kw_only=True)
    class Allocators:
        allocator: list[AllocatorT] = field(
            default_factory=list,
            metadata={
                "name": "Allocator",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
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
        :ivar max_routing_apdu_length: registration-relevant
        :ivar comparable:
        :ivar reconstructable:
        :ivar download_invisible_parameters:
        :ivar supports_extended_memory_services: registration-relevant
        :ivar supports_extended_property_services: registration-relevant
        :ivar supports_ip_system_broadcast: registration-relevant
        :ivar not_loadable: registration-relevant
        :ivar not_loadable_message_ref:
        :ivar customer_adjustable_parameters: registration-relevant
        :ivar master_reset_on_crcmismatch: registration-relevant
        :ivar prompt_before_full_download:
        :ivar legacy_patch_manufacturer_id_in_task_segment:
            registration-relevant
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
        max_routing_apdu_length: None | int = field(
            default=None,
            metadata={
                "name": "MaxRoutingApduLength",
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
        supports_extended_memory_services: bool = field(
            default=False,
            metadata={
                "name": "SupportsExtendedMemoryServices",
                "type": "Attribute",
            },
        )
        supports_extended_property_services: bool = field(
            default=False,
            metadata={
                "name": "SupportsExtendedPropertyServices",
                "type": "Attribute",
            },
        )
        supports_ip_system_broadcast: bool = field(
            default=False,
            metadata={
                "name": "SupportsIpSystemBroadcast",
                "type": "Attribute",
            },
        )
        not_loadable: None | OptionsNotLoadable = field(
            default=None,
            metadata={
                "name": "NotLoadable",
                "type": "Attribute",
            },
        )
        not_loadable_message_ref: None | str = field(
            default=None,
            metadata={
                "name": "NotLoadableMessageRef",
                "type": "Attribute",
            },
        )
        customer_adjustable_parameters: None | OptionsCustomerAdjustableParameters = field(
            default=None,
            metadata={
                "name": "CustomerAdjustableParameters",
                "type": "Attribute",
            },
        )
        master_reset_on_crcmismatch: bool = field(
            default=False,
            metadata={
                "name": "MasterResetOnCRCMismatch",
                "type": "Attribute",
            },
        )
        prompt_before_full_download: bool = field(
            default=False,
            metadata={
                "name": "PromptBeforeFullDownload",
                "type": "Attribute",
            },
        )
        legacy_patch_manufacturer_id_in_task_segment: bool = field(
            default=False,
            metadata={
                "name": "LegacyPatchManufacturerIdInTaskSegment",
                "type": "Attribute",
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    mask_entries: None | MaskVersionT.MaskEntries = field(
        default=None,
        metadata={
            "name": "MaskEntries",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    hawk_configuration_data: list[HawkConfigurationDataT] = field(
        default_factory=list,
        metadata={
            "name": "HawkConfigurationData",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
class ModuleDefDynamicT:
    class Meta:
        name = "ModuleDefDynamic_t"

    channel_independent_block: list[ChannelIndependentBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ChannelIndependentBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    channel: list[ApplicationProgramChannelT] = field(
        default_factory=list,
        metadata={
            "name": "Channel",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    choose: list[DependentChannelChooseT] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    module: list[ModuleT] = field(
        default_factory=list,
        metadata={
            "name": "Module",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    repeat: list[RepeatT] = field(
        default_factory=list,
        metadata={
            "name": "Repeat",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_block: list[ComObjectParameterBlockT] = field(
        default_factory=list,
        metadata={
            "name": "ParameterBlock",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )


@dataclass(slots=True, kw_only=True)
class ModuleDefLoadProceduresT:
    """
    :ivar load_procedure: registration-relevant set
    """

    class Meta:
        name = "ModuleDefLoadProcedures_t"

    load_procedure: list[ModuleDefLoadProcedureT] = field(
        default_factory=list,
        metadata={
            "name": "LoadProcedure",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
            "min_occurs": 1,
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
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    datapoint_roles: None | MasterDataT.DatapointRoles = field(
        default=None,
        metadata={
            "name": "DatapointRoles",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    interface_object_types: None | MasterDataT.InterfaceObjectTypes = field(
        default=None,
        metadata={
            "name": "InterfaceObjectTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    interface_object_properties: None | MasterDataT.InterfaceObjectProperties = field(
        default=None,
        metadata={
            "name": "InterfaceObjectProperties",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    property_data_types: None | MasterDataT.PropertyDataTypes = field(
        default=None,
        metadata={
            "name": "PropertyDataTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    medium_types: None | MasterDataT.MediumTypes = field(
        default=None,
        metadata={
            "name": "MediumTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    mask_versions: None | MasterDataT.MaskVersions = field(
        default=None,
        metadata={
            "name": "MaskVersions",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    functional_blocks: None | MasterDataT.FunctionalBlocks = field(
        default=None,
        metadata={
            "name": "FunctionalBlocks",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    product_languages: None | MasterDataT.ProductLanguages = field(
        default=None,
        metadata={
            "name": "ProductLanguages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    function_types: None | MasterDataT.FunctionTypes = field(
        default=None,
        metadata={
            "name": "FunctionTypes",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    space_usages: None | MasterDataT.SpaceUsages = field(
        default=None,
        metadata={
            "name": "SpaceUsages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    manufacturers: None | MasterDataT.Manufacturers = field(
        default=None,
        metadata={
            "name": "Manufacturers",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    languages: None | MasterDataT.Languages = field(
        default=None,
        metadata={
            "name": "Languages",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
        datapoint_type: list[DatapointTypeT] = field(
            default_factory=list,
            metadata={
                "name": "DatapointType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class DatapointRoles:
        datapoint_role: list[DatapointRoleT] = field(
            default_factory=list,
            metadata={
                "name": "DatapointRole",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class InterfaceObjectTypes:
        interface_object_type: list[MasterDataT.InterfaceObjectTypes.InterfaceObjectType] = field(
            default_factory=list,
            metadata={
                "name": "InterfaceObjectType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
            access_policy: None | str = field(
                default=None,
                metadata={
                    "name": "AccessPolicy",
                    "type": "Attribute",
                    "pattern": r"[0-3][0-9A-F]{2}/[0-3][0-9A-F]{2}",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class PropertyDataTypes:
        property_data_type: list[MasterDataT.PropertyDataTypes.PropertyDataType] = field(
            default_factory=list,
            metadata={
                "name": "PropertyDataType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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
                        "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
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
    class FunctionTypes:
        functions_group: list[FunctionsGroupT] = field(
            default_factory=list,
            metadata={
                "name": "FunctionsGroup",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        function_type: list[FunctionTypeT] = field(
            default_factory=list,
            metadata={
                "name": "FunctionType",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

    @dataclass(slots=True, kw_only=True)
    class SpaceUsages:
        space_usage: list[SpaceUsageT] = field(
            default_factory=list,
            metadata={
                "name": "SpaceUsage",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Manufacturers:
        manufacturer: list[MasterDataT.Manufacturers.Manufacturer] = field(
            default_factory=list,
            metadata={
                "name": "Manufacturer",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            public_keys: None | MasterDataT.Manufacturers.Manufacturer.PublicKeys = field(
                default=None,
                metadata={
                    "name": "PublicKeys",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            datapoint_types: None | MasterDataT.Manufacturers.Manufacturer.DatapointTypes = field(
                default=None,
                metadata={
                    "name": "DatapointTypes",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            datapoint_roles: None | MasterDataT.Manufacturers.Manufacturer.DatapointRoles = field(
                default=None,
                metadata={
                    "name": "DatapointRoles",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            function_types: None | MasterDataT.Manufacturers.Manufacturer.FunctionTypes = field(
                default=None,
                metadata={
                    "name": "FunctionTypes",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            space_usages: None | MasterDataT.Manufacturers.Manufacturer.SpaceUsages = field(
                default=None,
                metadata={
                    "name": "SpaceUsages",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            order_number_wildcard_character: None | str = field(
                default=None,
                metadata={
                    "name": "OrderNumberWildcardCharacter",
                    "type": "Attribute",
                    "length": 1,
                },
            )
            member_status: MemberStatusT = field(
                default=MemberStatusT.ACTIVE,
                metadata={
                    "name": "MemberStatus",
                    "type": "Attribute",
                },
            )

            @dataclass(slots=True, kw_only=True)
            class PublicKeys:
                public_key: list[MasterDataT.Manufacturers.Manufacturer.PublicKeys.PublicKey] = field(
                    default_factory=list,
                    metadata={
                        "name": "PublicKey",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                        "min_occurs": 1,
                    },
                )

                @dataclass(slots=True, kw_only=True)
                class PublicKey:
                    rsakey_value: MasterDataT.Manufacturers.Manufacturer.PublicKeys.PublicKey.RsakeyValue = field(
                        metadata={
                            "name": "RSAKeyValue",
                            "type": "Element",
                            "namespace": "http://knx.org/xml/project/22",
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
                    purpose: list[str] = field(
                        default_factory=list,
                        metadata={
                            "name": "Purpose",
                            "type": "Attribute",
                            "tokens": True,
                        },
                    )

                    @dataclass(slots=True, kw_only=True)
                    class RsakeyValue:
                        modulus: bytes = field(
                            metadata={
                                "name": "Modulus",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/22",
                                "format": "base64",
                            }
                        )
                        exponent: bytes = field(
                            metadata={
                                "name": "Exponent",
                                "type": "Element",
                                "namespace": "http://knx.org/xml/project/22",
                                "format": "base64",
                            }
                        )

            @dataclass(slots=True, kw_only=True)
            class DatapointTypes:
                datapoint_type: list[DatapointTypeT] = field(
                    default_factory=list,
                    metadata={
                        "name": "DatapointType",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                        "min_occurs": 1,
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class DatapointRoles:
                datapoint_role: list[DatapointRoleT] = field(
                    default_factory=list,
                    metadata={
                        "name": "DatapointRole",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                        "min_occurs": 1,
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class FunctionTypes:
                functions_group: list[FunctionsGroupT] = field(
                    default_factory=list,
                    metadata={
                        "name": "FunctionsGroup",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )
                function_type: list[FunctionTypeT] = field(
                    default_factory=list,
                    metadata={
                        "name": "FunctionType",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class SpaceUsages:
                space_usage: list[SpaceUsageT] = field(
                    default_factory=list,
                    metadata={
                        "name": "SpaceUsage",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ModuleDefStaticT:
    """
    :ivar parameters:
    :ivar parameter_refs:
    :ivar parameter_calculations:
    :ivar parameter_validations:
    :ivar com_objects:
    :ivar com_object_refs:
    :ivar load_procedures:
    :ivar allocators: registration-relevant set
    """

    class Meta:
        name = "ModuleDefStatic_t"

    parameters: None | ModuleDefStaticT.Parameters = field(
        default=None,
        metadata={
            "name": "Parameters",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_refs: None | ModuleDefStaticT.ParameterRefs = field(
        default=None,
        metadata={
            "name": "ParameterRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_calculations: None | ModuleDefStaticT.ParameterCalculations = field(
        default=None,
        metadata={
            "name": "ParameterCalculations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    parameter_validations: None | ModuleDefStaticT.ParameterValidations = field(
        default=None,
        metadata={
            "name": "ParameterValidations",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_objects: None | ModuleDefStaticT.ComObjects = field(
        default=None,
        metadata={
            "name": "ComObjects",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    com_object_refs: None | ModuleDefStaticT.ComObjectRefs = field(
        default=None,
        metadata={
            "name": "ComObjectRefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    load_procedures: None | ModuleDefLoadProceduresT = field(
        default=None,
        metadata={
            "name": "LoadProcedures",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    allocators: None | ModuleDefStaticT.Allocators = field(
        default=None,
        metadata={
            "name": "Allocators",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Parameters:
        parameter: list[ModuleDefStaticT.Parameters.Parameter] = field(
            default_factory=list,
            metadata={
                "name": "Parameter",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        union: list[ModuleDefStaticT.Parameters.UnionType] = field(
            default_factory=list,
            metadata={
                "name": "Union",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Parameter(ParameterBaseT):
            """
            :ivar memory:
            :ivar property:
            :ivar io_tpoint:
            :ivar base_value: registration-relevant
            """

            memory: None | ModuleDefStaticT.Parameters.Parameter.Memory = field(
                default=None,
                metadata={
                    "name": "Memory",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            property: None | ModuleDefStaticT.Parameters.Parameter.Property = field(
                default=None,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            io_tpoint: None | IoTpointParameterT = field(
                default=None,
                metadata={
                    "name": "IoTPoint",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            base_value: None | str = field(
                default=None,
                metadata={
                    "name": "BaseValue",
                    "type": "Attribute",
                },
            )

            @dataclass(slots=True, kw_only=True)
            class Memory(MemoryParameterT):
                """
                :ivar base_offset: registration-relevant
                """

                base_offset: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOffset",
                        "type": "Attribute",
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class Property(PropertyParameterT):
                """
                :ivar base_offset: registration-relevant
                :ivar base_index: registration-relevant
                :ivar base_occurrence: registration-relevant
                """

                base_offset: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOffset",
                        "type": "Attribute",
                    },
                )
                base_index: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseIndex",
                        "type": "Attribute",
                    },
                )
                base_occurrence: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOccurrence",
                        "type": "Attribute",
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

            memory: None | ModuleDefStaticT.Parameters.UnionType.Memory = field(
                default=None,
                metadata={
                    "name": "Memory",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            property: None | ModuleDefStaticT.Parameters.UnionType.Property = field(
                default=None,
                metadata={
                    "name": "Property",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
                },
            )
            parameter: list[UnionParameterT] = field(
                default_factory=list,
                metadata={
                    "name": "Parameter",
                    "type": "Element",
                    "namespace": "http://knx.org/xml/project/22",
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
            class Memory(MemoryUnionT):
                """
                :ivar base_offset: registration-relevant
                """

                base_offset: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOffset",
                        "type": "Attribute",
                    },
                )

            @dataclass(slots=True, kw_only=True)
            class Property(PropertyUnionT):
                """
                :ivar base_offset: registration-relevant
                :ivar base_index: registration-relevant
                :ivar base_occurrence: registration-relevant
                """

                base_offset: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOffset",
                        "type": "Attribute",
                    },
                )
                base_index: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseIndex",
                        "type": "Attribute",
                    },
                )
                base_occurrence: None | str = field(
                    default=None,
                    metadata={
                        "name": "BaseOccurrence",
                        "type": "Attribute",
                    },
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
                "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ParameterValidations:
        """
        :ivar parameter_validation: registration-relevant set
        """

        parameter_validation: list[ParameterValidationT] = field(
            default_factory=list,
            metadata={
                "name": "ParameterValidation",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class ComObjects:
        """
        :ivar com_object: registration-relevant set
        """

        com_object: list[ModuleDefStaticT.ComObjects.ComObject] = field(
            default_factory=list,
            metadata={
                "name": "ComObject",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )

        @dataclass(slots=True, kw_only=True)
        class ComObject(ComObjectT):
            """
            :ivar base_number: registration-relevant
            """

            base_number: None | str = field(
                default=None,
                metadata={
                    "name": "BaseNumber",
                    "type": "Attribute",
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
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

    @dataclass(slots=True, kw_only=True)
    class Allocators:
        allocator: list[AllocatorT] = field(
            default_factory=list,
            metadata={
                "name": "Allocator",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ModuleDefT:
    class Meta:
        name = "ModuleDef_t"

    arguments: None | ModuleDefT.Arguments = field(
        default=None,
        metadata={
            "name": "Arguments",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    static: ModuleDefStaticT = field(
        metadata={
            "name": "Static",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        }
    )
    sub_module_defs: None | ModuleDefT.SubModuleDefs = field(
        default=None,
        metadata={
            "name": "SubModuleDefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    dynamic: None | ModuleDefDynamicT = field(
        default=None,
        metadata={
            "name": "Dynamic",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    internal_description: None | str = field(
        default=None,
        metadata={
            "name": "InternalDescription",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class Arguments:
        argument: list[ModuleDefT.Arguments.Argument] = field(
            default_factory=list,
            metadata={
                "name": "Argument",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )

        @dataclass(slots=True, kw_only=True)
        class Argument:
            """
            :ivar id:
            :ivar name: registration-relevant
            :ivar type_value: registration-relevant
            :ivar internal_description:
            :ivar allocates: registration-relevant
            :ivar alignment: registration-relevant
            """

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
                    "pattern": r"[A-Za-z_][A-Za-z0-9_]*",
                }
            )
            type_value: ModuleDefArgTypeT = field(
                default=ModuleDefArgTypeT.NUMERIC,
                metadata={
                    "name": "Type",
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
            allocates: None | int = field(
                default=None,
                metadata={
                    "name": "Allocates",
                    "type": "Attribute",
                },
            )
            alignment: ArgumentAlignment = field(
                default=ArgumentAlignment.VALUE_1,
                metadata={
                    "name": "Alignment",
                    "type": "Attribute",
                },
            )

    @dataclass(slots=True, kw_only=True)
    class SubModuleDefs:
        """
        :ivar module_def: registration-relevant set
        """

        module_def: list[ModuleDefT] = field(
            default_factory=list,
            metadata={
                "name": "ModuleDef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
            },
        )


@dataclass(slots=True, kw_only=True)
class ApplicationProgramT:
    """
    :ivar static:
    :ivar module_defs:
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
    :ivar hardware_type: registration-relevant
    :ivar help_topic:
    :ivar help_file:
    :ivar context_help_file:
    :ivar icon_file:
    :ivar default_language:
    :ivar dynamic_table_management: registration-relevant
    :ivar linkable: registration-relevant
    :ivar is_secure_enabled: registration-relevant
    :ivar min_ets_version:
    :ivar original_manufacturer: registration-relevant
    :ivar pre_ets4_style: registration-relevant
    :ivar converted_from_pre_ets4_data: registration-relevant
    :ivar created_from_legacy_schema_version:
    :ivar ipconfig: registration-relevant
    :ivar additional_addresses_count: registration-relevant
    :ivar max_user_entries: registration-relevant
    :ivar max_tunneling_user_entries: registration-relevant
    :ivar max_security_individual_address_entries: registration-relevant
    :ivar max_security_group_key_table_entries: registration-relevant
    :ivar max_security_p2_pkey_table_entries: registration-relevant
    :ivar max_security_proxy_group_key_table_entries: registration-
        relevant
    :ivar non_reg_relevant_data_version:
    :ivar broken:
    :ivar download_info_incomplete:
    :ivar replaces_versions: registration-relevant
    :ivar hash:
    :ivar internal_description:
    :ivar semantics:
    """

    class Meta:
        name = "ApplicationProgram_t"

    static: ApplicationProgramStaticT = field(
        metadata={
            "name": "Static",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        }
    )
    module_defs: None | ApplicationProgramT.ModuleDefs = field(
        default=None,
        metadata={
            "name": "ModuleDefs",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
        },
    )
    dynamic: None | ApplicationProgramDynamicT = field(
        default=None,
        metadata={
            "name": "Dynamic",
            "type": "Element",
            "namespace": "http://knx.org/xml/project/22",
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
    hardware_type: None | bytes = field(
        default=None,
        metadata={
            "name": "HardwareType",
            "type": "Attribute",
            "format": "base64",
        },
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
        },
    )
    context_help_file: None | str = field(
        default=None,
        metadata={
            "name": "ContextHelpFile",
            "type": "Attribute",
        },
    )
    icon_file: None | str = field(
        default=None,
        metadata={
            "name": "IconFile",
            "type": "Attribute",
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
    is_secure_enabled: bool = field(
        default=False,
        metadata={
            "name": "IsSecureEnabled",
            "type": "Attribute",
        },
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
    max_user_entries: int = field(
        default=0,
        metadata={
            "name": "MaxUserEntries",
            "type": "Attribute",
        },
    )
    max_tunneling_user_entries: int = field(
        default=0,
        metadata={
            "name": "MaxTunnelingUserEntries",
            "type": "Attribute",
        },
    )
    max_security_individual_address_entries: int = field(
        default=0,
        metadata={
            "name": "MaxSecurityIndividualAddressEntries",
            "type": "Attribute",
        },
    )
    max_security_group_key_table_entries: int = field(
        default=0,
        metadata={
            "name": "MaxSecurityGroupKeyTableEntries",
            "type": "Attribute",
        },
    )
    max_security_p2_pkey_table_entries: int = field(
        default=0,
        metadata={
            "name": "MaxSecurityP2PKeyTableEntries",
            "type": "Attribute",
        },
    )
    max_security_proxy_group_key_table_entries: int = field(
        default=0,
        metadata={
            "name": "MaxSecurityProxyGroupKeyTableEntries",
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
    semantics: None | str = field(
        default=None,
        metadata={
            "name": "Semantics",
            "type": "Attribute",
        },
    )

    @dataclass(slots=True, kw_only=True)
    class ModuleDefs:
        """
        :ivar module_def: registration-relevant set
        """

        module_def: list[ModuleDefT] = field(
            default_factory=list,
            metadata={
                "name": "ModuleDef",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
                "min_occurs": 1,
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
            "namespace": "http://knx.org/xml/project/22",
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
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        application_programs: None | ManufacturerDataT.Manufacturer.ApplicationPrograms = field(
            default=None,
            metadata={
                "name": "ApplicationPrograms",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        baggages: None | ManufacturerDataT.Manufacturer.Baggages = field(
            default=None,
            metadata={
                "name": "Baggages",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        hardware: None | ManufacturerDataT.Manufacturer.Hardware = field(
            default=None,
            metadata={
                "name": "Hardware",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
            },
        )
        languages: None | ManufacturerDataT.Manufacturer.Languages = field(
            default=None,
            metadata={
                "name": "Languages",
                "type": "Element",
                "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                    "min_occurs": 1,
                },
            )

            @dataclass(slots=True, kw_only=True)
            class Baggage:
                file_info: ManufacturerDataT.Manufacturer.Baggages.Baggage.FileInfo = field(
                    metadata={
                        "name": "FileInfo",
                        "type": "Element",
                        "namespace": "http://knx.org/xml/project/22",
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
                guid: None | str = field(
                    default=None,
                    metadata={
                        "name": "Guid",
                        "type": "Attribute",
                        "pattern": r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
                    },
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
                    "namespace": "http://knx.org/xml/project/22",
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
                    "namespace": "http://knx.org/xml/project/22",
                    "min_occurs": 1,
                },
            )


@dataclass(slots=True, kw_only=True)
class Knx:
    class Meta:
        name = "KNX"
        namespace = "http://knx.org/xml/project/22"

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
