"""
G-code PostProcessor Component — rhinoPaths Grasshopper node.

Takes 3D toolpath curves and emits G-code or ShopBot SBP.

Inputs:
    passes      : [Curve]  — ordered list of 3D toolpath curves (from cutout/pocket/etc)
    safe_z      : float    — rapid retract Z height, mm (default 5.0)
    feed_xy     : float    — XY cutting feedrate, mm/min
    feed_z      : float    — plunge feedrate, mm/min
    post_type   : str      — "gcode" (default) or "shopbot"
    file_path   : str      — optional: if set, write output to this path
    tolerance   : float    — curve sampling tolerance, mm (default 0.01)

Outputs:
    gcode       : str      — full G-code / SBP program as a string
    line_count  : int      — number of output lines
"""

from rhinopaths.geometry import curve_to_polyline
from rhinopaths.postprocessor import GCodePost, ShopBotPost
import os

# ---- Input defaults ----
if safe_z     is None: safe_z     = 5.0
if feed_xy    is None: feed_xy    = 3000.0
if feed_z     is None: feed_z     = 600.0
if post_type  is None: post_type  = "gcode"
if tolerance  is None: tolerance  = 0.01

# ---- Select post-processor ----
post = ShopBotPost() if post_type.lower() == "shopbot" else GCodePost()

# ---- Build program ----
lines = [post.header()]

prev_end = None
for curve in (passes or []):
    pts = curve_to_polyline(curve, tolerance)
    if not pts:
        continue

    start = pts[0]

    # Retract to safe Z, then rapid XY to start, then plunge
    lines.append(post.rapid(z=safe_z))
    lines.append(post.rapid(x=start[0], y=start[1]))
    lines.append(post.feed(z=start[2] if len(start) > 2 else 0.0, f=feed_z))

    # Cut through rest of path
    for pt in pts[1:]:
        z = pt[2] if len(pt) > 2 else start[2]
        lines.append(post.feed(x=pt[0], y=pt[1], z=z, f=feed_xy))

    prev_end = pts[-1]

# Final retract
lines.append(post.rapid(z=safe_z))
lines.append(post.footer())

gcode = "\n".join(l for l in lines if l)
line_count = gcode.count("\n") + 1

# ---- Optional file write ----
if file_path:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(gcode)
    except Exception as e:
        import sys
        print(f"rhinoPaths: could not write file: {e}", file=sys.stderr)
