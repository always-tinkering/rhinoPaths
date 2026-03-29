# rhinoPaths — Free, Open-Source CAM for Rhino 8

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

A free, open-source parametric CAM plugin for **Rhino 8 and Grasshopper**, designed to make CNC routing and milling accessible to designers, makerspaces, fab labs, and architecture schools worldwide.

Why pay thousands of dollars for proprietary CAM software when you can generate high-quality toolpaths directly inside Grasshopper for free?

---

## 🚀 Easy Installation

Using `rhinoPaths` is incredibly simple. You do not need to know how to code to use this plugin!

### Option 1: Rhino Package Manager (Recommended)
1. Open **Rhino 8**.
2. Type `PackageManager` in the Rhino command line and press Enter.
3. Search for **rhinoPaths**.
4. Click **Install**.
5. Restart Rhino. Open Grasshopper, and you will see the new **rhinoPaths** tab at the top of your screen!

### Option 2: Manual Installation (.yak file)
1. Download the latest `rhinoPaths-...yak` file from the [Releases](https://github.com/always-tinkering/rhinoPaths/releases) page.
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

---

## License

MIT — see [LICENSE](LICENSE). Free for personal, academic, and commercial use.
