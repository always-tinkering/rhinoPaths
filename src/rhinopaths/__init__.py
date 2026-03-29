"""
rhinoPaths Rhino8: Native Python 3 parametric CAM algorithms for Rhino 8.

All modules are designed to be imported either fully headless (if mock geometry is passed)
or through RhinoCommon inside Grasshopper.
"""

from .geometry import (
    classify_curves,
    sort_by_containment,
    curve_to_polyline,
    polyline_to_curve,
    bounding_box,
)

from .offset import safe_offset, shrink_to_nothing
from .feedrate import feedrate, feedrate_for_arcs, recommended_chipload
from .dogbone import add_dogbones

__all__ = [
    "classify_curves",
    "sort_by_containment",
    "curve_to_polyline",
    "polyline_to_curve",
    "bounding_box",
    "safe_offset",
    "shrink_to_nothing",
    "feedrate",
    "feedrate_for_arcs",
    "recommended_chipload",
    "add_dogbones",
]
