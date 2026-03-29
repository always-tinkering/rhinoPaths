"""
G-code Previewer Component — rhinoPaths Grasshopper node.

Parses a G-code string and reconstructs the toolpath as Rhino geometry
for visual preview inside Grasshopper. Supports G0, G1 linear moves.

Inputs:
    gcode       : str     — G-code program string
    rapid_color : Colour  — display colour for rapid moves (optional)
    feed_color  : Colour  — display colour for feed moves (optional)

Outputs:
    rapid_moves : [Line]  — G0 rapid move segments
    feed_moves  : [Line]  — G1 cutting move segments
    positions   : [Point] — all visited XYZ positions
    bounds      : Box     — bounding box of the toolpath
"""

import sys as _sys, os as _os
_SRC = _os.path.normpath("/Users/angrym4macmini/antigravity/scratch/opencam-rhino8/src")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

import re
import Rhino.Geometry as rg

def _parse_gcode(gcode_str):
    """Parse G-code lines into a sequence of (mode, x, y, z) tuples."""
    moves = []
    x = y = z = 0.0
    mode = "G0"  # start in rapid mode
    for raw_line in (gcode_str or "").splitlines():
        line = raw_line.split(";")[0].strip().upper()  # strip comments
        if not line:
            continue
        if "G0" in line or "G00" in line:
            mode = "G0"
        elif "G1" in line or "G01" in line:
            mode = "G1"
        for axis, pattern in [("X", r"X([-\d.]+)"), ("Y", r"Y([-\d.]+)"), ("Z", r"Z([-\d.]+)")]:
            m = re.search(pattern, line)
            if m:
                val = float(m.group(1))
                if axis == "X": x = val
                elif axis == "Y": y = val
                elif axis == "Z": z = val
        moves.append((mode, x, y, z))
    return moves

# ---- Parse G-code ----
moves = _parse_gcode(gcode)

rapid_moves = []
feed_moves  = []
positions   = []
prev = None

for (mode, x, y, z) in moves:
    curr_pt = rg.Point3d(x, y, z)
    positions.append(curr_pt)
    if prev is not None:
        seg = rg.LineCurve(prev, curr_pt)
        if mode == "G0":
            rapid_moves.append(seg)
        else:
            feed_moves.append(seg)
    prev = curr_pt

# ---- Bounding box ----
all_pts = [rg.Point3d(m[1], m[2], m[3]) for m in moves] if moves else []
if all_pts:
    bb = rg.BoundingBox(all_pts)
    bounds = rg.Box(bb)
else:
    bounds = None
