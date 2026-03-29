"""
rhinoPaths — geometry utilities.

All functions in this module operate on plain Python tuples/lists of (x, y, z)
so they can be unit-tested without Rhino. At the GH wrapper boundary, Rhino
Point3d / Curve objects are converted to/from these plain types.

When running inside Rhino, helpers that need RhinoCommon are imported lazily
inside the functions that require them, so the module still loads headlessly.
"""

import math


# ---------------------------------------------------------------------------
# Point helpers  (operate on (x, y) or (x, y, z) tuples)
# ---------------------------------------------------------------------------

def pt2(p):
    """Return 2-D tuple from any (x, y[, z]) sequence."""
    return (p[0], p[1])


def dist2(a, b):
    """Euclidean distance between two 2-D points."""
    return math.hypot(b[0] - a[0], b[1] - a[1])


def sub2(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add2(a, b):
    return (a[0] + b[0], a[1] + b[1])


def scale2(v, s):
    return (v[0] * s, v[1] * s)


def norm2(v):
    """Normalise a 2-D vector; returns (0, 0) for zero-length vectors."""
    length = math.hypot(v[0], v[1])
    if length < 1e-12:
        return (0.0, 0.0)
    return (v[0] / length, v[1] / length)


def cross2(a, b):
    """2-D cross product (scalar z-component of 3-D cross)."""
    return a[0] * b[1] - a[1] * b[0]


def dot2(a, b):
    return a[0] * b[0] + a[1] * b[1]


def interior_angle_deg(prev_pt, vertex, next_pt):
    """
    Return interior angle (degrees) at *vertex* in the polyline prev→vertex→next.
    """
    u = sub2(prev_pt, vertex)
    v = sub2(next_pt, vertex)
    cos_a = dot2(u, v) / max(math.hypot(*u) * math.hypot(*v), 1e-12)
    cos_a = max(-1.0, min(1.0, cos_a))
    return math.degrees(math.acos(cos_a))


def is_concave_vertex(prev_pt, vertex, next_pt, ccw=True):
    """
    Return True if *vertex* is a concave (reflex) corner.

    For a CCW polygon, a *right* turn between successive edges is concave.
    The cross product of (prev→vertex) × (vertex→next) is negative for a right turn.
    """
    u = sub2(vertex, prev_pt)   # incoming edge direction
    v = sub2(next_pt, vertex)   # outgoing edge direction
    cross = cross2(u, v)
    # CCW polygon: right turn (cross < 0) → concave; left turn (cross > 0) → convex
    return cross < 0 if ccw else cross > 0


# ---------------------------------------------------------------------------
# Polyline helpers  (list of (x, y) or (x, y, z) tuples)
# ---------------------------------------------------------------------------

def polyline_length(pts):
    """Total arc length of a polyline."""
    return sum(dist2(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def polyline_area(pts):
    """
    Signed area of a closed 2-D polyline (shoelace formula).
    Positive → CCW, Negative → CW.
    """
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return area / 2.0


def is_ccw(pts):
    """Return True if the polyline winds counter-clockwise."""
    return polyline_area(pts) > 0


def point_in_polygon(pt, poly):
    """
    Ray-casting point-in-polygon test.

    Args:
        pt:   (x, y)
        poly: list of (x, y)  — closed or not (last edge auto-closed)

    Returns:
        bool
    """
    x, y = pt[0], pt[1]
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i][0], poly[i][1]
        xj, yj = poly[j][0], poly[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def bounding_box(pts_list):
    """
    Axis-aligned bounding box for one or more polylines.

    Args:
        pts_list: list of polylines, each a list of (x, y[, z])

    Returns:
        (min_x, min_y, max_x, max_y)
    """
    all_pts = [pt for poly in pts_list for pt in poly]
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------------------
# Containment / nesting
# ---------------------------------------------------------------------------

def classify_curves(polylines):
    """
    Classify a list of closed polylines into exterior boundaries and interior holes
    based on containment (inner curves nest inside outer ones).

    Uses a single representative point from each curve and tests it against
    all others with point_in_polygon.

    Args:
        polylines: list of closed polylines (each a list of (x, y) tuples)

    Returns:
        (exteriors, holes)  — each is a list of polylines
    """
    if not polylines:
        return [], []

    n = len(polylines)
    # Count how many other polylines contain each one
    container_count = [0] * n
    for i in range(n):
        rep = polylines[i][0]  # representative point
        for j in range(n):
            if i == j:
                continue
            if point_in_polygon(rep, polylines[j]):
                container_count[i] += 1

    # Even nesting depth → exterior, odd → hole
    exteriors = [polylines[i] for i in range(n) if container_count[i] % 2 == 0]
    holes = [polylines[i] for i in range(n) if container_count[i] % 2 == 1]
    return exteriors, holes


def sort_by_containment(polylines):
    """
    Return polylines sorted from deepest nesting level to shallowest.
    Useful for machining islands before their enclosing pockets.
    """
    n = len(polylines)
    container_count = []
    for i in range(n):
        rep = polylines[i][0]
        count = sum(
            1 for j in range(n) if i != j and point_in_polygon(rep, polylines[j])
        )
        container_count.append((count, i))
    container_count.sort(key=lambda x: -x[0])
    return [polylines[i] for _, i in container_count]


# ---------------------------------------------------------------------------
# Rhino-type conversion (lazy import — only available inside Rhino/GH)
# ---------------------------------------------------------------------------

def curve_to_polyline(rhino_curve, tolerance=0.01):
    """
    Discretise a Rhino NurbsCurve into a list of (x, y, z) tuples.

    Requires rhinoscriptsyntax / RhinoCommon to be available (i.e. inside Rhino).
    """
    try:
        import Rhino.Geometry as rg
        ok, polyline = rhino_curve.TryGetPolyline()
        if ok:
            return [(p.X, p.Y, p.Z) for p in polyline]
        # Fall back to chord-length discretisation
        pts = rhino_curve.DivideByLength(tolerance, True)
        if pts is None:
            pts = rhino_curve.DivideByCount(64, True)
        return [(rhino_curve.PointAt(t).X,
                 rhino_curve.PointAt(t).Y,
                 rhino_curve.PointAt(t).Z) for t in pts]
    except ImportError:
        raise RuntimeError("curve_to_polyline requires RhinoCommon (run inside Rhino).")


def polyline_to_curve(pts):
    """
    Rebuild a list of (x, y, z) tuples into a Rhino NurbsCurve (PolylineCurve).

    Requires RhinoCommon (run inside Rhino/GH).
    """
    try:
        import Rhino.Geometry as rg
        rhino_pts = [rg.Point3d(p[0], p[1], p[2] if len(p) > 2 else 0.0) for p in pts]
        return rg.PolylineCurve(rhino_pts)
    except ImportError:
        raise RuntimeError("polyline_to_curve requires RhinoCommon (run inside Rhino).")
