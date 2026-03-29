# rhinoPaths — Free, Open-Source CAM for Rhino 8

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

A free, open-source parametric CAM plugin for **Rhino 8 and Grasshopper**, designed to make CNC routing and milling accessible to designers, makerspaces, fab labs, and architecture schools worldwide.

Why pay thousands of dollars for proprietary CAM software when you can generate high-quality toolpaths directly inside Grasshopper for free?

---

## 🚀 Easy Installation

Using `rhinoPaths` is incredibly simple. You do not need to know how to code to use this plugin!

### Option 1: Rhino Package Manager (Coming Soon!)
*Currently in Alpha. Once v1.0 is published, you will be able to install via:*
1. Open **Rhino 8**.
2. Type `PackageManager` in the Rhino command line and press Enter.
3. Search for **rhinoPaths**.
4. Click **Install**.
5. Restart Rhino. Open Grasshopper, and you will see the new **rhinoPaths** tab at the top of your screen!

### Option 2: Manual Installation (Alpha Users)
1. Download the latest `rhinoPaths-...yak` file from the [Releases](https://github.com/always-tinkering/rhinoPaths/releases) page. (Or build it yourself locally).
2. Open **Rhino 8**.
3. Drag and drop the `.yak` file directly into the open Rhino 8 viewport.
4. Rhino will install the package automatically. Restart Rhino.
5. Open Grasshopper to access the **rhinoPaths** components.

---

## 🛠️ Features (2.5-Axis Milling)

Simply drag and drop these components onto your Grasshopper canvas to start generating G-Code for your CNC router!

| Operation | Description | Status |
|-----------|-------------|--------|
| **Cutout / Profile** | Cut outside, inside, or exactly on a line. Supports climb/conventional milling and multi-pass depth cuts. | ✅ Working |
| **Raster Pocket** | Hollow out shapes with concentric toolpaths. Supports island avoidance and custom stepovers. | ✅ Working |
| **Drill** | Automatically extract hole centers from circles and generate drill cycles. | ✅ Working |
| **Engrave** | Follow open curves for V-carving or standard engraving. | ✅ Working |
| **Dogbone Corners** | Automatically insert circular reliefs into sharp inside corners so parts fit together perfectly after CNC cutting. | ✅ Working |
| **Feedrate Calculator** | Automatically dial in your feeds and speeds based on your tool diameter, flutes, and desired chip load. | ✅ Working |
| **Post-Processor** | Export your toolpaths! Includes built-in support for standard standard `G-code` (.nc) and ShopBot (`.sbp`). | ✅ Working |
| **G-Code Previewer** | Read G-Code back into Grasshopper to visualize and verify the exact generated toolpaths (red for rapid travel, blue for cutting). | ✅ Working |

---

## 📏 Standardized CAM Parameters

rhinoPaths embraces industry-standard CAM terminology and hobbyist-friendly defaults to provide an intuitive experience out of the box:
* **`stepdown`**: The maximum depth the tool will cut per pass (formerly pass_depth). Defaults to `3.175 mm` (1/8").
* **`clearance_height`**: Safety retract height between cuts to clear clamps and material (formerly safe_z). Defaults to `12.7 mm` (1/2").
* **`stepover`**: Percentage of the tool diameter to move sideways during pocketing routines. Defaults to `0.4` (40%).
* **Default Tool**: Pre-configured for a typical `6.35 mm` (1/4") end mill.
* **Default Stock**: Pre-configured for `19.05 mm` (3/4") material.

---

## 👩‍💻 For Developers & Contributors

`rhinoPaths` is built natively for Rhino 8's new CPython 3 architecture. 
* All heavy-lifting algorithms (offsets, toolpath logic, post-processors) live in a headless, unit-testable Python library (`src/rhinopaths/`).
* The Grasshopper components are lightweight UI wrappers generated programmatically into a `.yak` package.

### Building the Plugin Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/always-tinkering/rhinoPaths.git
   ```
2. (Optional) Run the headless Python test suite:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   pytest tests/ -v
   ```
3. To package the Grasshopper plugin, run the build script (Mac/Linux):
   ```bash
   ./build.sh
   ```
   *Note: This utilizes the `rhinocode` CLI to bundle the `.rhproj` file into a distributable `.yak` file found in the `/build` folder. Make sure Rhino 8's Script Server is running.*

### Agent-Driven Debugging (MCP)
To enable AI-assisted debugging and integration testing with tools like Cursor or Claude Desktop, you can configure community **Model Context Protocol (MCP)** servers:
1. Install [RhinoMCP](https://github.com/jingcheng-chen/rhinomcp) to allow AI agents to execute Python scripts inside a living Rhino document.
2. Install [Grasshopper MCP Bridge](https://github.com/alfredatnycu/grasshopper-mcp) as a `GH_MCP.gha` plugin to allow AI agents to instantiate and wire `rhinoPaths` components automatically on a live Grasshopper canvas.
3. Test geometries and fixtures can be accessed by the MCP servers via the `tests/fixtures/` directory. (Note: Ensure Rhino GUI is running when using MCP tools.)

---

## License

MIT — see [LICENSE](LICENSE). Free for personal, academic, and commercial use.
