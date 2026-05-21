# KNX Product File Format (`.knxprod`)

A `.knxprod` file is a ZIP archive distributed by KNX device manufacturers. It contains the full definition of one or more devices: their hardware, firmware application programs, and ETS catalog entries.

Supported schema versions: **10, 11, 12, 13, 14, 20, 21, 22, 23** (namespace `http://knx.org/xml/project/{version}`).

Fields without a version annotation have been present since **v10**.

---

## Archive structure

```
knx_master.xml                   — version metadata; namespace determines schema version
M-XXXX/                          — one directory per manufacturer (hex ID, e.g. M-00FA)
  Catalog.xml                    — product catalog / ETS tree
  Hardware.xml                   — hardware and product definitions
  M-XXXX_A-<name>.xml            — one application XML per device program
  M-XXXX.signature               — optional archive signature
```

The manufacturer code `M-XXXX` is a four-hex-digit string that appears throughout cross-file references (e.g. `M-00FA`).

---

## Hardware.xml

Root structure:

```xml
<KNX>
  <ManufacturerData>
    <Manufacturer RefId="M-XXXX">
      <Hardware>
        <Hardware ...>
          <Products>
            <Product ... />
          </Products>
          <Hardware2Programs>
            <Hardware2Program ...>
              <ApplicationProgramRef RefId="..." />
            </Hardware2Program>
          </Hardware2Programs>
        </Hardware>
      </Hardware>
    </Manufacturer>
  </ManufacturerData>
</KNX>
```

### `<Hardware>` element

Represents a physical hardware variant. One file can contain multiple `<Hardware>` elements (e.g. different bus interface types of the same product family).

| Attribute | Since | Type | Req | Description |
|---|---|---|---|---|
| `Id` | v10 | string | yes | Unique identifier, referenced by `Hardware2Program` cross-links. |
| `Name` | v10 | string ≤255 | yes | Human-readable hardware name. |
| `SerialNumber` | v10 | string ≤50 | yes | Manufacturer's serial number for this hardware. |
| `VersionNumber` | v10 | int 0–32767 | yes | Hardware revision number. |
| `BusCurrent` | v10 | float | no | Current drawn from the KNX bus in milliamps. |
| `HasIndividualAddress` | v10 | bool | yes | Device occupies a KNX individual address on the bus. |
| `HasApplicationProgram` | v10 | bool | yes | Device has a downloadable application program (primary). |
| `HasApplicationProgram2` | v10 | bool | no | Device has a second application program slot. |
| `IsAccessory` | v10 | bool | no | Device is an accessory (not a standalone bus device). |
| `IsPowerSupply` | v10 | bool | no | Device supplies power to the KNX bus. |
| `IsChoke` | v10 | bool | no | Device is a bus choke (inductance). |
| `IsCoupler` | v10 | bool | no | Device is a KNX coupler (area/line). |
| `IsPowerLineRepeater` | v10 | bool | no | Device acts as a PL (powerline) repeater. |
| `IsPowerLineSignalFilter` | v10 | bool | no | Device is a PL signal filter. |
| `IsCable` | v10 | bool | no | Entry represents a cable accessory, not an active device. |
| `IsIPEnabled` | v10 | bool | no | Device supports KNXnet/IP. |
| `IsRFRetransmitter` | v12 | bool | no | Device retransmits RF telegrams. |
| `OriginalManufacturer` | v10 | string | no | Manufacturer ID if this hardware is an OEM copy of another manufacturer's product. |
| `Tp256` | v20 | bool | no | Device supports TP 256 addressing mode. |
| `NoDownloadWithoutPlugin` | v10 | bool | no | ETS must not download this device without a vendor plugin. |
| `NonRegRelevantDataVersion` | v10 | int | no | Internal version counter for non-registration data. |
| `InternalDescription` | v12 | string | no | Free-text note for manufacturer tooling; not shown in ETS. |
| `Semantics` | v21 | string | no | Semantic classification for tooling. |

**Removed attributes:**

| Attribute | Versions | Description |
|---|---|---|
| `RFDeviceMode` | v12–v19 | RF device operating mode. |
| `RuntimeUnidirectional` | v12–v19 | Device operates in unidirectional RF mode at runtime. |
| `RFRxCapabilities` | v20 only | RF receive capability flags. Moved to `<Hardware2Program>` in v21. |
| `RFTxCapabilities` | v20 only | RF transmit capability flags. Moved to `<Hardware2Program>` in v21. |

Child elements:

- `<Products>` — contains one or more `<Product>` elements (orderable variants of this hardware)
- `<Hardware2Programs>` — contains one or more `<Hardware2Program>` elements (links to application programs)

---

### `<Product>` element

Represents a single orderable product SKU within a hardware definition.

| Attribute | Since | Type | Req | Description |
|---|---|---|---|---|
| `Id` | v10 | string | yes | Unique identifier; referenced from `Catalog.xml` via `ProductRefId`. |
| `Text` | v10 | string ≤255 | yes | Display name in the ETS catalog. |
| `OrderNumber` | v10 | string ≤50 | yes | Manufacturer's ordering number (e.g. `2CDG110187R0011`). |
| `IsRailMounted` | v10 | bool | yes | Device mounts on a DIN rail. |
| `WidthInMillimeter` | v10 | float | no | Physical width in millimeters (used for DIN rail space calculation). |
| `VisibleDescription` | v10 | string | no | Short description shown in ETS catalog. |
| `DefaultLanguage` | v10 | string | no | BCP-47 language tag for default display text. |
| `NonRegRelevantDataVersion` | v10 | int | no | Internal version counter. |
| `Hash` | v10 | base64 | no | Content hash for integrity checking. |
| `InternalDescription` | v12 | string | no | Manufacturer-internal note. |

Child elements:

- `<Baggages>` — list of `<Baggage RefId="...">` pointing to external resource files (PDF datasheets, images, etc.)
- `<Attributes>` — list of `<Attribute Name="..." Value="...">` for ETS display attributes (e.g. colour, certification marks). Attribute names are drawn from a fixed enum (`DeviceBusVoltage`, `DevicePeiType`, `HardwareType`, etc.)

---

### `<Hardware2Program>` element

Links a hardware variant to one or two application programs and specifies the supported bus media.

| Attribute | Since | Type | Req | Description |
|---|---|---|---|---|
| `Id` | v10 | string | yes | Unique identifier; referenced from `Catalog.xml` via `Hardware2ProgramRefId`. |
| `MediumTypes` | v10 | token list | no | Space-separated KNX medium types this combination supports: `TP` (twisted pair), `PL110` (powerline), `RF` (radio frequency), `IP`. |
| `Hash` | v10 | base64 | no | Content hash. |
| `CheckSums` | v11 | base64 | no | Additional checksums for the linked application program data. |
| `LoadedImage` | v11 | base64 | no | Pre-built firmware image embedded directly in the archive. |
| `CouplerCapabilities` | v20 | token list | no | Coupler-specific capability flags. |
| `RFRxCapabilities` | v21 | enum | no | RF receive capability flags. Moved here from `<Hardware>` in v21. |
| `RFTxCapabilities` | v21 | enum | no | RF transmit capability flags. Moved here from `<Hardware>` in v21. |
| `Semantics` | v21 | string | no | Semantic classification for tooling. |
| `SleepCycleTimeSeconds` | v22 | int | no | Sleep cycle duration in seconds for RF battery-powered devices. |

Child elements: `<ApplicationProgramRef>`, `<RegistrationInfo>`.

---

### `<ApplicationProgramRef>` element

Links a `<Hardware2Program>` to one application program. Up to two may be present (primary + secondary slot).

| Attribute | Since | Description |
|---|---|---|
| `RefId` | v10 | Matches `ApplicationProgram/@Id` in the corresponding `M-XXXX_A-*.xml`. |

---

### `<RegistrationInfo>` element

KNX registration/certification metadata attached to a `<Hardware2Program>`. Only present on products that have been officially registered with the KNX Association.

| Attribute | Since | Description |
|---|---|---|
| `RegistrationStatus` | v10 | Certification status: `Certified`, `Registered`, `InProgress`, or `Unknown`. |
| `RegistrationNumber` | v10 | KNX-assigned registration number in the form `YYYY/NNN`. |
| `OriginalRegistrationNumber` | v10 | Registration number of the product this was derived from (OEM / white-label case). |
| `RegistrationDate` | v10 | ISO date on which registration was granted. |
| `RegistrationSignature` | v10 | Base64-encoded cryptographic signature issued by the KNX Association. |
| `RegistrationKey` | v10 | Key type used for the signature (default `KnxConv`). |

---

## Application XML (`M-XXXX_A-*.xml`)

One file per application program. The root element is `<KNX>` containing a `<ManufacturerData><Manufacturer><ApplicationPrograms><ApplicationProgram>` hierarchy.

### `<ApplicationProgram>` element

Top-level descriptor of a device firmware application.

| Attribute | Since | Type | Req | Description |
|---|---|---|---|---|
| `Id` | v10 | string | yes | Unique ID, format `M-XXXX_A-<name>`. Matched by `Hardware2Program/ApplicationProgramRef/@RefId`. |
| `Name` | v10 | string | yes | Human-readable application name. |
| `ApplicationNumber` | v10 | int | yes | KNX application number programmed into the device. |
| `ApplicationVersion` | v10 | int | yes | KNX application version. |
| `ProgramType` | v10 | enum | yes | `ApplicationProgram` or `SystemProgram`. |
| `MaskVersion` | v10 | string | yes | BCU mask version this application targets (e.g. `MV-57B0`). |
| `LoadProcedureStyle` | v10 | enum | yes | How ETS should load the application: `DefaultProcedure`, `MergeIntoProcedure`, `ProductionProcedure`, `SystemProcedure`. |
| `PeiType` | v10 | int | no | Required PEI (physical external interface) type, if any. |
| `DynamicTableManagement` | v10 | bool | no | Application manages group object table dynamically. |
| `Linkable` | v10 | bool | no | Application supports linkable parameters. |
| `AdditionalAddressesCount` | v10 | int | no | Number of additional individual addresses required. |
| `DefaultLanguage` | v10 | string | no | BCP-47 language tag for default display text. |
| `MinEtsVersion` | v10 | string | no | Minimum ETS version required to program this device. |
| `VisibleDescription` | v10 | string | no | Free text shown in ETS. |
| `ReplacesVersions` | v10 | string | no | Comma-separated list of older `ApplicationVersion` values this replaces. |
| `OriginalManufacturer` | v10 | string | no | Manufacturer ID for OEM products. |
| `PreEts4Style` | v10 | bool | no | Legacy flag; application was authored for ETS 3 or earlier. |
| `ConvertedFromPreEts4Data` | v10 | bool | no | Set by ETS when an application was converted from a pre-ETS 4 project file. |
| `IPConfig` | v10 | enum | no | IP configuration method: `Auto`, `Bootstrap`, `Fixed`. |
| `HelpTopic` | v10 | int | no | ETS help topic ID for this application. |
| `HelpFile` | v10 | string | no | Path to a help file. Superseded by `ContextHelpFile` in v14; both may be present. |
| `NonRegRelevantDataVersion` | v10 | int | no | Internal version counter for non-registration data. |
| `Broken` | v10 | bool | no | Set by ETS when it detects the application data is inconsistent; not set by manufacturers. |
| `DownloadInfoIncomplete` | v10 | bool | no | Set by ETS when the download information is incomplete; not set by manufacturers. |
| `Hash` | v10 | base64 | no | Content hash. |
| `InternalDescription` | v12 | string | no | Manufacturer-internal note. |
| `CreatedFromLegacySchemaVersion` | v11 | bool | no | Set when the file was generated from a legacy (pre-v11) schema source. |
| `IsSecureEnabled` | v13 | bool | no | Application supports KNX Security. |
| `MaxUserEntries` | v13 | int | no | Maximum number of user entries (KNX Security). |
| `MaxTunnelingUserEntries` | v13 | int | no | Maximum tunneling user entries (KNX Security). |
| `MaxSecurityIndividualAddressEntries` | v13 | int | no | Maximum individual address security table entries. |
| `MaxSecurityGroupKeyTableEntries` | v13 | int | no | Maximum group key table entries. |
| `MaxSecurityP2PKeyTableEntries` | v13 | int | no | Maximum point-to-point key table entries. |
| `ContextHelpFile` | v14 | string | no | Path to a context-sensitive help file for ETS. Replaces `HelpFile`. |
| `IconFile` | v14 | string | no | Path to an icon file shown in ETS. |
| `Semantics` | v20 | string | no | Semantic classification for tooling. |
| `MaxSecurityProxyGroupKeyTableEntries` | v20 | int | no | Maximum proxy group key table entries (KNX Security). |
| `HardwareType` | v21 | string | no | Hardware type identifier. |
| `CloudConnect` | v23 | enum | no | Cloud connectivity mode. |
| `Profile` | v23 | string | no | Application profile for cloud/IoT integration. |

**Removed attributes:**

| Attribute | Versions | Description |
|---|---|---|
| `TunnelingAddressIndices` | v13 only | Space-separated list of address indices for KNX Security tunneling. Dropped without replacement in v14. |
| `MaxSecurityProxyIndividualAddressTableEntries` | v20 only | Maximum proxy individual address table entries (KNX Security). Dropped in v21. |

Child elements: `<Static>`, `<Dynamic>`, `<ModuleDefs>`.

---

### `<Static>` section

Contains all static (non-conditional) definitions.

#### `<ParameterTypes>`

Only present in `ApplicationProgram/Static` — module definitions do not define their own parameter types.

Each `<ParameterType Id="...">` holds exactly one of:

**`<TypeRestriction>`** — enumeration type

Contains one or more `<Enumeration>` children:

| Attribute | Since | Description |
|---|---|---|
| `Value` | v10 | The raw value stored in the parameter (always a string, typically an integer). |
| `Text` | v10 | Display label shown in ETS. |
| `Id` | v10 | Optional unique ID for this enum entry. |
| `DisplayOrder` | v10 | Optional integer controlling display order in ETS. |

**`<TypeNumber>`** — integer or checkbox type

| Attribute | Since | Description |
|---|---|---|
| `MinInclusive` | v10 | Minimum allowed value (integer). |
| `MaxInclusive` | v10 | Maximum allowed value (integer). |
| `SizeInBit` | v10 | Storage width in bits. |
| `UIHint` | v10 | If `"Checkbox"`, renders as a boolean toggle instead of a numeric input. |

**`<TypeText>`** — free-text string type

| Attribute | Since | Description |
|---|---|---|
| `SizeInBit` | v10 | Maximum string length in bits (divide by 8 for bytes). |

**`<TypeTime>`** — time duration type (seconds)

| Attribute | Since | Description |
|---|---|---|
| `MinInclusive` | v10 | Minimum value in seconds. |
| `MaxInclusive` | v10 | Maximum value in seconds. |

**`<TypePicture>`** *(since v11)* — binary image data (no user-editable attributes).

**`<TypeRawData>`** *(since v14)* — raw binary data (no user-editable attributes).

---

#### `<Parameters>`

Defines the base parameter definitions. Referenced via `<ParameterRefs>`.

Each `<Parameter>` (or `<Parameter>` inside a `<Union>`):

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique base definition ID. |
| `Name` | v10 | Internal parameter name (identifier-style, ≤50 chars, not shown in UI). |
| `Text` | v10 | Display label shown in ETS. |
| `Value` | v10 | Default value (always a string). |
| `ParameterType` | v10 | Reference to a `ParameterType/@Id` defined in `<ParameterTypes>`. |
| `Access` | v10 | ETS edit permission: `None`, `Read`, `ReadWrite` (default). |
| `SuffixText` | v11 | Unit label appended after the value in ETS (e.g. `"ms"`, `"°C"`). ≤20 chars. |
| `InternalDescription` | v12 | Manufacturer-internal note; not shown in ETS. |
| `InitialValue` | v14 | Factory-reset value, if different from `Value`. |
| `CustomerAdjustable` | v14 | When `true`, end-customers may adjust this parameter in ETS without full engineering access. |

Child elements:

- `<Memory CodeSegment="..." Offset="..." BitOffset="...">` — locates the parameter's storage in device memory (code segment reference, byte offset, bit offset within the byte).
- `<Property ObjIdx="..." PropId="...">` — alternative storage: the parameter maps to a KNX interface object property rather than a memory address.

`<Union>` groups parameters that share the same memory address (only one is active at a time based on conditions).

---

#### `<ParameterRefs>`

The usable instances of parameters, which can override base definitions.

Each `<ParameterRef>`:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ref ID; used by the `<Dynamic>` section. |
| `RefId` | v10 | Points to the base `<Parameter/@Id>`. |
| `Name` | v10 | Override of the base `Name` (optional). |
| `Text` | v10 | Override of the display label (optional). |
| `Value` | v10 | Override of the default value (optional). |
| `Access` | v10 | Override of edit permission (optional). |
| `DisplayOrder` | v10 | Integer controlling display order within its section. |
| `Tag` | v10 | Short tag string (≤50 chars) for tooling grouping. |
| `SuffixText` | v11 | Override of the unit label (optional). |
| `TextParameterRefId` | v12 | Reference to another `ParameterRef/@Id` whose current value is used as the display label at runtime, replacing `Text`. |
| `InternalDescription` | v12 | Manufacturer-internal note. |
| `InitialValue` | v14 | Override of factory-reset value. |
| `CustomerAdjustable` | v14 | Override of customer-adjustable flag. |
| `ForbidGrantingUseByCustomer` | v14 | When `true`, prevents a project engineer from granting customer-adjustable access to this parameter. |
| `Semantics` | v20 | Semantic classification for tooling. |

Resolution order: ref attributes take precedence over base attributes.

---

#### `<ParameterCalculations>`

Bidirectional value-transformation rules between pairs of parameters. Used when a physical value (e.g. raw timer ticks) must be converted to a human-readable form (e.g. seconds) for display in ETS, and back again when the user edits it.

Each `<ParameterCalculation>`:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique identifier. |
| `Name` | v10 | Internal name (≤50 chars). |
| `Language` | v10 | Script language: `VBScript` or `JavaScript`. |
| `InternalDescription` | v10 | Manufacturer-internal note. |
| `RLTransformationFunc` | v10 | Function name for the right-to-left transformation (raw device value → display value). |
| `RLTransformationParameters` | v10 | Extra arguments passed to `RLTransformationFunc`. |
| `LRTransformationFunc` | v10 | Function name for the left-to-right transformation (display value → raw device value). |
| `LRTransformationParameters` | v10 | Extra arguments passed to `LRTransformationFunc`. |

Child elements:
- `<LParameters>` — list of `<ParameterRefRef>` identifying the left-side (display) parameters.
- `<RParameters>` — list of `<ParameterRefRef>` identifying the right-side (raw) parameters.
- `<RLTransformation>` — optional inline script body for the RL direction (alternative to `RLTransformationFunc`).
- `<LRTransformation>` — optional inline script body for the LR direction.

---

#### `<Code>`

Firmware binary data embedded in the archive. Contains the actual memory image that ETS downloads to the device. Not needed for parameter or com-object parsing.

Child elements:

**`<AbsoluteSegment>`** — a code block placed at a fixed device memory address.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique identifier; referenced by `ComObjectTable/@CodeSegment`, `Parameter/Memory/@CodeSegment`, etc. |
| `Name` | v10 | Internal name (≤50 chars). |
| `Address` | v10 | Absolute memory address on the device (0–1 048 575). |
| `Size` | v10 | Size in bytes (0–1 048 575). |
| `MemoryType` | v10 | Memory type identifier (device-specific). |
| `UserMemory` | v10 | When `true`, this segment resides in user-accessible memory. |
| `InternalDescription` | v10 | Manufacturer-internal note. |

Contains `<Data>` (base64 binary) and optional `<Mask>` (base64 bitmask of writable bits).

**`<RelativeSegment>`** — a code block placed at an offset within a load-state-machine segment.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique identifier. |
| `Name` | v10 | Internal name (≤50 chars). |
| `Offset` | v10 | Byte offset within the LSM segment (0–1 048 575). |
| `Size` | v10 | Size in bytes (0–1 048 575). |
| `LoadStateMachine` | v10 | Index of the load state machine that owns this segment. |
| `InternalDescription` | v10 | Manufacturer-internal note. |

Contains `<Data>` (base64) and optional `<Mask>` (base64).

---

#### `<ComObjectTable>`

Used inside `ApplicationProgram/<Static>`. Defines the base communication objects for an application program.

The table element itself carries two device memory layout attributes:

| Attribute | Since | Description |
|---|---|---|
| `CodeSegment` | v10 | Reference to the memory segment that holds the group object table on the device. |
| `Offset` | v10 | Byte offset within that segment (0–1 048 575). |

Each `<ComObject>` child:

| Attribute | Since | Type | Req | Description |
|---|---|---|---|---|
| `Id` | v10 | string | yes | Unique base definition ID; referenced by `ComObjectRef/@RefId`. |
| `Name` | v10 | string ≤255 | yes | Internal identifier-style name. |
| `Text` | v10 | string ≤255 | yes | Display label shown in ETS (preferred over `Name` for UI). |
| `Number` | v10 | int | yes | KNX group object number on the device (0–255+). Objects are sorted by this value in the parsed output. |
| `FunctionText` | v10 | string ≤255 | yes | Functional role label (e.g. `"Switching"`, `"Dimming"`). Used as the `{{0}}` template substitution source. |
| `ObjectSize` | v10 | enum | yes | Wire size of the object's value. Values: `"1 Bit"`, `"2 Bit"` … `"7 Bit"`, `"1 Byte"` … `"24 Bytes"`, `"LegacyVarData"`. Must match the DPT's encoding width. |
| `Priority` | v10 | enum | no | KNX telegram priority: `Low` (default), `High`, `Alert`. |
| `DatapointType` | v10 | token list | no | Space-separated DPT codes, e.g. `"DPT-1 DPT-5.1"`. Describes the value encoding. |
| `CommunicationFlag` | v10 | `Enabled`/`Disabled` | yes | Enables participation in bus communication. |
| `ReadFlag` | v10 | `Enabled`/`Disabled` | yes | Device responds to read requests from other devices. |
| `WriteFlag` | v10 | `Enabled`/`Disabled` | yes | Device accepts write telegrams from other devices. |
| `TransmitFlag` | v10 | `Enabled`/`Disabled` | yes | Device autonomously sends the value when it changes. |
| `UpdateFlag` | v10 | `Enabled`/`Disabled` | yes | Device updates its internal value when it receives a write telegram. |
| `ReadOnInitFlag` | v10 | `Enabled`/`Disabled` | yes | Device issues a read request on startup to fetch the current bus value. |
| `InternalDescription` | v12 | string | no | Manufacturer-internal note; not shown in ETS. |
| `SecurityRequired` | v13 | enum | no | KNX Security requirement: `None` (default), `Auth` (authenticated), `AuthAndConf` (authenticated + encrypted). |
| `MayRead` | v20 | bool | no | Hint that this object's value may be read even when `ReadFlag` is disabled. Used by ETS for display purposes. |
| `ReadFlagLocked` | v20 | bool | no | When `true`, the user cannot change `ReadFlag` in ETS. Default: `false`. |
| `WriteFlagLocked` | v20 | bool | no | Locks `WriteFlag`. |
| `TransmitFlagLocked` | v20 | bool | no | Locks `TransmitFlag`. |
| `UpdateFlagLocked` | v20 | bool | no | Locks `UpdateFlag`. |
| `ReadOnInitFlagLocked` | v20 | bool | no | Locks `ReadOnInitFlag`. |

**Removed attributes:**

| Attribute | Versions | Description |
|---|---|---|
| `VisibleDescription` | v10–v11 | Public-facing description shown in ETS. Removed in v12 with no replacement; use `InternalDescription` for internal notes only. |

---

#### `<ComObjectRefs>`

Usable instances of communication objects, can override base definitions.

Each `<ComObjectRef>`:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ref ID; referenced by `<ComObjectRefRef>` in the `<Dynamic>` section. |
| `RefId` | v10 | Points to the base `<ComObject/@Id>`. |
| `Name` | v10 | Override of the base `Name` (optional). |
| `Text` | v10 | Override of the display label (optional). |
| `Tag` | v10 | Short tag string (≤50 chars) for tooling or semantic grouping; not shown in ETS UI. |
| `FunctionText` | v10 | Override of the `{{0}}` template substitution source. |
| `Number` | v10 | Override of the object number (optional). |
| `ObjectSize` | v10 | Override of the wire size (optional). |
| `Priority` | v10 | Override of the telegram priority (optional). |
| `DatapointType` | v10 | Override of DPT codes (optional). |
| `CommunicationFlag` | v10 | Override (optional). |
| `ReadFlag` | v10 | Override (optional). |
| `WriteFlag` | v10 | Override (optional). |
| `TransmitFlag` | v10 | Override (optional). |
| `UpdateFlag` | v10 | Override (optional). |
| `ReadOnInitFlag` | v10 | Override (optional). |
| `TextParameterRefId` | v12 | Reference to a `ParameterRef/@Id` whose current value is used as the display label at runtime, replacing `Text`. |
| `InternalDescription` | v12 | Manufacturer-internal note. |
| `Roles` | v13 | Space-separated semantic role tokens used by ETS for automatic group address linking suggestions. |
| `SecurityRequired` | v13 | Override of security requirement (optional). |
| `MayRead` | v20 | Override (optional). |
| `ReadFlagLocked` | v20 | Override of lock (optional). |
| `WriteFlagLocked` | v20 | Override of lock (optional). |
| `TransmitFlagLocked` | v20 | Override of lock (optional). |
| `UpdateFlagLocked` | v20 | Override of lock (optional). |
| `ReadOnInitFlagLocked` | v20 | Override of lock (optional). |
| `Semantics` | v20 | Free-text semantic description for tooling. |

Resolution order: ref attributes take precedence over base `<ComObject>` attributes when present.

**Removed attributes:**

| Attribute | Versions | Description |
|---|---|---|
| `VisibleDescription` | v10–v11 | Public-facing description shown in ETS. Removed in v12; use `InternalDescription` instead. |

> **Note on `<ModuleDef>/<Static>/<ComObjects>`:** Module definitions use `<ComObjects>` instead of `<ComObjectTable>`. The contained `<ComObject>` elements are identical to those above, but carry one additional attribute:
>
> | Attribute | Since | Description |
> |---|---|---|
> | `BaseNumber` | v20 | Base offset added to all `Number` values in this module when the module is instantiated. Allows a single module definition to be reused for multiple channels without object number collisions. |
>
> `<ComObjects>` has no `CodeSegment` or `Offset` attributes.

---

#### `<AddressTable>`

*(ApplicationProgram/Static only — not in ModuleDef/Static)*

Locates the KNX individual-address table in device memory.

| Attribute | Since | Description |
|---|---|---|
| `CodeSegment` | v10 | Reference to the memory segment holding the address table. |
| `Offset` | v10 | Byte offset within that segment (0–1 048 575). |
| `MaxEntries` | v10 | Maximum number of individual addresses the table can hold. |

---

#### `<AssociationTable>`

*(ApplicationProgram/Static only — not in ModuleDef/Static)*

Locates the KNX group-address association table in device memory. Each entry associates a group address (from the address table) with a communication object.

| Attribute | Since | Description |
|---|---|---|
| `CodeSegment` | v10 | Reference to the memory segment holding the association table. |
| `Offset` | v10 | Byte offset within that segment (0–1 048 575). |
| `MaxEntries` | v10 | Maximum number of entries in the association table. |

---

#### `<FixupList>`

*(ApplicationProgram/Static only)*

A list of relocation fixups applied after the firmware image is loaded. Each `<Fixup>` patches a set of byte offsets within a code segment to resolve a function reference (used for position-independent code).

| Attribute | Since | Description |
|---|---|---|
| `FunctionRef` | v10 | Name of the function whose resolved address is written into the patched offsets. |
| `CodeSegment` | v10 | Reference to the `<Code>/<AbsoluteSegment>` or `<RelativeSegment>` being patched. |

Child element: one or more `<Offset>` integer values — the byte positions within the segment to patch (0–65 535).

---

#### `<BusInterfaces>` *(since v14)*

*(ApplicationProgram/Static only)*

Describes secondary bus interfaces exposed by couplers and proxy devices (e.g. a KNX-USB interface or a tunneling gateway). Each `<BusInterface>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v14 | Unique identifier. |
| `AddressIndex` | v14 | Index into the additional-address table for this interface's individual address. |
| `AccessType` | v14 | Interface type: `Tunneling`, `USB`, or `Routing`. |
| `Text` | v14 | Human-readable label (optional, ≤255 chars). |

---

#### `<Messages>` *(since v14)*

*(ApplicationProgram/Static only)*

Named string constants referenced by ETS dialogs, error messages, or progress text steps in `<LoadProcedures>`. Each `<Message>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v14 | Unique identifier; referenced by `LdCtrlProgressText` and similar load steps via `MessageRef`. |
| `Name` | v14 | Internal name (≤50 chars). |
| `Text` | v14 | The message string displayed in ETS (≤255 chars). |
| `InternalDescription` | v14 | Manufacturer-internal note. |

---

#### `<ParameterValidations>` *(since v14)*

*(ApplicationProgram/Static only)*

Cross-parameter validation rules evaluated by ETS to check consistency between multiple parameters. Each `<ParameterValidation>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v14 | Unique identifier. |
| `Name` | v14 | Internal name (≤50 chars). |
| `ValidationFunc` | v14 | Name of the validation function to invoke. |
| `ValidationParameters` | v14 | Optional extra arguments passed to `ValidationFunc`. |
| `InternalDescription` | v14 | Manufacturer-internal note. |

Child element: `<Parameters>` — list of `<ParameterRefRef RefId="..." AliasName="...">` passing the referenced parameter values to the validation function. `AliasName` gives the function's local name for that parameter.

---

#### `<Script>` *(since v14)*

*(ApplicationProgram/Static only)*

A raw string element containing an ETS script (VBScript or JavaScript). The script is executed by ETS during project-level operations such as parameter initialization or consistency checks. The element has no attributes — its entire content is the script text.

---

#### `<SecurityRoles>` *(since v14)*

*(ApplicationProgram/Static only)*

Defines named security roles used by KNX Security. ETS uses these to assign access rights to tunneling users. Each `<SecurityRole>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v14 | Unique identifier. |
| `Text` | v14 | Human-readable role name shown in ETS (≤255 chars). |
| `Mask` | v14 | Bitmask of permissions granted to this role. |

---

#### `<Allocators>` *(since v20)*

Numeric range allocators used by the module system. When a `<ModuleDef>` is instantiated multiple times, allocators assign non-overlapping numeric ranges (e.g. com-object number ranges) to each instance automatically.

Each `<Allocator>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v20 | Unique identifier; referenced by module instances. |
| `Name` | v20 | Internal name (≤255 chars). |
| `Start` | v20 | First value in the allocatable range. |
| `maxInclusive` | v20 | Last value in the allocatable range (inclusive). |
| `ErrorMessageRef` | v20 | Reference to a `<Message/@Id>` shown if allocation fails. |
| `InternalDescription` | v20 | Manufacturer-internal note. |

---

#### `<LoadProcedures>`

Firmware download sequence. Consumed by ETS; not needed for parameter/com-object parsing.

Each `<LoadProcedure>` is an ordered list of load control steps. The `ApplicationProgram/@LoadProcedureStyle` controls how ETS combines multiple procedures.

Step element names map to the following kinds (camel-cased from XML element names):

| XML element | Kind string | Purpose |
|---|---|---|
| `LdCtrlUnload` | `Unload` | Unload the application on device. |
| `LdCtrlLoad` | `Load` | Initiate application load. |
| `LdCtrlMaxLength` | `MaxLength` | Set maximum memory segment length. |
| `LdCtrlAbsSegment` | `AbsSegment` | Write an absolute memory segment. |
| `LdCtrlRelSegment` | `RelSegment` | Write a relative memory segment. |
| `LdCtrlTaskSegment` | `TaskSegment` | Write a task table segment. |
| `LdCtrlTaskPtr` | `TaskPtr` | Set a task pointer. |
| `LdCtrlTaskCtrl1` | `TaskCtrl1` | Task control register 1. |
| `LdCtrlTaskCtrl2` | `TaskCtrl2` | Task control register 2. |
| `LdCtrlWriteProp` | `WriteProp` | Write a device property. |
| `LdCtrlCompareProp` | `CompareProp` | Compare a device property. |
| `LdCtrlLoadImageProp` | `LoadImageProp` | Load image via property. |
| `LdCtrlWriteMem` | `WriteMem` | Write absolute memory. |
| `LdCtrlCompareMem` | `CompareMem` | Compare memory. |
| `LdCtrlLoadImageMem` | `LoadImageMem` | Load image into memory. |
| `LdCtrlWriteRelMem` | `WriteRelMem` | Write relative memory. |
| `LdCtrlInvokeFunctionProp` | `InvokeFunctionProp` | Invoke a function property. |
| `LdCtrlReadFunctionProp` | `ReadFunctionProp` | Read a function property result. |
| `LdCtrlMerge` | `Merge` | Merge step (combine procedures). |
| `LdCtrlConnect` | `Connect` | Open management connection to device. |
| `LdCtrlDisconnect` | `Disconnect` | Close management connection. |
| `LdCtrlSetControlVariable` | `SetControlVariable` | Set a load state machine variable. |
| `LdCtrlMapError` | `MapError` | Map an error code to a message. |
| `LdCtrlProgressText` | `ProgressText` | Emit a progress message in ETS. |
| `LdCtrlRestart` | `Restart` | Restart the device. |
| `LdCtrlMasterReset` | `MasterReset` | Factory-reset the device. |
| `LdCtrlDelay` | `Delay` | Wait a fixed duration. |
| `LdCtrlLoadCompleted` | `LoadCompleted` | Signal load completion. |
| `LdCtrlClearCachedObjectTypes` | `ClearCachedObjectTypes` | Clear cached object type table. |
| `LdCtrlClearLcfilterTable` | `ClearLcfilterTable` | Clear line coupler filter table. |
| `LdCtrlDeclarePropDesc` | `DeclarePropDesc` | Declare a property description. |

Common step attributes (not all steps carry all attributes):

| Attribute | Description |
|---|---|
| `AppliesTo` | Scope: `auto`, `application`, `module`, or a specific object index. |
| `LsmIdx` | Load state machine index. |
| `ObjIdx` | Target interface object index. |
| `ObjType` | Interface object type. |
| `Occurrence` | Occurrence selector when multiple objects share a type. |
| `PropId` | Property ID within the interface object. |
| `SegType` | Segment type (`Data`, `Code`, `Poll`, etc.). |
| `Address` | Memory address (absolute or relative). |
| `Size` | Size in bytes. |
| `Count` | Number of elements. |
| `MemType` | Memory addressing mode (`Absolute`, `Relative`). |

---

#### `<Extension>`

*(ApplicationProgram/Static only)*

References ETS vendor plugin assemblies that must be loaded alongside this application. Plugins extend ETS with custom download, UI, or data-handling logic.

| Attribute | Since | Description |
|---|---|---|
| `EtsDownloadPlugin` | v10 | Assembly identifier for the ETS download plugin. |
| `EtsUiPlugin` | v10 | Assembly identifier for the ETS UI plugin. |
| `EtsDataHandler` | v10 | Assembly identifier for the ETS data-handler plugin. |
| `EtsDataHandlerCapabilities` | v10 | Space-separated capability tokens the data handler provides (e.g. `AddDeleteDevice`, `TransferParameters`). |
| `RequiresExternalSoftware` | v10 | When `true`, ETS requires external (non-plugin) software to be installed before programming. |

Child element: `<Baggages>` — list of `<Baggage RefId="...">` linking to external resource files bundled in the archive.

---

#### `<BinaryData>`

Named binary blobs embedded in the archive and referenced by the application (e.g. lookup tables, calibration data). Each `<BinaryData>` element:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique identifier. |
| `Name` | v10 | Internal name (≤50 chars). |
| `InternalDescription` | v10 | Manufacturer-internal note. |

Child element: `<Data>` — the binary payload (base64-encoded).

---

#### `<DeviceCompare>`

*(ApplicationProgram/Static only)*

Specifies memory regions and properties that ETS should skip when comparing the device's current state against the expected application state (e.g. volatile runtime counters that should not trigger a "device differs" warning).

Child elements:

**`<ExcludeMemory>`** — excludes a memory range from comparison.

| Attribute | Since | Description |
|---|---|---|
| `CodeSegment` | v10 | Reference to the code segment containing the excluded region. |
| `Offset` | v10 | Start offset within the segment. |
| `Size` | v10 | Number of bytes to exclude. |
| `InternalDescription` | v12 | Manufacturer-internal note. |

**`<ExcludeProperty>`** — excludes a KNX interface object property from comparison.

| Attribute | Since | Description |
|---|---|---|
| `ObjectIndex` | v10 | Interface object index (optional; matches any if absent). |
| `ObjectType` | v10 | Interface object type (optional). |
| `Occurrence` | v10 | Occurrence index when multiple objects share a type (default `0`). |
| `PropertyId` | v10 | Property ID within the interface object. |
| `Offset` | v10 | Byte offset within the property value. |
| `Size` | v10 | Number of bytes to exclude. |
| `InternalDescription` | v12 | Manufacturer-internal note. |

---

#### `<Options>`

*(ApplicationProgram/Static only)*

ETS behavioral flags for download, comparison, and legacy compatibility. All attributes are optional booleans unless noted.

| Attribute | Since | Description |
|---|---|---|
| `PreferPartialDownloadIfApplicationLoaded` | v10 | Prefer incremental (partial) download when the application is already loaded on the device. |
| `EasyCtrlModeModeStyleEmptyGroupComTables` | v10 | EasyControl mode: leave group com tables empty. |
| `SetObjectTableLengthAlwaysToOne` | v10 | Always set the object table length to 1, regardless of the actual number of com objects. |
| `TextParameterEncoding` | v10 | Text encoding for string parameters (legacy fixed enum). |
| `TextParameterEncodingSelector` | v11 | Text encoding selector (replaces `TextParameterEncoding`). |
| `TextParameterZeroTerminate` | v10 | Null-terminate string parameter values when downloading. |
| `ParameterByteOrder` | v10 | Byte order for multi-byte parameters: `BigEndian` or `LittleEndian`. |
| `PartialDownloadOnlyVisibleParameters` | v14 | During partial download, only send parameters visible under the current configuration. |
| `LegacyNoPartialDownload` | v10 | Disable partial download (always do a full download). |
| `LegacyNoMemoryVerifyMode` | v10 | Disable memory verification after download. |
| `LegacyNoOptimisticWrite` | v10 | Disable optimistic write (always read-back after write). |
| `LegacyDoNotReportPropertyWriteErrors` | v10 | Suppress property write errors. |
| `LegacyNoBackgroundDownload` | v10 | Disable background downloading. |
| `LegacyDoNotCheckManufacturerId` | v10 | Skip manufacturer ID check before programming. |
| `LegacyAlwaysReloadAppIfCoVisibilityChanged` | v10 | Force full reload when com-object visibility changes. |
| `LegacyNeverReloadAppIfCoVisibilityChanged` | v10 | Never reload when com-object visibility changes. |
| `Comparable` | v14 | Application supports device-state comparison. |
| `Reconstructable` | v14 | Application state can be reconstructed from the device without a full readback. |
| `DownloadInvisibleParameters` | v14 | Download parameters not currently visible in the ETS UI. |
| `SupportsExtendedMemoryServices` | v20 | Device supports extended memory access services. |
| `SupportsExtendedPropertyServices` | v20 | Device supports extended property access services. |
| `SupportsIPSystemBroadcast` | v20 | Device supports IP system broadcast. |
| `NotLoadable` | v20 | Device cannot be programmed by ETS (display only). |
| `CustomerAdjustableParameters` | v20 | Application has parameters marked as customer-adjustable. |

---

### `<Dynamic>` section

Defines the conditional visibility of parameters and communication objects in the ETS UI. The tree is evaluated against the current parameter values to produce the visible set.

The root `<Dynamic>` element can contain `<Channel>`, `<ChannelIndependentBlock>`, `<Choose>`, `<Module>` *(v20+)*, and `<Repeat>` *(v20+)* elements.

#### `<Channel>` element

A named, numbered UI section representing a device channel. Contains parameter blocks, com-object refs, and conditional branches.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique section ID. |
| `Name` | v10 | Internal name (≤255 chars). |
| `Text` | v10 | Display heading in ETS (may contain template placeholders). |
| `Number` | v10 | Channel number; used for ordering and template substitution. String (≤50 chars). |
| `TextParameterRefId` | v12 | Reference to a `ParameterRef/@Id` whose current value is used as the heading instead of `Text`. |
| `InternalDescription` | v12 | Manufacturer-internal note. |
| `Icon` | v14 | Icon identifier shown next to the channel heading in ETS. |
| `HelpContext` | v14 | Context-sensitive help reference string. |
| `Semantics` | v20 | Semantic classification for tooling. |

Child elements: `<ParameterBlock>`, `<ComObjectRefRef>`, `<BinaryDataRef>`, `<Choose>`, `<Module>` *(v20+)*, `<Repeat>` *(v20+)*.

---

#### `<ChannelIndependentBlock>` element

A structural wrapper for parameter blocks and com-object refs that are not associated with any specific channel. Has no attributes of its own.

Child elements: `<ParameterBlock>`, `<BinaryDataRef>`, `<Choose>`, `<ComObjectRefRef>` *(v20+)*, `<Module>` *(v20+)*, `<Repeat>` *(v20+)*.

---

#### `<ParameterBlock>` element

A collapsible group of parameters within a channel or `<ChannelIndependentBlock>`. Can be nested.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique section ID. |
| `Name` | v10 | Internal name (≤255 chars). |
| `Text` | v10 | Display heading in ETS (may contain template placeholders). |
| `Access` | v10 | Edit permission for all parameters in this block: `None`, `Read`, `ReadWrite` (default). |
| `HelpTopic` | v10 | Integer ETS help topic ID for this block. |
| `InternalDescription` | v10 | Manufacturer-internal note. |
| `ParamRefId` | v10 | Reference to a `ParameterRef/@Id`; its current value is used as the block heading instead of `Text`. |
| `TextParameterRefId` | v12 | Reference to a `ParameterRef/@Id` whose current value is used as the heading. Takes precedence over `ParamRefId`. |
| `Inline` | v14 | When `true`, renders the block's parameters inline without a separate heading. |
| `Layout` | v14 | Layout mode: `List` (default, vertical) or `Grid` (tabular). |
| `Cell` | v14 | Grid position in the form `row,col` (only meaningful when `Layout="Grid"`). |
| `Icon` | v14 | Icon identifier shown next to the block heading. |
| `HelpContext` | v14 | Context-sensitive help reference string. |
| `ShowInComObjectTree` | v14 | When `true`, group objects in this block appear in the ETS com-object tree. |
| `Semantics` | v20 | Semantic classification for tooling. |

Child elements: `<ParameterRefRef>`, `<ComObjectRefRef>`, `<ParameterSeparator>`, `<BinaryDataRef>`, `<Assign>`, nested `<ParameterBlock>`, `<Choose>`, `<Button>` *(v14+)*, `<Module>` *(v20+)*, `<Repeat>` *(v20+)*. When `Layout="Grid"`, the block may also contain `<Rows>` and `<Columns>` *(v14+)* layout definitions.

> [!WARNING]
> `<ParameterBlock>` is **not** valid at the top level of `ApplicationProgram/<Dynamic>` — it may only appear inside `<Channel>` or `<ChannelIndependentBlock>`. It is valid at the top level of `ModuleDef/<Dynamic>`.

---

#### `<Choose>` element

Conditional switch on a parameter value. There are four context-specific Choose variants; all share the same `ParamRefId` attribute and `<When>` children, but differ in which elements are allowed inside `<When>`:

| Context | Choose type | Allowed `<When>` children |
|---|---|---|
| Top-level `<Dynamic>` | `DependentChannelChoose` | `<Channel>`, nested `<Choose>`, `<ParameterBlockRename>` |
| Inside `<Channel>` | `ChannelChoose` | `<ParameterBlock>`, `<ComObjectRefRef>`, `<BinaryDataRef>`, nested `<Choose>`, `<ParameterBlockRename>` |
| Inside `<ChannelIndependentBlock>` | `IndependentParameterBlockChoose` | `<ParameterBlock>`, nested `<Choose>`, `<ParameterBlockRename>` |
| Inside `<ParameterBlock>` | `ComObjectParameterChoose` | `<ParameterRefRef>`, `<ParameterSeparator>`, `<ComObjectRefRef>`, `<BinaryDataRef>`, `<Assign>`, nested `<Choose>`, `<ParameterBlockRename>` |

| Attribute | Since | Description |
|---|---|---|
| `ParamRefId` | v10 | The `ParameterRef/@Id` whose current value drives the branch selection. |

#### `<When>` element

| Attribute | Since | Description |
|---|---|---|
| `test` | v10 | Space-separated list of parameter values (or a comparison expression like `>=5`) that activate this branch. |
| `default` | v10 | `true` if this branch is the fallback when no `test` values match. |

Evaluation rules:
1. Find the first `<When>` whose `test` list contains the current parameter value → show that branch.
2. If no match, use the `<When default="true">` branch.
3. If neither matches, nothing in this `<Choose>` is shown.

---

#### `<Module>` element *(since v20)*

Instantiates a `<ModuleDef>` with specific text argument values.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v20 | Instance ID. |
| `Name` | v20 | Instance display name. |
| `RefId` | v20 | Points to `<ModuleDef/@Id>` in the `<ModuleDefs>` section. |

Child elements:

- `<TextArg RefId="..." Value="...">` — supplies a string value for a named module argument.
- `<NumericArg RefId="..." Value="...">` — supplies a numeric value for a named module argument.

---

#### `<Repeat>` element *(since v20)*

Repeats a set of `<Module>` and `<Choose>` instantiations a fixed or parameter-driven number of times. Used to generate multiple channel instances from a single `<ModuleDef>` without enumerating each one.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v20 | Unique identifier. |
| `Name` | v20 | Internal name (≤255 chars). |
| `InternalDescription` | v20 | Manufacturer-internal note. |
| `ParameterRefId` | v20 | Reference to a `ParameterRef/@Id` whose current integer value determines the repeat count at runtime. If absent, `Count` is used instead. |
| `Count` | v20 | Static repeat count (default `0`). Used when `ParameterRefId` is not set. |

Child elements: `<Module>`, `<Choose>`, nested `<Repeat>`.

---

#### `<ParameterRefRef>` element

Leaf element that places a single parameter widget in the ETS UI.

| Attribute | Since | Description |
|---|---|---|
| `RefId` | v10 | References `ParameterRef/@Id` in `<Static>/<ParameterRefs>`. The referenced `ParameterRef` determines the parameter shown and any ref-level overrides. |

---

#### `<ComObjectRefRef>` element

Leaf element that places a com-object row in the ETS com-object table.

| Attribute | Since | Description |
|---|---|---|
| `RefId` | v10 | References `ComObjectRef/@Id` in `<Static>/<ComObjectRefs>`. |

---

#### `<ParameterSeparator>` element

A visual divider (horizontal rule + optional label) rendered between parameters in a `<ParameterBlock>`.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ID within the application. |
| `Text` | v10 | Label text displayed next to the separator line (≤255 chars). |
| `Access` | v10 | Visibility/editability: `None`, `Read`, `ReadWrite` (default). |
| `UIHint` | v14 | Rendering hint: `Separator` (default line) or `GroupBox` (box around subsequent items). |
| `TextParameterRefId` | v14 | Reference to a `ParameterRef/@Id` whose current value is used as the label instead of `Text`. |
| `InternalDescription` | v14 | Manufacturer-internal note. |
| `Cell` | v14 | Grid position in the form `row,col` (only meaningful when the enclosing `ParameterBlock` uses `Layout="Grid"`). |
| `Icon` | v14 | Icon identifier shown next to the separator. |

---

#### `<Button>` element *(since v14)*

A push-button widget inside a `<ParameterBlock>` that triggers an ETS plugin action.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v14 | Unique ID within the application. |
| `Text` | v14 | Button label (≤255 chars). |
| `Access` | v14 | `None`, `Read`, or `ReadWrite` (default). |
| `TextParameterRefId` | v14 | Reference to a `ParameterRef/@Id` whose current value is used as the label. |
| `InternalDescription` | v14 | Manufacturer-internal note. |
| `Cell` | v14 | Grid position `row,col`. |
| `Icon` | v14 | Icon identifier shown on the button. |
| `EventHandler` | v14 | Identifier of the ETS plugin event handler to invoke when the button is clicked. |
| `EventHandlerParameters` | v14 | Opaque string passed to the event handler. |
| `EventHandlerOnline` | v14 | When and how the button is callable: `Always`, `OnlyOffline`, `OnlyOnline`. |
| `Name` | v20 | Internal name for tooling (≤255 chars). |

---

#### `<Assign>` element

Copies a parameter value at download time. Used to synchronise one parameter from another, or to set a parameter to a fixed string value.

| Attribute | Since | Description |
|---|---|---|
| `TargetParamRefRef` | v10 | `ParameterRef/@Id` of the parameter to write. |
| `SourceParamRefRef` | v10 | `ParameterRef/@Id` to read the value from. Mutually exclusive with `Value`. |
| `Value` | v10 | Literal string value to assign. Mutually exclusive with `SourceParamRefRef`. |

Exactly one of `SourceParamRefRef` or `Value` must be present.

---

#### `<BinaryDataRef>` element

References (or embeds) a `<BinaryData>` blob within the Dynamic tree. Used to attach binary payloads to specific UI positions for download or plugin consumption.

| Attribute | Since | Description |
|---|---|---|
| `RefId` | v10 | References `<BinaryData/@Name>` in `<Static>/<BinaryData>`. |

Child element: `<Data>` — optional inline base64 blob overriding the static reference.

---

#### `<ParameterBlockRename>` element

Inside a `<When>` branch, renames an existing `<ParameterBlock>` (by ref). Used in module-based designs to give contextually appropriate labels to re-used blocks.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ID. |
| `RefId` | v10 | References the `<ParameterBlock/@Id>` to rename. |
| `Name` | v10 | New internal name (optional, ≤50 chars). |
| `Text` | v10 | New display heading (≤255 chars). |

---

#### `<Rows>` / `<Columns>` elements *(since v14)*

Grid layout definitions for a `<ParameterBlock Layout="Grid">`. A block may contain one `<Rows>` and one `<Columns>` child; each holds an ordered list of `<Row>` or `<Column>` items that define the grid structure. Individual parameters, separators, and buttons reference a cell via their `Cell="row,col"` attribute.

**`<Row>` attributes:**

| Attribute | Description |
|---|---|
| `Id` | Unique row ID. |
| `Name` | Internal name (≤50 chars). |
| `Text` | Row header label (≤255 chars). |
| `TextParameterRefId` | `ParameterRef/@Id` whose value is used as the header. |
| `CollapseIfEmpty` | When `true`, hide the row if it contains no visible items (default `false`). |
| `InternalDescription` | Manufacturer-internal note. |

**`<Column>` attributes:**

| Attribute | Description |
|---|---|
| `Id` | Unique column ID. |
| `Name` | Internal name (≤50 chars). |
| `Text` | Column header label (≤255 chars). |
| `TextParameterRefId` | `ParameterRef/@Id` whose value is used as the header. |
| `Width` | Column width as a percentage string, e.g. `"30%"` (must sum to 100%). |
| `InternalDescription` | Manufacturer-internal note. |

---

### `<ModuleDefs>` section *(since v20)*

Reusable parameter/com-object groups, typically used to define repeated channel structures.

Each `<ModuleDef>`:

| Attribute | Since | Description |
|---|---|---|
| `Id` | v20 | Unique ID; referenced by `<Module/@RefId>`. |
| `Name` | v20 | Internal name for tooling. |

Child elements:

- `<Arguments>` — list of `<Argument Id="..." Name="...">` declaring the template parameters.
- `<Static>` — subset of `ApplicationProgram/Static`. Contains: `<Parameters>`, `<ParameterRefs>`, `<ParameterCalculations>`, `<ParameterValidations>`, `<ComObjects>` (not `<ComObjectTable>`; each `<ComObject>` gains a `BaseNumber` attribute), `<ComObjectRefs>`, `<LoadProcedures>`, `<Allocators>`. Does **not** contain `<ParameterTypes>`, `<ComObjectTable>`, `<AddressTable>`, `<AssociationTable>`, `<Code>`, or `<BusInterfaces>` — those are application-level concerns.
- `<Dynamic>` — superset of `ApplicationProgram/Dynamic`. Contains all the same elements (`<ChannelIndependentBlock>`, `<Channel>`, `<Choose>`, `<Module>`, `<Repeat>`) and additionally allows `<ParameterBlock>` at the top level, which the application-level `<Dynamic>` does not permit.
- `<SubModuleDefs>` — nested module definitions, allowing multi-level module composition.

Module arguments are substituted into `Text` attributes via `{{ArgumentName}}` placeholders (see Template substitution below).

---

## Template substitution

`Text` attributes in `<Dynamic>` elements, `<ComObjectRef>`, and `<ComObject>` can contain placeholders:

| Placeholder | Source | Example result |
|---|---|---|
| `{{0}}` | `FunctionText` attribute of the enclosing `<ComObjectRef>` or `<Channel>` | `"Dimming"` |
| `{{ArgName}}` | Value of a `<TextArg>` or `<NumericArg>` with `RefId` matching the argument name | `"A"`, `"1"` |

Unresolved placeholders (no matching argument) are stripped from the output and surrounding whitespace is collapsed.

Example:
```
Text="Channel {{ChNo}}: {{0}}"
TextArg ChNo="A", FunctionText="Dimming"
→ "Channel A: Dimming"
```

---

## Catalog.xml

Defines the ETS product tree. Not parsed into `DeviceApplication`; used to link catalog entries to hardware/application IDs.

### `<CatalogSection>` element

Hierarchical category node (can be nested).

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ID. |
| `Name` | v10 | Category name (≤255 chars). |
| `Number` | v10 | Ordering number (≤20 chars). |
| `VisibleDescription` | v10 | Short description. |
| `DefaultLanguage` | v10 | BCP-47 language tag. |
| `InternalDescription` | v12 | Manufacturer-internal note. |

### `<CatalogItem>` element

A leaf entry representing one orderable product.

| Attribute | Since | Description |
|---|---|---|
| `Id` | v10 | Unique ID. |
| `Name` | v10 | Display name (≤255 chars). |
| `Number` | v10 | Ordering number within its section. |
| `VisibleDescription` | v10 | Short description. |
| `ProductRefId` | v10 | References `Hardware.xml/Hardware/Products/Product/@Id`. |
| `Hardware2ProgramRefId` | v10 | References `Hardware.xml/Hardware/Hardware2Programs/Hardware2Program/@Id`. |
| `DefaultLanguage` | v10 | BCP-47 language tag. |

---

## Schema version changelog

The namespace `http://knx.org/xml/project/{version}` identifies the schema version in every XML file in the archive. Versions 10–14 correspond to ETS 4/5 releases; versions 20–23 to ETS 6.

### v10 → v11

- **`ApplicationProgramT`**: added `CreatedFromLegacySchemaVersion` (bool flag set when the file was generated from a pre-v11 source).
- **`ParameterT` / `ParameterRefT`**: added `SuffixText` — a unit label appended after the parameter value in the ETS UI (e.g. `"ms"`, `"°C"`).
- **`Hardware2ProgramT`**: added `CheckSums` and `LoadedImage` (pre-built firmware image embedded in archive).
- **`TypePicture`**: new parameter type for binary image data.
- **`SplitInfoT`**: new element tracking installation split information.
- Enum `OptionsTextParameterEncoding` replaced by `OptionsTextParameterEncodingSelector`.

### v11 → v12

- **`ApplicationProgramT`**: added `InternalDescription`.
- **`ComObjectT`**: `VisibleDescription` removed; replaced by `InternalDescription` (manufacturer-internal, not shown in ETS).
- **`ComObjectRefT`**: same — `VisibleDescription` removed, `InternalDescription` and `TextParameterRefId` added.
- **`HardwareT`**: added `IsRFRetransmitter`, `RFDeviceMode`, `RuntimeUnidirectional`, `InternalDescription`.
- **`ParameterT` / `ParameterRefT`**: added `InternalDescription`; `ParameterRefT` also gains `TextParameterRefId`.
- **`ChannelT`**: added `TextParameterRefId`, `InternalDescription`.
- **`ParameterBlockT`**: added `TextParameterRefId`.
- **`CatalogSectionT`**: added `InternalDescription`.
- New functional block and group address reference types added (`FunctionalBlock`, `GroupAddressRefT`, `FunctionT`).
- `AddInData` renamed to `AddinData`.

### v12 → v13

- **KNX Security introduced.**
- **`ApplicationProgramT`**: added `IsSecureEnabled`, `MaxUserEntries`, `MaxTunnelingUserEntries`, `MaxSecurityIndividualAddressEntries`, `MaxSecurityGroupKeyTableEntries`, `MaxSecurityP2PKeyTableEntries`, `TunnelingAddressIndices`.
- **`ComObjectT`**: added `SecurityRequired` (`None` / `Auth` / `AuthAndConf`).
- **`ComObjectRefT`**: added `Roles` (semantic role tokens for automatic group address linking), `SecurityRequired`.
- New classes: `BusInterfaceT`, `DeviceCertificateT`, `ChannelInstanceT`, `SecurityT`.

### v13 → v14

- **`ApplicationProgramStaticT`**: `<Options>` gains `PartialDownloadOnlyVisibleParameters`, `Comparable`, `Reconstructable`, `DownloadInvisibleParameters`.
- **`ApplicationProgramT`**: added `ContextHelpFile`, `IconFile`; removed `TunnelingAddressIndices` (a space-separated list of address indices for KNX Security tunneling, present only in v13 — dropped without replacement in v14).
- **`ApplicationProgramStaticT`**: major expansion — added `<BusInterfaces>`, `<Messages>`, `<ParameterValidations>`, `<Script>`, `<SecurityRoles>`.
- **`ParameterT`**: added `CustomerAdjustable`, `InitialValue`.
- **`ParameterRefT`**: added `CustomerAdjustable`, `ForbidGrantingUseByCustomer`, `InitialValue`.
- **`ChannelT`**: added `Icon`, `HelpContext`.
- **`ParameterBlockT`**: added `Inline`, `Layout`, `Cell`, `Icon`, `HelpContext`, `ShowInComObjectTree`. Grid layout support: `<Rows>` and `<Columns>` child elements.
- **`ParameterSeparatorT`**: added `UIHint`, `TextParameterRefId`, `InternalDescription`, `Cell`, `Icon`.
- New Dynamic leaf element: `<Button>` — a plugin-triggering push-button widget.
- New parameter type `TypeRawData`.
- New UI layout types: `Column`, `Row`, `SpaceT`, `ParameterBlockLayoutT`.
- LdCtrl classes renamed with `T` suffix throughout.

### v14 → v20

- **Major release. Module system introduced.**
- **`ApplicationProgramT`**: added `ModuleDefs`, `Semantics`, `MaxSecurityProxyGroupKeyTableEntries`, `MaxSecurityProxyIndividualAddressTableEntries`.
- **`ApplicationProgramStaticT`**: added `<Allocators>`; `<Options>` gains `SupportsExtendedMemoryServices`, `SupportsExtendedPropertyServices`, `SupportsIPSystemBroadcast`, `NotLoadable`, `CustomerAdjustableParameters`; `<ParameterCalculations>` now also present in `ModuleDefStaticT`.
- **`ApplicationProgramDynamicT`**: added `<Module>` and `<Repeat>` — applications can now instantiate module definitions and repeat them.
- **`ButtonT`**: added `Name` attribute.
- **`ComObjectT`**: added all five flag lock attributes (`ReadFlagLocked`, `WriteFlagLocked`, `TransmitFlagLocked`, `UpdateFlagLocked`, `ReadOnInitFlagLocked`) and `MayRead`.
- **`ComObjectRefT`**: same flag locks plus `Semantics`.
- **`ChannelT`**: added `Semantics`.
- **`ParameterBlockT`**: added `Semantics`.
- **`HardwareT`**: added `Tp256`, `RFRxCapabilities`, `RFTxCapabilities`; removed `RFDeviceMode`, `RuntimeUnidirectional`.
- **`Hardware2ProgramT`**: added `CouplerCapabilities`.
- **`ParameterRefT`**: added `Semantics`.
- New module infrastructure: `ModuleDefT`, `ModuleDefStaticT`, `ModuleDefDynamicT`, `ModuleT`, `RepeatT`, `AllocatorT`, `SubModuleDefs`, `TextArg`, `NumericArg`, `ModuleArgT`.
- `ModuleDefDynamic` gains `<ParameterBlock>` at top level (not available in `ApplicationProgramDynamic`).
- Module com objects use `<ComObjects>` with `BaseNumber` instead of `<ComObjectTable>`.

### v20 → v21

- **`ApplicationProgramT`**: added `HardwareType`; removed `MaxSecurityProxyIndividualAddressTableEntries`.
- **`HardwareT`**: added `Semantics`; `RFRxCapabilities` and `RFTxCapabilities` **moved** to `<Hardware2Program>`.
- **`Hardware2ProgramT`**: now carries `RFRxCapabilities`, `RFTxCapabilities`, `Semantics`.
- New: `Tag` / `Tags` elements; `Segment`; `ProjectTypeT` enum.

### v21 → v22

- **`ComObjectT`**: added `IoTpointReference` — links a com object to an IoT data point.
- **`Hardware2ProgramT`**: added `SleepCycleTimeSeconds` for RF battery devices.
- New: `IoTpointParameterT` class supporting IoT integration.

### v22 → v23

- **`ApplicationProgramT`**: added `CloudConnect` and `Profile` — cloud connectivity configuration.
- New: `IoT` and `Profile` classes.
- New enum: `ApplicationProgramTCloudConnect`.
