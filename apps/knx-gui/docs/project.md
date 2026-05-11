# Project Persistence Architecture

## Overview

KNX GUI uses SQLite3 for project persistence with an event sourcing pattern. Every user action is stored as an immutable event, enabling full undo/redo support.

## Database Schema

### Events Table
Stores all user actions as serialized events.

| Column    | Type     | Description                              |
|-----------|----------|------------------------------------------|
| id        | INTEGER  | Primary key, auto-increment              |
| type      | TEXT     | Event class name (e.g., "DeviceAdded")   |
| data      | JSON     | Serialized event payload                 |
| timestamp | DATETIME | When the event occurred (UTC)            |
| reverted  | BOOLEAN  | True if event has been undone            |

### Devices Table
Materialized state for devices.

| Column      | Type    | Description                    |
|-------------|---------|--------------------------------|
| id          | INTEGER | Primary key (node_id)          |
| address     | TEXT    | KNX individual address         |
| template_id | TEXT    | Reference to device template   |
| name        | TEXT    | User-defined device name       |

### Parameters Table
Stores device parameter values.

| Column    | Type    | Description                    |
|-----------|---------|--------------------------------|
| id        | INTEGER | Primary key, auto-increment    |
| device_id | INTEGER | Foreign key to devices         |
| param_id  | TEXT    | Parameter identifier           |
| value     | TEXT    | Current parameter value        |

### Com Objects Table
Stores communication object configuration.

| Column             | Type    | Description                    |
|--------------------|---------|--------------------------------|
| id                 | INTEGER | Primary key, auto-increment    |
| device_id          | INTEGER | Foreign key to devices         |
| co_id              | TEXT    | Com object identifier          |
| dpt_major          | INTEGER | DPT major number               |
| dpt_minor          | INTEGER | DPT minor number               |
| flag_communication | BOOLEAN | Communication flag             |
| flag_read          | BOOLEAN | Read flag                      |
| flag_write         | BOOLEAN | Write flag                     |
| flag_transmit      | BOOLEAN | Transmit flag                  |
| flag_update        | BOOLEAN | Update flag                    |

### Links Table
Stores connections between com object pins.

| Column    | Type    | Description                    |
|-----------|---------|--------------------------------|
| id        | INTEGER | Primary key (link_id)          |
| start_pin | INTEGER | Source pin identifier          |
| end_pin   | INTEGER | Destination pin identifier     |

## Event Types

### DeviceAdded
Emitted when a device is added from catalog or knxprod file.

```python
{
    "device_id": int,
    "address": str | None,
    "template_id": str,      # e.g., "switch_actuator" or "knxprod:M-123:A-456"
    "name": str,
    "parameters": [(param_id, value), ...],
    "com_objects": [{co_id, dpt_major, dpt_minor, flags...}, ...]
}
```

### DeviceRemoved
Emitted when a device is deleted. Stores full device state for undo.

### DeviceAddressChanged
Emitted when device individual address changes.

```python
{
    "device_id": int,
    "old_address": str | None,
    "new_address": str | None
}
```

### ParameterChanged
Emitted when a device parameter value changes.

```python
{
    "device_id": int,
    "param_id": str,
    "old_value": str,
    "new_value": str
}
```

### ComObjectDptChanged
Emitted when a com object's DPT is changed.

```python
{
    "device_id": int,
    "co_id": str,
    "old_dpt_major": int,
    "old_dpt_minor": int,
    "new_dpt_major": int,
    "new_dpt_minor": int
}
```

### ComObjectFlagChanged
Emitted when a com object flag is toggled.

```python
{
    "device_id": int,
    "co_id": str,
    "flag_name": str,        # "communication", "read", "write", "transmit", "update"
    "old_value": bool,
    "new_value": bool
}
```

### LinkCreated
Emitted when a link is created between two pins.

```python
{
    "link_id": int,
    "start_pin": int,
    "end_pin": int
}
```

### LinkRemoved
Emitted when a link is deleted.

## Event Sourcing Pattern

### Dual-Write Strategy
Each event both:
1. Appends to the events table (immutable log)
2. Updates the materialized state tables (devices, parameters, com_objects, links)

This provides:
- Fast reads from materialized state
- Full history for undo/redo
- No need to replay events on load

### Undo/Redo Implementation

The EventStore maintains a cursor pointing to the current position in history.

**Undo:**
1. Get event at cursor position
2. Call `event.revert(session)` to update materialized state
3. Mark event as `reverted=True`
4. Move cursor back to previous non-reverted event

**Redo:**
1. Find next reverted event after cursor
2. Call `event.apply(session)` to update materialized state
3. Mark event as `reverted=False`
4. Move cursor forward

**New Action After Undo:**
When a new event is appended while cursor is not at the end, all events after the cursor are deleted (branch is discarded).

## Migrations

Schema migrations use Alembic with auto-stamping:
- `create()` initializes schema and stamps as current head
- `open()` runs pending migrations on existing databases
- Migration files in `src/knx_gui/project/migrations/versions/`

## File Format

Project files use `.xknx` extension. They are standard SQLite3 databases that can be inspected with any SQLite tool:

```bash
sqlite3 project.xknx "SELECT type, data FROM events ORDER BY id;"
```

## Limitations

### knxprod Devices
Devices loaded from `.knxprod` files store `template_id` as `knxprod:{manufacturer}:{application}`. These devices cannot be reconstructed after undo/redo because the full template data is not stored in the database. The knxprod file must be reloaded.

### Template Changes
If a template in `DEVICE_TEMPLATES` is modified between sessions, devices using that template may not load correctly. Template versioning is not currently implemented.
