"""
Feedrate planning and calculations for rhinoPaths.

Chip-load based feedrate formula, material lookup table, and arc compensation.
"""

# ---------------------------------------------------------------------------
# Chipload lookup table: material → (min_mm_per_tooth, max_mm_per_tooth)
# ---------------------------------------------------------------------------
_CHIPLOAD_TABLE = {
    "mdf":      (0.030, 0.080),
    "plywood":  (0.040, 0.100),
    "hardwood": (0.030, 0.080),
    "softwood": (0.050, 0.130),
    "acrylic":  (0.020, 0.060),
    "hdpe":     (0.050, 0.150),
    "aluminum": (0.010, 0.040),
    "brass":    (0.008, 0.025),
    "foam":     (0.100, 0.300),
}

# Common aliases → canonical material key
_ALIASES = {
    "plywood": "plywood", "birch": "plywood",
    "mdf": "mdf",
    "hardwood": "hardwood", "oak": "hardwood", "maple": "hardwood", "walnut": "hardwood",
    "softwood": "softwood", "pine": "softwood",
    "acrylic": "acrylic", "perspex": "acrylic", "pmma": "acrylic",
    "hdpe": "hdpe", "polyethylene": "hdpe",
    "aluminum": "aluminum", "aluminium": "aluminum", "al": "aluminum",
    "brass": "brass",
    "foam": "foam", "xps": "foam", "eps": "foam",
}


def recommended_chipload(material_name, tool_diam):
    """
    Return recommended chipload (mm/tooth) for a material and tool diameter.

    Scales linearly within the safe range:
      6 mm tool → lower bound,  25 mm tool → upper bound.

    Args:
        material_name: str  e.g. "plywood", "aluminum"
        tool_diam:     float, mm

    Returns:
        float: chipload in mm per tooth
    """
    key = _ALIASES.get(material_name.lower().strip())
    if key is None:
        return 0.05  # conservative fallback

    lo, hi = _CHIPLOAD_TABLE[key]
    t = max(0.0, min(1.0, (tool_diam - 6.0) / 19.0))
    return round(lo + t * (hi - lo), 4)


def feedrate(tool_diam, flutes, rpm, chipload):
    """
    Calculate linear feedrate in mm/min.

    Formula: F = RPM × flutes × chipload

    Args:
        tool_diam: float, mm  (kept for API symmetry; not used in formula)
        flutes:    int
        rpm:       float, rev/min
        chipload:  float, mm/tooth

    Returns:
        float: mm/min
    """
    return float(rpm) * int(flutes) * float(chipload)


def feedrate_for_arcs(linear_feedrate, tool_r, arc_r):
    """
    Compensate feedrate for internal circular arc moves.

    The tool centre travels on a smaller radius than the cutting edge;
    this reduces the programmed rate so the chip-load stays constant.

        F_arc = F_linear × (arc_r − tool_r) / arc_r

    Args:
        linear_feedrate: float, mm/min
        tool_r:          float, tool radius (mm)
        arc_r:           float, arc toolpath radius (mm)

    Returns:
        float: compensated feedrate mm/min
               (returns linear_feedrate unchanged for degenerate inputs)
    """
    if arc_r <= 0 or arc_r <= tool_r:
        return float(linear_feedrate)
    return round(float(linear_feedrate) * (arc_r - tool_r) / arc_r, 2)
