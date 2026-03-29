"""
Pocket Component — rhinoPaths Grasshopper node.

Inputs:
    boundary   : Curve    — outer pocket boundary
    islands    : [Curve]  — optional island curves (bosses to avoid)
    tool_diam  : float    — cutter diameter, mm
    stepover   : float    — 0.0–1.0 (fraction of tool_diam), default 0.5
    start_z    : float    — top of material, mm (default 0.0)
    end_z      : float    — pocket depth, mm (negative, e.g. -12.0)
    pass_depth : float    — max step-down per pass, mm (e.g. 6.0)

Outputs:
    shells     : [Curve]  — all toolpath shells (GH curve list)
    passes     : [Curve]  — shells duplicated for each Z level
    preview    : [Curve]  — flat list suitable for GH Preview
"""

import rhinopaths
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import pocket, pass_depths, apply_z

# ---- Input defaults ----
if tool_diam is None: tool_diam = 6.0
if stepover  is None: stepover  = 0.5
if start_z   is None: start_z   = 0.0
if end_z     is None: end_z     = -12.0
if pass_depth is None: pass_depth = 6.0

# ---- Convert Rhino curves → polylines ----
tol = 0.01  # document tolerance; tighten if needed
boundary_pts = curve_to_polyline(boundary, tol)
island_pts_list = [curve_to_polyline(c, tol) for c in (islands or [])]

# ---- Core algorithm (headless) ----
shells_2d = pocket(boundary_pts, island_pts_list, tool_diam, stepover)
depths    = pass_depths(start_z, end_z, pass_depth)
passes_3d = []
for shell in shells_2d:
    for z_pass in apply_z(shell, depths):
        passes_3d.append(z_pass)

# ---- Convert back to Rhino curves ----
shells  = [polyline_to_curve(s) for s in shells_2d]
passes  = [polyline_to_curve(p) for p in passes_3d]
preview = passes  # alias for GH pipeline preview
