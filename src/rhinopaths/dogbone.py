"""
Dogbone generator for rhinoPaths Rhino8.

Detects internal corners that would be rounded by a cylindrical CNC endmill,
and inserts external or along-path outward arcs so an inner part can snap
perfectly into place without manual corner filleting.
"""

def add_dogbones(curve, tool_radius, threshold_angle=89.0):
    """
    Given a closed polyline boundary curve, iterate through its vertices and
    insert outwards dogbones (arcs) at concave corners.

    Args:
        curve: Rhino.Geometry.Curve representing the boundary.
        tool_radius: float
        threshold_angle: float, internal angle threshold to consider (typically < 90).
        
    Returns:
        Modified Rhino.Geometry.Curve with dogbone arcs inserted at the corners.
    """
    # Steps:
    # 1. Deconstruct polyline into points.
    # 2. Walk points 1 to N-1 (handling wraparound).
    # 3. For each vertex B, form vector A->B and B->C.
    # 4. Check cross product for concavity (inside/outside routing context).
    # 5. Check dot product for angle severity.
    # 6. If concave and angle <= threshold, insert arc segment of radius = tool_radius.
    #    The center of the tool arc is positioned along the angle bisector vector,
    #    distance = tool_radius away from vertex B.
    # 7. Rebuild curve.
    pass
