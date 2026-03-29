# rhinoPaths — Open-Source CAM for Rhino 8

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

A free, open-source parametric CAM plugin for **Rhino 8 / Grasshopper 1**, filling the only serious gap in the Rhino ecosystem. RhinoCAM charges $1,500–$2,500 for what should be accessible to makerspaces, fab labs, and architecture schools worldwide.

---

## Features (Phase 1 — 2.5-axis)

| Operation | Status |
|-----------|--------|
| Profile / Cutout | 🚧 In progress |
| Raster Pocket | 🚧 In progress |
| Drill | 🚧 In progress |
| Engrave | 🚧 In progress |
| Dogbone corners | 🚧 In progress |
| G-code output (Fanuc/GRBL) | ✅ Working |
| ShopBot `.sbp` output | ✅ Working |
| Feedrate calculator | ✅ Working |
| Automated GH installer | ✅ Working |

---

## Architecture

```
rhinopaths/
├── src/rhinopaths/         # Core Python 3 algorithm library (headless, pip-installable)
│   ├── geometry.py         # Curve utilities, containment, polyline conversion
│   ├── offset.py           # Safe non-self-intersecting offset (RhinoCommon + Clipper2)
│   ├── toolpaths.py        # 2.5-axis CAM operations
│   ├── dogbone.py          # Concave corner arc insertion
│   ├── feedrate.py         # Chipload-based feedrate calculator
│   ├── postprocessor.py    # G-code + ShopBot post-processor
│   └── units.py            # mm/inch conversion helpers
├── src/components/         # Thin Grasshopper Python 3 Script wrapper components
│   ├── install_component.py  # Run once to install dependencies
│   └── cutout_component.py
├── definitions/            # Grasshopper definitions (.ghx) and template files
├── examples/               # Sample Rhino geometry for testing
└── tests/                  # Headless pytest suite (no Rhino required)
```

**Key design principle:** All algorithm logic lives in the `rhinopaths` Python package. Grasshopper components are thin wrappers that collect inputs, call library functions, and return geometry. This means the library is fully unit-testable without Rhino.

---

## Getting Started

### Prerequisites
- Rhino 8 (with Grasshopper 1)
- Git

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/opencam-rhino8.git
   ```

2. Open `definitions/OpenCAM_v0.1.ghx` in Rhino 8 / Grasshopper.

3. Find the **Installer** component, set its `RunInstall` toggle to `True`. This will automatically:
   - Install `clipper2` from PyPI into Rhino's Python environment
   - Install the `rhinopaths` package via `pip install -e .`

4. You're ready. All other components can now `import rhinopaths` cleanly.

### Running Tests (no Rhino needed)

```bash
cd opencam-rhino8
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Contributing

Pull requests welcome. See the [Build Checklist](docs/CHECKLIST.md) for current status and open tasks.

## License

MIT — see [LICENSE](LICENSE).
