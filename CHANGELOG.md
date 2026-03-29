# Changelog

All notable changes to **rhinoPaths** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — Phase 2

### Planned
- Clipper2 integration for robust polygon offset (replaces vertex-normal approximation)
- 3-axis surface finish (iso-curve) pass generation
- Horizontal roughing from mesh
- Adaptive / HSM trochoidal pocket
- Machining time estimator
- Configurable post-processor templates (YAML)
- Food4Rhino listing + Yak package manifest

---

## [0.1.0] — 2026-03-29 — Phase 1 Complete

### Added

**Core library (`src/rhinopaths/`)**
- `geometry.py` — headless polygon math: point helpers, polyline area/CCW check,
  point-in-polygon (ray casting), bounding box, containment classification
  (`classify_curves`, `sort_by_containment`), interior angle, concave vertex
  detection, lazy RhinoCommon conversion helpers
- `offset.py` — vertex-normal inward polygon offset engine; `safe_offset()`
  with Clipper2 hook (falls back to pure Python); `shrink_to_nothing()` shell
  generator with max-iterations safety guard; degeneration detection (area ratio
  + winding flip checks)
- `toolpaths.py` — 2.5-axis operations:
  - `pass_depths()` — multi-pass Z depth list
  - `drill()` — centroid extraction from circle polylines
  - `engrave()` — nearest-neighbour curve ordering
  - `cutout()` — profile toolpath (inside / outside / on, climb / conventional)
  - `pocket()` — concentric shell raster pocket with island avoidance and
    bounding-box early-exit guard
  - `apply_z()` — extrude 2D toolpath to 3D multi-pass list
- `dogbone.py` — concave corner detection (CCW cross-product winding),
  bisector arc insertion (polyline approximation, configurable segments)
- `feedrate.py` — chipload table (9 materials + aliases), `feedrate()` formula,
  `feedrate_for_arcs()` arc compensation, `recommended_chipload()` lookup
- `postprocessor.py` — full rewrite:
  - `GCodePost` — keyword-axis move API (G0/G1/G2/G3), feedrate modal suppression,
    tab insertion (`tabs()`), helical ramp entry (`ramp_entry()`),
    header/footer (G90/G21/M3/M5/M30)
  - `ShopBotPost` — SBP dialect (J3/M3/SA/MS/C6/C7)
  - Backwards-compatible `GCodePostProcessor` / `ShopBotPostProcessor` aliases
- `units.py` — mm/inch conversion, normalise helper
- `__init__.py` — full public API export of all modules

**Grasshopper components (`src/components/`)**
- `install_component.py` — zero-setup pip + editable install of rhinoPaths
- `cutout_component.py` — profile/cutout + multi-Z passes
- `pocket_component.py` — concentric pocket + multi-Z passes
- `drill_component.py` — circle curves → drill centres + G-code drill cycle
- `engrave_component.py` — nearest-neighbour sort + full G-code
- `dogbone_component.py` — per-curve dogbone arc insertion with count output
- `pass_depths_component.py` — Z depth list generator
- `feedrate_component.py` — chipload lookup + feedrate + arc compensation
- `postprocessor_component.py` — ordered curve list → G-code / ShopBot file
- `gcode_previewer_component.py` — G-code parser → Rhino rapid/feed geometry

**Documentation & tooling**
- `definitions/README.md` — Grasshopper canvas assembly guide (inputs, outputs,
  wiring tips, suggested group layout)
- `scripts/create_template_3dm.py` — Rhino script to generate standard CNC
  template with 8 pre-configured layers (BOUNDARY, TOOLPATH, ISLANDS, HOLES,
  ENGRAVE, DOGBONE, STOCK, OUTPUT)
- `README.md` — project overview, installation, quick-start
- `LICENSE` — MIT
- `pyproject.toml` — setuptools src-layout, dev extras (pytest, numpy)

**Tests** — 64 tests, all passing in < 0.05 s
- `test_geometry.py` (15) — point math, containment, angles, winding
- `test_dogbone.py` (8) — corner detection, arc insertion
- `test_feedrate.py` (2) — basic feedrate formula
- `test_postprocessor.py` (22) — all move types, modal feedrate, tabs, ramps,
  ShopBot dialect, header/footer
- `test_toolpaths.py` (17) — pass_depths, drill, engrave, apply_z,
  safe_offset, shrink_to_nothing, cutout, pocket
