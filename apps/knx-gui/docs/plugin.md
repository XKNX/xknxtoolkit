# Plugin Architecture

## Overview

The application uses a plugin-based architecture where functionality is organized into self-contained plugins. Each plugin owns its UI panels, handles its own state, and communicates with other plugins through a shared API and event bus.

## Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         PluginAPI                                │
│  Shared context passed to all plugins                            │
│                                                                  │
│  ├── project: ProjectService   (devices, links, persistence)    │
│  └── catalog: CatalogService   (device templates)               │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Plugin  │   │  Plugin  │   │  Plugin  │
        │ (panels) │   │ (panels) │   │ (panels) │
        └──────────┘   └──────────┘   └──────────┘
```

## Plugin Protocol

Every plugin implements the `Plugin` protocol:

```python
class Plugin(Protocol):
    name: str

    @property
    def panels(self) -> list[PanelDefinition]: ...
    def on_load(self) -> None: ...
    def on_unload(self) -> None: ...
```

## Panel Definition

Plugins declare their UI panels via `PanelDefinition`:

```python
@dataclass
class PanelDefinition:
    name: str                      # unique identifier
    label: str                     # display name (use S.PANEL_*)
    dock: str                      # dock space name
    render: Callable[[], None]     # render function
```

**Dock spaces:**
- `LeftSpace` - left sidebar (devices, catalog)
- `RightSpace` - right sidebar (configure, history)
- `BottomSpace` - bottom panel (telegrams)
- `MainDockSpace` - central area (node editor)

**Example:**

```python
class ProjectPlugin:
    def __init__(self, api: PluginAPI) -> None:
        self._devices_panel = DevicesPanel(...)
        self._configure_panel = ConfigurePanel(...)
        
        self._panels = [
            PanelDefinition(
                name="devices",
                label=S.PANEL_DEVICES,
                dock="LeftSpace",
                render=self._devices_panel.render,
            ),
            PanelDefinition(
                name="configure",
                label=S.PANEL_CONFIGURE,
                dock="RightSpace",
                render=self._configure_panel.render,
            ),
        ]

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels
```

## Services

### ProjectService

Manages project state (devices, links) and persistence.

```python
# State access
project.devices                    # list[Device]
project.links                      # list[tuple[link_id, start_pin, end_pin]]
project.selected_device            # Device | None (settable)

# State mutation
project.add_device_to_state(app, address) -> Device
project.add_link_to_state(start_pin, end_pin) -> int
project.remove_link_from_state(link_id)
project.set_flag(device, co_id, flag_name, new_value)
project.set_param(device, param_id, new_value)

# Persistence (writes to DB with event sourcing)
project.add_device(template_id, name, app, address) -> int
project.add_link(link_id, start_pin, end_pin)
project.remove_link(link_id, start_pin, end_pin)

# Undo/redo (auto-reloads from DB)
project.undo() -> bool
project.redo() -> bool
project.jump_to(event_id)

# Events (subscribe to state changes)
project.subscribe("device_selected", handler) -> unsubscribe_fn
```

**Events emitted by ProjectService:**

| Event | Args | Description |
|-------|------|-------------|
| `device_selected` | `device: Device \| None` | Selection changed |
| `flag_changed` | `device, co_id, flag_name, old, new` | Com object flag changed |
| `param_changed` | `device, param_id, old, new` | Parameter value changed |
| `link_added` | `link_id, start_pin, end_pin` | Link created |
| `link_removed` | `link_id, start_pin, end_pin` | Link deleted |

### CatalogService

Provides access to device templates from the catalog.

```python
catalog.get_entries() -> list[CatalogEntry]
catalog.get_application_xml(application_id) -> bytes | None
catalog.import_knxprod(path) -> list[str]  # returns added app IDs
```

## Current Plugins

| Plugin | Panels | Purpose |
|--------|--------|---------|
| `ProjectPlugin` | devices, configure, history | Device management, configuration, undo history |
| `NodeEditorPlugin` | node_editor | Visual node graph for linking com objects |
| `CatalogPlugin` | catalog | Browse and add devices from catalog |
| `TelegramsPlugin` | telegrams | KNX telegram monitoring |
| `ConnectionPlugin` | (none) | KNX connection status, menu rendering |

## Creating a New Plugin

1. Create plugin directory: `plugins/myplugin/`

2. Implement the plugin class:

```python
# plugins/myplugin/plugin.py
from knx_gui.plugins.base import PanelDefinition, PluginAPI
from knx_gui.strings import S

class MyPlugin:
    name = "myplugin"

    def __init__(self, api: PluginAPI) -> None:
        self._api = api
        self._panel = MyPanel(...)
        self._panels = [
            PanelDefinition(
                name="mypanel",
                label=S.PANEL_MYPANEL,
                dock="BottomSpace",
                render=self._panel.render,
            ),
        ]

    @property
    def panels(self) -> list[PanelDefinition]:
        return self._panels

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass
```

3. Export from `__init__.py`:

```python
# plugins/myplugin/__init__.py
from knx_gui.plugins.myplugin.plugin import MyPlugin

__all__ = ["MyPlugin"]
```

4. Register in `main.py`:

```python
self._myplugin = MyPlugin(self._plugin_api)
self._plugins.append(self._myplugin)
```

5. Create plugin strings with translations (see Translations section below)

## Dependencies Between Plugins

Plugins can depend on each other through the PluginAPI or by passing callbacks:

```python
# NodeEditorPlugin exposes method
class NodeEditorPlugin:
    def get_selected_node_ids(self) -> list[int]:
        return self._panel.get_selected_node_ids()

# ProjectPlugin uses it via callback injection
self._project_plugin = ProjectPlugin(
    self._plugin_api,
    get_selected_node_ids=self._node_editor_plugin.get_selected_node_ids,
)
```

This avoids circular imports while allowing cross-plugin coordination.

## Translations (i18n)

Each plugin manages its own translations using gettext.

### Plugin Structure

```
plugins/myplugin/
  plugin.py
  strings.py              # plugin strings
  locales/
    nl/LC_MESSAGES/
      myplugin.po         # Dutch translations source
      myplugin.mo         # compiled translations
```

### Creating strings.py

```python
from pathlib import Path
from knx_gui.strings import create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("myplugin", _locale_dir)

class MyPluginStrings:
    @property
    def PANEL_TITLE(self) -> str:
        return _("My Panel")

    @property
    def BTN_DO_THING(self) -> str:
        return _("Do Thing")

S = MyPluginStrings()
```

To inherit common strings (buttons like Add, Close, Cancel), extend `BaseStrings`:

```python
from knx_gui.strings import BaseStrings, create_translator

class MyPluginStrings(BaseStrings):
    # now has BTN_ADD, BTN_CLOSE, BTN_CANCEL, etc.
    ...
```

### Creating Translation Files

1. Create `.po` file at `locales/<lang>/LC_MESSAGES/<domain>.po`:

```
msgid "My Panel"
msgstr "Mijn Paneel"

msgid "Do Thing"
msgstr "Doe Ding"
```

2. Compile to `.mo`:

```bash
msgfmt -o myplugin.mo myplugin.po
```

### Language Detection

Language is detected from system locale at startup, falls back to English.
