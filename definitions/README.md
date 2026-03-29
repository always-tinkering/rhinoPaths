# rhinoPaths Grasshopper Definition Assembly Guide

This document describes how to assemble the `rhinoPaths_v0.1.ghx` Grasshopper
canvas by hand, using the Script components in `src/components/`.

---

## Prerequisites

1. Run the **rhinoPaths Installer** component once to install dependencies.
2. Verify `import rhinopaths` succeeds in a blank GHPython component.

---

## Canvas Layout (left → right pipeline)

```
[INSTALL]   [FEEDRATE]
    ↓              ↓
[PASS DEPTHS]  [POSTPROCESSOR] ← [CUTOUT / POCKET / DRILL / ENGRAVE / DOGBONE]
                    ↓
              [GCODE PREVIEW]
                    ↓
              [FILE WRITE (Panel + Button)]
```

---

## Component-by-Component Setup

### 1. rhinoPaths Installer
- Script: `src/components/install_component.py`
- Inputs: *(none)*
- Outputs: `status` (string panel)
- **Run once on first use.** Wire a Button to force re-run.

### 2. Pass Depths
- Script: `src/components/pass_depths_component.py`
- Inputs: `start_z` (Number Slider, 0), `end_z` (Number Slider, −18), `pass_depth` (Number Slider, 6)
- Outputs: `depths` (Value List), `count` (Panel)

### 3. Feedrate Calculator
- Script: `src/components/feedrate_component.py`
- Inputs: `material` (Value List: plywood/hardwood/aluminum/acrylic/hdpe),
  `tool_diam` (Number Slider), `flutes` (Number Slider), `rpm` (Number Slider)
- Outputs: `feed_mm` (Panel), `feed_ipm` (Panel), `chipload_used` (Panel)

### 4. Cutout
- Script: `src/components/cutout_component.py`
- Inputs: `boundary` (Curve), `tool_diam`, `side` (Value List: outside/inside/on),
  `climb` (Boolean Toggle), `start_z`, `end_z`, `pass_depth`
- Outputs: `toolpath` (Curve), `passes` (Curve List)

### 5. Pocket
- Script: `src/components/pocket_component.py`
- Inputs: `boundary` (Curve), `islands` (Curve List, optional), `tool_diam`,
  `stepover`, `start_z`, `end_z`, `pass_depth`
- Outputs: `shells` (Curve List), `passes` (Curve List)

### 6. Drill
- Script: `src/components/drill_component.py`
- Inputs: `circles` (Curve List), `start_z`, `end_z`, `feedrate`
- Outputs: `centres` (Point List), `gcode` (Panel)

### 7. Engrave
- Script: `src/components/engrave_component.py`
- Inputs: `curves` (Curve List), `start_z`, `end_z`, `feedrate`
- Outputs: `sorted_curves` (Curve List), `passes` (Curve List)

### 8. Dogbone Maker
- Script: `src/components/dogbone_component.py`
- Inputs: `curves` (Curve List), `tool_diam`, `threshold` (Number Slider, 90),
  `n_segments` (Number Slider, 8)
- Outputs: `result_curves` (Curve List), `corner_count` (Panel)

### 9. G-code PostProcessor
- Script: `src/components/postprocessor_component.py`
- Inputs: `passes` (Curve List — from cutout/pocket/etc), `safe_z`, `feed_xy`,
  `feed_z`, `post_type` (Value List: gcode/shopbot), `file_path` (Panel, optional)
- Outputs: `gcode` (multiline Panel), `line_count` (Panel)

### 10. G-code Previewer
- Script: `src/components/gcode_previewer_component.py`
- Inputs: `gcode` (string from PostProcessor)
- Outputs: `rapid_moves` (Curve List — display in red), `feed_moves` (Curve List — display in cyan)

---

## Suggested GH Groups

| Group name | Components |
|---|---|
| **Setup** | Installer, Feedrate Calculator |
| **Operation** | Pass Depths + one of: Cutout / Pocket / Drill / Engrave |
| **Corner Treatment** | Dogbone Maker |
| **Output** | PostProcessor, File Write, G-code Previewer |

---

## Tips

- Wire `depths` from **Pass Depths** into the `pass_depth` input of Cutout or Pocket
  if you want visual depth control.
- Use a **Merge** component to combine curves from multiple operations before
  the PostProcessor (e.g. pocket shells + drill holes in one G-code file).
- The **G-code Previewer** rapid moves should be displayed in a contrasting
  colour (red) vs feed moves (cyan) using Rhino Display pipeline overrides.
