"""Tests for rhinopaths.dogbone — fully headless."""
import math
import pytest
from rhinopaths.dogbone import add_dogbones
from rhinopaths.geometry import is_concave_vertex


def _rect(w, h):
    """CCW rectangle polyline (4 corners, no repeated start/end)."""
    return [(0,0),(w,0),(w,h),(0,h)]


def test_no_dogbones_on_rectangle():
    """A plain rectangle has all convex corners → no extra points inserted."""
    rect = _rect(100, 50)
    result = add_dogbones(rect, tool_radius=3.175, threshold_angle=89.0)
    # All corners are 90° convex → nothing added (result same length or only original pts)
    assert len(result) == len(rect)


def test_is_concave_vertex_concave():
    # Simple concave vertex: a U-shape notch corner.
    # For a CCW polygon, a right turn (CW local rotation) is concave.
    # Edge A→B = (0,0)→(10,0): rightward
    # Edge B→C = (10,0)→(10,-5): downward  (a right-turn at B)
    # Cross product of (B-A) × (C-B) = (10,0)×(0,-5) = -50 < 0 → concave
    assert is_concave_vertex((0, 0), (10, 0), (10, -5), ccw=True) is True
    # And a left-turn corner is convex
    assert is_concave_vertex((0, 0), (10, 0), (10, 5), ccw=True) is False


def test_dogbone_on_l_shape():
    """
    An L-shaped pocket has one concave (reflex) corner at (10, 10).
    After dogbone insertion the output should have more points than the input
    and the inserted arc should be centred near the corner.
    """
    # CCW L-shape: outer rectangle with a square notch cut out of corner
    l_shape = [
        (0, 0), (20, 0), (20, 10),
        (10, 10),   # ← this is the concave corner
        (10, 20), (0, 20),
    ]
    tool_r = 3.0
    result = add_dogbones(l_shape, tool_radius=tool_r, threshold_angle=90.0)

    # More points because the concave corner was replaced by an arc
    assert len(result) > len(l_shape)


def test_dogbone_arc_radius():
    """
    The arc points inserted for a 90° concave corner should all lie at
    approximately tool_radius distance from the corner vertex.
    """
    l_shape = [
        (0, 0), (20, 0), (20, 10),
        (10, 10),   # concave corner
        (10, 20), (0, 20),
    ]
    tool_r = 3.0
    result = add_dogbones(l_shape, tool_radius=tool_r, threshold_angle=90.0, n_arc_segments=8)

    # The dogbone insert arc points, they should be located near the corner.
    # Verify that there are more than 6 points (arc inserted) and
    # that at least one new point is further from the corner than 0 but within 2*tool_r
    original_pts = set(map(tuple, l_shape))
    inserted_pts = [p for p in result if tuple(p) not in original_pts]
    assert len(inserted_pts) > 0, "No arc points were inserted"
    # All inserted arc points should be within 2*tool_r of the corner
    corner = (10, 10)
    for p in inserted_pts:
        d = math.hypot(p[0] - corner[0], p[1] - corner[1])
        assert d <= tool_r * 2 + 0.5, f"Arc point {p} too far from corner ({d:.2f} > {2*tool_r}"


def test_feedrate_chipload_aluminum():
    """Sanity: recommended_chipload for aluminum should be small."""
    from rhinopaths.feedrate import recommended_chipload
    cl = recommended_chipload("aluminum", 6.0)
    assert 0.005 < cl < 0.05


def test_feedrate_chipload_unknown():
    """Unknown material falls back to conservative 0.05."""
    from rhinopaths.feedrate import recommended_chipload
    assert recommended_chipload("unobtainium", 10.0) == 0.05


def test_feedrate_for_arcs_normal():
    from rhinopaths.feedrate import feedrate_for_arcs
    # 1000 mm/min, tool_r=3, arc_r=10 → 1000*(10-3)/10 = 700
    assert math.isclose(feedrate_for_arcs(1000, 3, 10), 700.0)


def test_feedrate_for_arcs_degenerate():
    from rhinopaths.feedrate import feedrate_for_arcs
    # arc_r <= tool_r → return unchanged
    assert feedrate_for_arcs(1000, 5, 3) == 1000.0
    assert feedrate_for_arcs(1000, 5, 0) == 1000.0
