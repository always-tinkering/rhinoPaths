"""
Dogbone Maker Component — rhinoPaths Grasshopper node.

Inserts dogbone reliefs at concave corners so a cylindrical endmill
can reach the full depth of inside pockets.

Inputs:
    curves      : [Curve]  — closed boundary curves to process
    tool_diam   : float    — endmill diameter, mm
    threshold   : float    — max corner angle to treat as concave (default 90°)
    n_segments  : int      — arc resolution (default 8 segments per arc)

Outputs:
    result_curves : [Curve]  — modified curves with dogbone arcs inserted
    corner_count  : int      — total number of dogbone arcs added
"""

import rhinopaths
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.dogbone import add_dogbones

# ---- Input defaults ----
if tool_diam  is None: tool_diam  = 6.0
if threshold  is None: threshold  = 90.0
if n_segments is None: n_segments = 8

tol = 0.01
tool_r = tool_diam / 2.0

result_curves = []
corner_count  = 0

for curve in (curves or []):
    pts = curve_to_polyline(curve, tol)
    original_len = len(pts)
    modified = add_dogbones(pts, tool_r, threshold_angle=threshold,
                            n_arc_segments=n_segments)
    result_curves.append(polyline_to_curve(modified))
    # Count how many arcs were inserted (each arc adds n_segments points)
    extra_pts = len(modified) - original_len
    if extra_pts > 0:
        corner_count += extra_pts // n_segments
