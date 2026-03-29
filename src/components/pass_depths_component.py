"""
Pass Depths Component — rhinoPaths Grasshopper node.

Generates a list of Z cutting depths for multi-pass operations.

Inputs:
    start_z    : float    — top of material (default 0.0)
    end_z      : float    — target depth, mm negative (e.g. -18.0)
    pass_depth : float    — maximum step-down per pass (e.g. 6.0)

Outputs:
    depths     : [float]  — list of Z values, e.g. [-6.0, -12.0, -18.0]
    count      : int      — number of passes
"""

from rhinopaths.toolpaths import pass_depths as _pass_depths

# ---- Input defaults ----
if start_z    is None: start_z    =  0.0
if end_z      is None: end_z      = -18.0
if pass_depth is None: pass_depth =  6.0

depths = _pass_depths(start_z, end_z, pass_depth)
count  = len(depths)
