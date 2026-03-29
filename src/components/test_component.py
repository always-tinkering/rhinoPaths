"""
rhinoPaths — Quick Test Component
Paste into a Python 3 Script component in Rhino 8 Grasshopper.
No inputs needed — just run it to verify the install worked.
"""

import sys, os

# ── Path bootstrap ─────────────────────────────────────────────────────────
# Adds the rhinopaths src directory to sys.path so the import works
# regardless of how pip was invoked.
_SRC = "/Users/angrym4macmini/antigravity/scratch/opencam-rhino8/src"
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# Also try the ~/.rhinocode site-packages (where pip installed to)
_RHINO_SITE = os.path.expanduser(
    "~/.rhinocode/py39-rh8/lib/python3.9/site-packages"
)
if os.path.exists(_RHINO_SITE) and _RHINO_SITE not in sys.path:
    sys.path.insert(0, _RHINO_SITE)
# ───────────────────────────────────────────────────────────────────────────

try:
    import rhinopaths
    from rhinopaths import (
        pass_depths, feedrate, recommended_chipload,
        safe_offset, cutout, pocket
    )

    depths  = pass_depths(0.0, -18.0, 6.0)
    feed_mm = feedrate(6.0, 2, 18000, 0.05)
    sq      = [(0,0),(50,0),(50,50),(0,50)]
    shells  = pocket(sq, [], tool_diam=6.0)

    status = "\n".join([
        f"✅ rhinoPaths loaded OK",
        f"   Python: {sys.version.split()[0]}",
        f"   sys.path includes src: {_SRC in sys.path}",
        f"   pass_depths(0→-18, step=6): {depths}",
        f"   feedrate(Ø6mm, 2fl, 18k, 0.05cl): {feed_mm:.0f} mm/min",
        f"   pocket(50×50mm, Ø6mm): {len(shells)} shells",
    ])

except ImportError as e:
    status = "\n".join([
        f"❌ Import failed: {e}",
        f"",
        f"sys.path searched:",
        *[f"   {p}" for p in sys.path[:8]],
    ])
except Exception as e:
    import traceback
    status = f"❌ Runtime error: {e}\n{traceback.format_exc()}"

print(status)
