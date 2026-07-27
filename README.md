# XKNX Toolkit

XKNX Toolkit is a desktop application and set of Python libraries for working with [KNX](https://www.knx.org/) home and building automation installations — browsing product catalogs, editing installation projects, and talking to real or simulated KNX devices.

![App overview](docs/screenshots/app-overview.png)
<!-- TODO: screenshot -->

## Features

### Node-based project editor

Devices and group addresses are laid out as nodes on a canvas. Communication objects are linked to group addresses by drawing a connection between them, with live datapoint-type (DPT) compatibility checks and warnings for lossy or ambiguous links. Every change (device edits, links, renames, address moves) is tracked in a full undo/redo history.

![Node editor](docs/screenshots/node-editor.png)
<!-- TODO: screenshot -->

### Project management

Devices are organized by area/line/segment, matching standard KNX topology. Each device's parameters, com object flags, load procedures, and raw memory layout can be inspected and edited directly.

![Project devices](docs/screenshots/project-devices.png)
<!-- TODO: screenshot -->

### Product catalog

Import `.knxprod` archives to build up a searchable catalog of manufacturers, hardware, and application programs, independent of any single project. Catalog entries can be dragged into a project as new devices.

![Catalog browser](docs/screenshots/catalog.png)
<!-- TODO: screenshot -->

### Real KNX connections

Connect to a real KNX interface over tunneling (TCP/UDP) or routing (multicast), with automatic gateway discovery or manual IP entry.

### Virtual devices and proxy — test without hardware

No KNX interface on hand? XKNX Toolkit can stand in for one:

- **Virtual Router** — simulates a KNX line over multicast routing, so other tools can discover and talk to it as if it were a real router.
- **Virtual Devices** — simulate individual KNX devices, including programming-mode scanning and serial-number-based addressing.
- **Proxy** — a minimal KNXnet/IP tunnelling server added manually as an interface, useful for inspecting or relaying traffic between a real connection and another client without a physical interface in the loop.

![Virtual testing](docs/screenshots/virtual-testing.png)
<!-- TODO: screenshot -->

### Network monitor and logs

Every KNX telegram crossing a connection, the virtual router, or the proxy can be recorded and inspected in the Network panel, alongside a structured, filterable log of what the application itself is doing.

![Network monitor](docs/screenshots/network.png)
<!-- TODO: screenshot -->

## Installation

Download the latest release for your platform from the [GitHub releases page](https://github.com/XKNX/xknxtoolkit/releases), or run from source (see below).

## Running from source

```bash
uv sync
uv run python -m knx_gui.main
```

## Packages

The application is built on a set of standalone, typed Python libraries (the `xknxmono` namespace) that can also be used independently of the GUI:

| Package | Import | Description |
|---------|--------|-------------|
| `xknx-models` | `xknxmono.models` | KNX XML schema bindings and version detection (foundation for the rest) |
| `xknx-product` | `xknxmono.product` | Reads and validates `.knxprod` product archives |
| `xknx-catalog` | `xknxmono.catalog` | Product catalog built from imported `.knxprod` archives |
| `xknx-project` | `xknxmono.project` | Project state management for KNX installations |
| `xknx-keyring` | `xknxmono.keyring` | Parses and serializes KNX keyring XML (KNX IP Secure keys) |

```bash
pip install xknx-models xknx-product xknx-catalog xknx-project xknx-keyring
```

## Development

```bash
uv sync                             # Install dependencies
uv run pytest                       # Run all tests
uv run pytest packages/models       # Run tests for a single package
uv run ruff check                   # Lint
uv run ruff format                  # Format
uv run pyright                      # Type check
```

See `CLAUDE.md` and `apps/knx-gui/CLAUDE.md` for architecture notes and repo conventions.

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
