"""
rhinoPaths — dogbone corner insertion.

Detects concave (reflex) corners in a closed polyline and inserts
outward semicircular arcs so a cylindrical endmill can reach the full
depth of an inside corner.

All geometry is in plain (x, y[, z]) tuples — no Rhino dependency.
The Rhino-specific wrapper that converts Curve ↔ polyline lives in
src/components/dogbone_component.py.
"""

import math
from .geometry import (
    sub2, add2, scale2, norm2, cross2, dot2,
    interior_angle_deg, is_concave_vertex,
)


def _arc_pts(center, radius, start_angle_rad, end_angle_rad, n_segments=8):
    """
    Sample points along a circular arc.

    Args:
        center:          (x, y)
        radius:          float
        start_angle_rad: float
        end_angle_rad:   float
        n_segments:      int — number of line segments to approximate the arc

    Returns:
        list of (x, y) — including start point, excluding end point
          (end point becomes the vertex of the *next* edge)
    """
    pts = []
    for i in range(n_segments + 1):
        t = i / n_segments
        angle = start_angle_rad + t * (end_angle_rad - start_angle_rad)
        pts.append((
            center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle),
        ))
    return pts


def _bisector_outward(prev_pt, vertex, next_pt):
    """
    Return a unit vector pointing outward (away from the polygon interior)
    along the angle bisector at *vertex*.

    The direction is chosen so the dogbone arc is cut into the corner,
    not into the part material.
    """
    u = norm2(sub2(prev_pt, vertex))
    v = norm2(sub2(next_pt, vertex))
    bis = add2(u, v)
    bis_len = math.hypot(*bis)
    if bis_len < 1e-10:
        # Degenerate (180° straight line) — pick a perpendicular
        perp = (-u[1], u[0])
        return perp
    bis = scale2(bis, 1.0 / bis_len)
    # Flip if the bisector points inward (towards the polygon interior)
    # The cross product of u→vertex with vertex→v tells us winding
    edge_u = sub2(vertex, prev_pt)
    edge_v = sub2(next_pt, vertex)
    if cross2(edge_u, edge_v) > 0:
        # CCW winding at a concave vertex — bisector naturally points inward; flip it
        bis = (-bis[0], -bis[1])
    return bis


def add_dogbones(polyline_pts, tool_radius, threshold_angle=89.0, n_arc_segments=8):
    """
    Insert dogbone arcs at concave corners of a closed polyline.

    Args:
        polyline_pts:    list of (x, y) or (x, y, z) tuples (closed or open — last
                         point need not equal first; closure is assumed)
        tool_radius:     float, mm — radius of the endmill
        threshold_angle: float, degrees — only insert dogbone when interior angle ≤ this
        n_arc_segments:  int — how many line segments approximate each arc

    Returns:
        list of (x, y[, z]) tuples representing the modified polyline
        with dogbone arcs inserted at qualifying concave corners.
    """
    pts = [pt2d(p) for p in polyline_pts]   # work in 2-D
    n = len(pts)
    result = []

    for i in range(n):
        prev_pt = pts[(i - 1) % n]
        vertex  = pts[i]
        next_pt = pts[(i + 1) % n]

        angle = interior_angle_deg(prev_pt, vertex, next_pt)
        concave = is_concave_vertex(prev_pt, vertex, next_pt, ccw=True)

        if concave and angle <= threshold_angle:
            # Place the arc centre along the bisector, at distance = tool_radius
            outward = _bisector_outward(prev_pt, vertex, next_pt)
            center = add2(vertex, scale2(outward, tool_radius))

            # Angles from center to the incoming and outgoing edge directions
            v_to_prev = sub2(prev_pt, center)
            v_to_next = sub2(next_pt, center)
            start_angle = math.atan2(v_to_prev[1], v_to_prev[0])
            end_angle   = math.atan2(v_to_next[1], v_to_next[0])

            # Always sweep the short way around (CW for a concave corner in CCW polygon)
            # Normalise so start > end (CW sweep)
            while end_angle >= start_angle:
                end_angle -= 2 * math.pi

            arc = _arc_pts(center, tool_radius, start_angle, end_angle, n_arc_segments)
            result.extend(arc)
        else:
            result.append(vertex)

    # Preserve original z if inputs had it
    has_z = len(polyline_pts[0]) > 2
    if has_z:
        z = polyline_pts[0][2]
        result = [(p[0], p[1], z) for p in result]

    return result


def pt2d(p):
    """Extract 2-D tuple from a 2- or 3-D point."""
    return (p[0], p[1])
