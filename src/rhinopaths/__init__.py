"""
rhinoPaths: Native Python 3 parametric CAM algorithms for Rhino 8.

All modules are designed to be imported either fully headless (using plain
(x,y,z) tuple geometry) or through RhinoCommon inside Grasshopper.
"""

from .geometry import (
    classify_curves,
    sort_by_containment,
    curve_to_polyline,
    polyline_to_curve,
    bounding_box,
    interior_angle_deg,
    is_concave_vertex,
    point_in_polygon,
    is_ccw,
    polyline_area,
)

from .offset import safe_offset, shrink_to_nothing

from .toolpaths import (
    pass_depths,
    drill,
    engrave,
    cutout,
    pocket,
    apply_z,
)

from .dogbone import add_dogbones

from .feedrate import feedrate, feedrate_for_arcs, recommended_chipload

from .units import mm_to_inch, inch_to_mm, to_mm, to_inch, normalise

__all__ = [
    # geometry
    "classify_curves", "sort_by_containment", "curve_to_polyline",
    "polyline_to_curve", "bounding_box", "interior_angle_deg",
    "is_concave_vertex", "point_in_polygon", "is_ccw", "polyline_area",
    # offset
    "safe_offset", "shrink_to_nothing",
    # toolpaths
    "pass_depths", "drill", "engrave", "cutout", "pocket", "apply_z",
    # dogbone
    "add_dogbones",
    # feedrate
    "feedrate", "feedrate_for_arcs", "recommended_chipload",
    # units
    "mm_to_inch", "inch_to_mm", "to_mm", "to_inch", "normalise",
]
