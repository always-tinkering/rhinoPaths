"""
Feedrate Calculator Component — rhinoPaths Grasshopper node.

Calculates optimal feedrate and spindle speed from tool/material parameters.

Inputs:
    material   : str    — material name (e.g. "plywood", "aluminum", "acrylic")
    tool_diam  : float  — cutter diameter, mm
    flutes     : int    — number of cutting flutes
    rpm        : float  — spindle speed, rev/min
    chipload   : float  — override chipload, mm/tooth (optional; auto if None)
    arc_radius : float  — arc radius for internal arc compensation (optional)

Outputs:
    feed_mm    : float  — linear feedrate, mm/min
    feed_ipm   : float  — linear feedrate, inches/min
    chipload_used : float — actual chipload used, mm/tooth
    arc_feed   : float  — compensated feedrate for internal arcs, mm/min
"""

from rhinopaths.feedrate import (
    recommended_chipload, feedrate as calc_feedrate, feedrate_for_arcs
)
from rhinopaths.units import mm_to_inch

# ---- Input defaults ----
if material   is None: material   = "plywood"
if tool_diam  is None: tool_diam  = 6.0
if flutes     is None: flutes     = 2
if rpm        is None: rpm        = 18000.0

# ---- Resolve chipload ----
if chipload is None or chipload <= 0:
    chipload_used = recommended_chipload(material, tool_diam)
else:
    chipload_used = float(chipload)

# ---- Calculate feedrates ----
feed_mm  = calc_feedrate(tool_diam, flutes, rpm, chipload_used)
feed_ipm = mm_to_inch(feed_mm)

# ---- Arc compensation ----
if arc_radius is not None and arc_radius > 0:
    arc_feed = feedrate_for_arcs(feed_mm, tool_diam / 2.0, arc_radius)
else:
    arc_feed = feed_mm
