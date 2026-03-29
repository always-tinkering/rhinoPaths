"""
Drill Component — rhinoPaths Grasshopper node.

Inputs:
    circles    : [Curve]  — circle curves at drill locations
    start_z    : float    — retract / rapid Z height, mm
    end_z      : float    — drill depth, mm (negative)
    feedrate   : float    — plunge feedrate, mm/min

Outputs:
    centres    : [Point]  — drill point locations (GH Point3d)
    gcode      : str      — G-code drill cycle string
"""

import rhinopaths
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import drill
from rhinopaths.postprocessor import GCodePost

import Rhino.Geometry as rg

# ---- Input defaults ----
if start_z  is None: start_z  =  5.0
if end_z    is None: end_z    = -10.0
if feedrate is None: feedrate =  600.0

tol = 0.01

# ---- Convert circles → polylines → centres ----
circle_polys = [curve_to_polyline(c, tol) for c in (circles or [])]
centre_pts   = drill(circle_polys)

# ---- Convert centres to Rhino Point3d ----
centres = [rg.Point3d(p[0], p[1], p[2]) for p in centre_pts]

# ---- Generate G-code drill cycle ----
post = GCodePost()
lines = [post.rapid(x=p[0], y=p[1], z=start_z) +
         post.feed(x=p[0], y=p[1], z=end_z, f=feedrate) +
         post.rapid(x=p[0], y=p[1], z=start_z)
         for p in centre_pts]
gcode = "\n".join(lines)
