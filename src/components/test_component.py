"""
rhinoPaths — Quick Test Component
Paste this into a Python 3 Script component in Rhino 8 Grasshopper.
No inputs needed — just run it to verify the install worked.

Output: status (connect to a Panel to see the result)
"""

import sys

try:
    import rhinopaths
    from rhinopaths import (
        pass_depths, feedrate, recommended_chipload,
        safe_offset, cutout, pocket
    )

    # Quick smoke test
    depths  = pass_depths(0.0, -18.0, 6.0)
    feed_mm = feedrate(6.0, 2, 18000, 0.05)
    sq      = [(0,0),(50,0),(50,50),(0,50)]
    shells  = pocket(sq, [], tool_diam=6.0)

    status = "\n".join([
        f"✅ rhinoPaths {rhinopaths.__version__ if hasattr(rhinopaths, '__version__') else '0.1.0'} loaded OK",
        f"   Python: {sys.version.split()[0]}",
        f"   pass_depths(0→-18, step=6): {depths}",
        f"   feedrate(6mm, 2fl, 18k rpm, 0.05cl): {feed_mm:.0f} mm/min",
        f"   pocket(50×50, Ø6mm): {len(shells)} shells",
    ])

except ImportError as e:
    status = f"❌ Import failed: {e}\n\nRun in terminal:\n  ~/.rhinocode/py39-rh8/bin/pip install -e ~/antigravity/scratch/opencam-rhino8"
except Exception as e:
    import traceback
    status = f"❌ Error: {e}\n{traceback.format_exc()}"

# In Rhino 8 Script Editor: add an output param named 'status'
print(status)
