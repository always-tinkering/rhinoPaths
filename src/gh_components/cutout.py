from ._bootstrap import COMMON_BOOTSTRAP

COMPONENT = {
    "name": "rhinoPaths Cutout",
    "nickname": "rpCutout",
    "description": "Profile toolpath — inside, outside, or on-line offset with climb/conventional direction.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("boundary", "Curve", "Outer boundary curve"),
        ("tool_diam", "float", "Tool diameter, mm"),
        ("side", "str", "Offset side: outside/inside/on"),
        ("climb", "bool", "True: climb, False: conventional"),
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Cutting depth, mm (negative)"),
        ("pass_depth", "float", "Max step-down per pass, mm"),
    ],
    "outputs": [
        ("toolpath", "List of Curves", "2D toolpath curves at cut side"),
        ("passes", "List of Curves", "3D toolpath curves at each Z level"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import cutout, pass_depths, apply_z

# Defaults
if tool_diam is None: tool_diam = 6.0
if side is None: side = "outside"
if climb is None: climb = True
if start_z is None: start_z = 0.0
if end_z is None: end_z = -18.0
if pass_depth is None: pass_depth = 6.0

toolpath = []
passes = []

try:
    if boundary:
        tol = 0.01
        pts = curve_to_polyline(boundary, tol)
        
        path_2d = cutout(pts, tool_diam, side, climb)
        
        if path_2d:
            toolpath = [polyline_to_curve(path_2d)]
            
            # Apply Z passes
            depths = pass_depths(start_z, end_z, pass_depth)
            passes_3d = apply_z(path_2d, depths)
            passes = [polyline_to_curve(p) for p in passes_3d]

except Exception as e:
    print(f"Error computing cutout: {e}")
    print(traceback.format_exc())
"""
}
