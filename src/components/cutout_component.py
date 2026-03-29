"""
CUTOUT / PROFILE COMPONENT - Grasshopper Python 3 Node
Paste this code into a Python 3 component in Rhino 8.

Inputs:
    Curve (Rhino.Geometry.Curve) : Closed or open curve to cut
    ToolDiam (float) : Tool diameter in mm
    Side (str) : "outside", "inside", "on"
    Climb (bool) : True for climb, False for conventional
Outputs:
    Toolpaths (List of Rhino.Geometry.Curve) : Extracted toolpaths
"""

import sys as _sys, os as _os
_SRC = _os.path.normpath("/Users/angrym4macmini/antigravity/scratch/opencam-rhino8/src")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

try:
    import rhinopaths.toolpaths as tp
except ImportError:
    msg = "ERROR: Failed to import rhinopaths library. Did you run the installer component?"
    
def execute_cutout(curve, tool_diam, side, climb):
    # Map the high-level Python library function
    # Note: validation and exact parameter names match the GH interface names
    try:
        paths = tp.cutout(curve, tool_diam, side=side, climb=climb)
        return paths
    except Exception as e:
        return f"Error computing offset: {str(e)}"

# Input mapping from GH variables
if 'Curve' in globals() and Curve and 'ToolDiam' in globals() and ToolDiam:
    # Set defaults if side/climb unsupplied
    Side = Side if 'Side' in globals() and Side else "outside"
    Climb = Climb if 'Climb' in globals() and Climb is not None else True
    
    Toolpaths = execute_cutout(Curve, ToolDiam, Side, Climb)
