"""Tests for rhinopaths.geometry — fully headless."""
import math
import pytest
from rhinopaths.geometry import (
    dist2, polyline_area, is_ccw, point_in_polygon,
    bounding_box, classify_curves, sort_by_containment,
    interior_angle_deg, is_concave_vertex,
)

# --- basic point math ---

def test_dist2():
    assert math.isclose(dist2((0, 0), (3, 4)), 5.0)

def test_polyline_area_square():
    # 10×10 CCW square → area = 100
    sq = [(0,0),(10,0),(10,10),(0,10)]
    assert math.isclose(polyline_area(sq), 100.0)

def test_polyline_area_cw_negative():
    sq = [(0,0),(0,10),(10,10),(10,0)]
    assert polyline_area(sq) < 0

def test_is_ccw():
    ccw = [(0,0),(10,0),(10,10),(0,10)]
    cw  = [(0,0),(0,10),(10,10),(10,0)]
    assert is_ccw(ccw) is True
    assert is_ccw(cw)  is False

# --- point in polygon ---

def test_point_in_polygon_inside():
    sq = [(0,0),(10,0),(10,10),(0,10)]
    assert point_in_polygon((5, 5), sq) is True

def test_point_in_polygon_outside():
    sq = [(0,0),(10,0),(10,10),(0,10)]
    assert point_in_polygon((15, 5), sq) is False

# --- bounding box ---

def test_bounding_box():
    poly = [(1,2),(5,3),(3,8)]
    bb = bounding_box([poly])
    assert bb == (1, 2, 5, 8)

def test_bounding_box_multiple():
    a = [(0,0),(2,2)]
    b = [(-1,-1),(1,1)]
    bb = bounding_box([a, b])
    assert bb == (-1, -1, 2, 2)

# --- containment ---

def test_classify_curves_simple():
    outer = [(0,0),(20,0),(20,20),(0,20)]
    inner = [(5,5),(15,5),(15,15),(5,15)]
    ext, holes = classify_curves([outer, inner])
    assert len(ext) == 1
    assert len(holes) == 1

def test_sort_by_containment_deepest_first():
    outer = [(0,0),(30,0),(30,30),(0,30)]
    mid   = [(5,5),(25,5),(25,25),(5,25)]
    inner = [(10,10),(20,10),(20,20),(10,20)]
    sorted_polys = sort_by_containment([outer, mid, inner])
    # innermost should be first
    assert sorted_polys[0] is inner

# --- angle helpers ---

def test_interior_angle_right():
    # L-shaped corner: prev=(1,0), vertex=(0,0), next=(0,1) → 90°
    angle = interior_angle_deg((1,0), (0,0), (0,1))
    assert math.isclose(angle, 90.0, abs_tol=0.1)

def test_interior_angle_straight():
    angle = interior_angle_deg((-1,0), (0,0), (1,0))
    assert math.isclose(angle, 180.0, abs_tol=0.1)

def test_is_concave_vertex_convex():
    # CCW square — all corners are convex
    sq = [(0,0),(10,0),(10,10),(0,10)]
    assert is_concave_vertex(sq[3], sq[0], sq[1], ccw=True) is False

def test_is_concave_vertex_concave():
    # A right-turn at vertex B in a CCW polygon is concave.
    # Incoming edge A→B goes rightward (+x): A=(0,0), B=(10,0)
    # Outgoing edge B→C goes downward (−y): C=(10,-5)
    # cross((B−A), (C−B)) = cross((10,0),(0,−5)) = 10*−5 − 0*0 = −50 < 0 → concave (CCW)
    assert is_concave_vertex((0, 0), (10, 0), (10, -5), ccw=True) is True

def test_is_concave_vertex_left_turn_is_convex():
    # A left-turn at B is convex in a CCW polygon.
    # Incoming A→B rightward, outgoing B→C upward (+y)
    assert is_concave_vertex((0, 0), (10, 0), (10, 5), ccw=True) is False
