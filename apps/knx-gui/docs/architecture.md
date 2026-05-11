# KNX GUI Architecture

## Overview

The application follows a template/instance pattern where immutable device templates from the catalog are instantiated into configurable devices in projects.

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CATALOG                                  │
│  .xknxcatalog file (SQLite)                                      │
│                                                                  │
│  ApplicationModel                                                │
│    ├── application_id: str (unique key, e.g. "M-0083_A-0009...")│
│    ├── manufacturer_id: str                                      │
│    ├── name: str                                                 │
│    └── xml_data: bytes (raw application XML from knxprod)        │
│                                                                  │
│  Immutable. Never modified after import.                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ parse_application_xml()
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DeviceApplication                             │
│  (from knx_gui.knxprod.types)                                    │
│                                                                  │
│  Contains ALL data from knxprod:                                 │
│    ├── com_objects: list[ComObject]  (ALL, not filtered)         │
│    ├── parameters: list[Parameter]   (ALL, not filtered)         │
│    ├── dynamic: DynamicElement       (visibility rules tree)     │
│    └── methods:                                                  │
│        ├── visible_com_objects(param_values) -> filtered list    │
│        └── visible_parameters(param_values) -> filtered list     │
│                                                                  │
│  Immutable. Treated as the "blueprint" for devices.              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PROJECT                                  │
│  .xknx file (SQLite with event sourcing)                         │
│                                                                  │
│  DeviceModel                                                     │
│    ├── id: int (autoincrement)                                   │
│    ├── template_id: str (references catalog application_id)      │
│    ├── name: str                                                 │
│    └── address: str | None                                       │
│                                                                  │
│  ParameterModel (OVERRIDES only)                                 │
│    ├── device_id: int                                            │
│    ├── param_id: str                                             │
│    └── value: str                                                │
│                                                                  │
│  ComObjectModel (OVERRIDES only)                                 │
│    ├── device_id: int                                            │
│    ├── co_id: str                                                │
│    ├── dpt_major: int                                            │
│    ├── dpt_minor: int                                            │
│    └── flag_*: bool (communication, read, write, transmit, etc.) │
│                                                                  │
│  Stores only DELTAS from template defaults.                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DEVICE (runtime)                            │
│  (from knx_gui.types)                                            │
│                                                                  │
│  Device                                                          │
│    ├── node_id: int                                              │
│    ├── name: str                                                 │
│    ├── address: str                                              │
│    ├── app: DeviceApplication (immutable reference)              │
│    ├── com_objects: list[ComObject] (ALL, with overrides applied)│
│    └── _param_values: dict[str, str] (defaults + overrides)      │
│                                                                  │
│  Methods (compute at runtime):                                   │
│    ├── get_visible_com_objects() -> uses app.visible_com_objects │
│    ├── get_visible_parameters() -> uses app.visible_parameters   │
│    └── set_param_value() -> invalidates visibility cache         │
│                                                                  │
│  Visibility is DYNAMIC - changes when parameters change.         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Catalog is immutable**: Raw knxprod XML stored as-is. Never filtered or modified.

2. **DeviceApplication is immutable**: Parsed from catalog XML. Contains ALL com objects and parameters plus the DynamicElement tree for computing visibility.

3. **Project stores overrides only**: Parameter values and com object flags that differ from template defaults.

4. **Visibility computed at runtime**: `Device.get_visible_com_objects()` calls `app.visible_com_objects(current_param_values)`. When user changes a parameter, visibility is recomputed.

5. **Com objects hold current state**: `Device.com_objects` contains ALL com objects from the template with overrides (DPT, flags) applied. The `get_visible_com_objects()` method filters this list based on current parameter values.

## Loading a Device from Project

```python
def load_device(device_model, catalog):
    # 1. Get immutable template from catalog
    xml_data = get_application_xml(catalog, device_model.template_id)
    app = parse_application_xml(xml_data, manufacturer_id)[0]
    
    # 2. Create device with ALL com objects from template
    device = Device(
        node_id=device_model.id,
        name=device_model.name,
        address=device_model.address,
        app=app,
    )
    
    # 3. Apply parameter overrides
    for param in device_model.parameters:
        device.set_param_value(param.param_id, param.value)
    
    # 4. Apply com object overrides (DPT, flags)
    for co_override in device_model.com_objects:
        co = device.find_com_object(co_override.co_id)
        if co:
            co.dpt = lookup_dpt(co_override.dpt_major, co_override.dpt_minor)
            co.flags.communication = co_override.flag_communication
            # ... other flags
    
    return device
```

## Event Sourcing

All mutations go through events (see `project/events.py`):
- `DeviceAdded`: Stores template_id + initial parameter values + initial com object states
- `DeviceRemoved`: Stores full device state for undo
- `ParameterChanged`: Stores device_id, param_id, old_value, new_value
- `ComObjectFlagChanged`: Stores device_id, co_id, flag_name, old_value, new_value
- `ComObjectDptChanged`: Stores device_id, co_id, old/new dpt_major/minor

Events can be reverted (undo) by applying the inverse operation.
