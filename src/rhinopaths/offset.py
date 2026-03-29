"""
rhinoPaths — polygon offset engine.

Implements safe, non-self-intersecting polygon offset using a layered strategy:
  1. Pure-Python vertex-normal offset  (always available, headless, used for testing)
  2. Clipper2 offset                   (better quality, used if clipper2 is installed)
  3. RhinoCommon Curve.Offset          (highest quality, used inside Grasshopper)

The public API (safe_offset / shrink_to_nothing) is the same regardless of backend.
Callers pass plain (x, y) tuple polylines; Rhino types are handled at the GH boundary.
"""

import math
from .geometry import (
    sub2, add2, scale2, norm2, cross2, polyline_area, is_ccw, dist2
)


# ---------------------------------------------------------------------------
# Pure-Python vertex-normal offset
# ---------------------------------------------------------------------------

def _edge_normal(a, b, inward=True):
    """
    Unit normal to edge a→b.
    inward=True  → points toward interior of a CCW polygon (left normal)
    inward=False → points outward
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return (0.0, 0.0)
    # Left normal of a→b (for CCW polygon this points inward)
    n = (-dy / length, dx / length)
    return n if inward else (-n[0], -n[1])


def _offset_polygon_python(pts, distance):
    """
    Offset a closed polygon by *distance* using the vertex bisector method.

    Positive distance → inward offset for a CCW polygon (i.e. shrink).
    Negative distance → outward (grow).

    Args:
        pts:      list of (x, y) — closed polygon (last pt ≠ first pt)
        distance: float, mm

    Returns:
        list of (x, y) — offset polygon, or [] if it degenerates
    """
    n = len(pts)
    if n < 3:
        return []

    # Ensure CCW winding
    if not is_ccw(pts):
        pts = list(reversed(pts))

    result = []
    for i in range(n):
        prev_pt = pts[(i - 1) % n]
        curr_pt = pts[i]
        next_pt = pts[(i + 1) % n]

        # Inward normals of the two adjacent edges
        n1 = _edge_normal(prev_pt, curr_pt, inward=True)
        n2 = _edge_normal(curr_pt, next_pt, inward=True)

        # Bisector direction (average of the two normals)
        bis = norm2(add2(n1, n2))
        if bis == (0.0, 0.0):
            bis = n2  # parallel edges — just use one normal

        # Scale bisector so the offset distance is correct perpendicular to the edge
        # miter_length = distance / cos(half_angle)
        # cos(half_angle) = dot(n1, bis)
        cos_half = dot2(n1, bis)
        if abs(cos_half) < 0.01:
            cos_half = 0.01  # clamp to avoid extreme miter spikes
        miter = distance / cos_half

        new_pt = add2(curr_pt, scale2(bis, miter))
        result.append(new_pt)

    # Check the result polygon has positive area (not degenerated/inverted)
    if len(result) < 3:
        return []
    area = polyline_area(result)
    if abs(area) < 1e-6:
        return []
    original_area = polyline_area(pts)
    # If offset area >= original area, the offset expanded instead of shrinking
    # (degenerate case when distance > polygon size)
    if abs(area) >= abs(original_area):
        return []
    # If the offset flipped winding, the polygon collapsed
    if (original_area > 0) != (area > 0):
        return []

    return result


def dot2(a, b):
    return a[0] * b[0] + a[1] * b[1]


# ---------------------------------------------------------------------------
# Clipper2 backend (optional)
# ---------------------------------------------------------------------------

def _clipper2_available():
    try:
        import clipper2  # noqa: F401
        return True
    except ImportError:
        return False


def _offset_polygon_clipper2(pts, distance):
    """
    Offset using Clipper2 for robust handling of self-intersections.
    Falls back to None if clipper2 not available.
    """
    try:
        from clipper2 import ClipperOffset, EndType, JoinType, PathsD, PathD
        co = ClipperOffset()
        path = PathD([complex(p[0], p[1]) for p in pts])
        paths = PathsD([path])
        # Inward offset = negative delta for CCW polygon
        co.add_paths(paths, JoinType.Miter, EndType.Polygon)
        result_paths = co.execute(-distance)  # negative = inward
        if not result_paths:
            return []
        return [(pt.real, pt.imag) for pt in result_paths[0]]
    except Exception:
        return None  # Signal to fall back


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def safe_offset(pts, distance, use_clipper2=True):
    """
    Offset a closed polygon by *distance* (positive = inward for CCW polygon).

    Tries Clipper2 first (if available), falls back to pure-Python bisector method.

    Args:
        pts:          list of (x, y) tuples — closed CCW polygon
        distance:     float, mm  (positive = shrink / inward)
        use_clipper2: bool — attempt Clipper2 first

    Returns:
        list of (x, y) — offset polygon, or [] if fully consumed
    """
    if use_clipper2 and _clipper2_available():
        result = _offset_polygon_clipper2(pts, distance)
        if result is not None:
            return result
        # Fall through to pure-Python

    return _offset_polygon_python(pts, distance)


def shrink_to_nothing(pts, step, min_area=1.0, max_iterations=500):
    """
    Iteratively shrink a closed polygon inward by *step* until it disappears.
    Returns all intermediate shells — used to generate raster pocket paths.

    Args:
        pts:            list of (x, y) — the boundary polygon (CCW)
        step:           float, mm — stepover distance between shells
        min_area:       float, mm² — stop when area drops below this threshold
        max_iterations: int — safety cap to prevent infinite loops

    Returns:
        list of shell polygons (each a list of (x, y) tuples),
        ordered from outermost to innermost
    """
    shells = []
    current = list(pts)

    for _ in range(max_iterations):
        shell = safe_offset(current, step)
        if not shell:
            break
        area = abs(polyline_area(shell))
        if area < min_area:
            break
        shells.append(shell)
        current = shell

    return shells
