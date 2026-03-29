"""
Engrave Component — rhinoPaths Grasshopper node.

Inputs:
    curves     : [Curve]  — curves to engrave (follow on-surface)
    start_z    : float    — safe Z height, mm
    end_z      : float    — engraving depth, mm (negative, e.g. -0.5)
    feedrate   : float    — cutting feedrate, mm/min
    plunge_f   : float    — plunge feedrate, mm/min

Outputs:
    sorted_curves : [Curve]  — curves reordered for minimum air travel
    passes        : [Curve]  — 3D curves at engraving depth
    gcode         : str      — G-code output string
"""

import sys as _sys, os as _os
_SRC = _os.path.normpath("/Users/angrym4macmini/antigravity/scratch/opencam-rhino8/src")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

import rhinopaths
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import engrave
from rhinopaths.postprocessor import GCodePost

# ---- Input defaults ----
if start_z  is None: start_z  =  5.0
if end_z    is None: end_z    = -0.5
if feedrate is None: feedrate =  1200.0
if plunge_f is None: plunge_f =  300.0

tol = 0.01

# ---- Convert and sort curves ----
polys = [curve_to_polyline(c, tol) for c in (curves or [])]
sorted_polys = engrave(polys)

# ---- Build 3D passes at engraving depth ----
passes_3d = [[(p[0], p[1], end_z) for p in poly] for poly in sorted_polys]

# ---- Convert back to Rhino curves ----
sorted_curves = [polyline_to_curve(s) for s in sorted_polys]
passes        = [polyline_to_curve(p) for p in passes_3d]

# ---- G-code output ----
post = GCodePost()
lines = []
for poly in passes_3d:
    if not poly: continue
    lines.append(post.rapid(z=start_z))
    lines.append(post.rapid(x=poly[0][0], y=poly[0][1]))
    lines.append(post.feed(z=end_z, f=plunge_f))
    for pt in poly[1:]:
        lines.append(post.feed(x=pt[0], y=pt[1], f=feedrate))
    lines.append(post.rapid(z=start_z))
gcode = "\n".join(lines)
