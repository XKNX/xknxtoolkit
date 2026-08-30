# XKNX Toolkit

> [!WARNING]
> **Alpha, experimental software.** XKNX Toolkit is not intended for end users and comes with no stability or safety guarantees — expect breaking changes, rough edges, and bugs. It's mostly useful for developers experimenting with the [xknx](https://github.com/XKNX/xknx) library. It can program real KNX devices (see below), but that path is experimental — always review the change set with a preflight first and keep a way to restore the device. No support is offered to end users. Contributions are welcome. Large parts of this project were built using LLMs.

XKNX Toolkit is a desktop application and set of Python libraries for working with [KNX](https://www.knx.org/) home and building automation installations — browsing product catalogs, editing installation projects, and talking to real or simulated KNX devices.

![App overview](assets/main.png)

## Features

### Node-based project editor

Devices and group addresses are laid out as nodes on a canvas. Communication objects are linked to group addresses by drawing a connection between them, with live datapoint-type (DPT) compatibility checks and warnings for lossy or ambiguous links. Every change (device edits, links, renames, address moves) is tracked in a full undo/redo history.

### Project management

Devices are organized by area/line/segment, matching standard KNX topology. Each device's parameters, com object flags, load procedures, and raw memory layout can be inspected and edited directly. Projects import from and export to ETS `.knxproj` archives: the export bundles the referenced manufacturer data (verbatim from the original `.knxprod` archives) and a merged `knx_master.xml`, so applications resolve from the archive alone. The project can be browsed like ETS through the device topology, the group address tree with assignments, and the building/space tree with functions.

### Product catalog

Import `.knxprod` archives to build up a searchable catalog of manufacturers, hardware, and application programs, independent of any single project. Catalog entries can be dragged into a project as new devices. The GUI also connects to the **KNX online catalog** (the same anonymous service ETS uses — no account, no license check on the service side) and can browse and refresh the manufacturer list, cached locally so it stays available offline; downloading the actual products from the online catalog is not implemented yet.

### Real KNX connections

Connect to a real KNX interface over tunneling (TCP/UDP) or routing (multicast), with automatic gateway discovery or manual IP entry.

### Programming real devices

The toolkit can commission a physical KNX device end-to-end — the job ETS does on "Download" — without ETS. It assembles the device's memory image from the product database and your parameter and group-address choices, then executes the application's Load Procedure over a live bus: driving each loadable part's Load State Machine, writing memory and properties, laying down the group communication tables, and restarting the device. It also programs a virgin device's individual address. A read-only **preflight** reads back every location a write would touch and shows the exact diff before anything is written. **Test Before Programming** runs that preflight and reports per memory segment and property whether the generated image matches what is already programmed on the device (with the current and planned bytes exportable as a report), guarding against writing a wrongly generated image. Programming requires a live connection; every connection-dependent action (test, program, sending frames) is refused with a visible "no KNX connection" notice when the bus is not linked. This is a vendor-independent implementation derived from the KNX Standard v3.0.0, verified on real hardware; it lives in the `xknx-download` package and can be used without the GUI.

### Virtual devices and proxy — test without hardware

No KNX interface on hand? XKNX Toolkit can stand in for one:

- **Virtual Router** — simulates a KNX line over multicast routing, so other tools can discover and talk to it as if it were a real router.
- **Virtual Devices** — simulate individual KNX devices, including programming-mode scanning and serial-number-based addressing.
- **Proxy** — a minimal KNXnet/IP tunnelling server added manually as an interface, useful for inspecting or relaying traffic between a real connection and another client without a physical interface in the loop.

### Network monitor and logs

Every KNX telegram crossing a connection, the virtual router, or the proxy can be recorded and inspected in the Network panel, alongside a structured, filterable log of what the application itself is doing.

## Installation

Only running from source is supported for now — this is developer-focused software, see below.

## Running from source

```bash
uv sync
uv run --package knx-gui python -m knx_gui.main
```

`knx-gui` is a workspace member that the root project does not depend on, so a plain `uv sync` does
not install it (or its `imgui-bundle` dependency). The `--package knx-gui` flag runs it in — and
installs it — from the workspace.

## Packages

The application is built on a set of standalone, typed Python libraries (the `xknxmono` namespace) that can also be used independently of the GUI:

| Package | Import | Description |
|---------|--------|-------------|
| `xknx-models` | `xknxmono.models` | KNX XML schema bindings and version detection (foundation for the rest) |
| `xknx-product` | `xknxmono.product` | Reads and validates `.knxprod` product archives |
| `xknx-catalog` | `xknxmono.catalog` | Product catalog built from imported `.knxprod` archives |
| `xknx-project` | `xknxmono.project` | Project state management for KNX installations |
| `xknx-keyring` | `xknxmono.keyring` | Parses and serializes KNX keyring XML (KNX IP Secure keys) |
| `xknx-download` | `xknxmono.download` | Programs applications and individual addresses into real KNX devices |

```bash
pip install xknx-models xknx-product xknx-catalog xknx-project xknx-keyring xknx-download
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

### Developing against a local xknx checkout

To test unreleased `xknx` library changes end-to-end in the GUI, point `apps/knx-gui` at a sibling checkout instead of the published package:

```bash
git clone https://github.com/XKNX/xknx ../xknx   # relative to xknxtoolkit/
```

Add a source override to `apps/knx-gui/pyproject.toml`:

```toml
[tool.uv.sources]
xknx = { path = "../../../xknx", editable = true }
```

Then re-lock:

```bash
uv lock
```

Revert both files (`git checkout apps/knx-gui/pyproject.toml uv.lock`) before committing, to go back to the published version.

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)
