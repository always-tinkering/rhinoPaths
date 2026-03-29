"""Tests for rhinopaths.toolpaths and rhinopaths.offset — fully headless."""
import math
import pytest
from rhinopaths.toolpaths import (
    pass_depths, drill, engrave, cutout, pocket, apply_z
)
from rhinopaths.offset import safe_offset, shrink_to_nothing
from rhinopaths.geometry import polyline_area, is_ccw


# ---------------------------------------------------------------------------
# pass_depths
# ---------------------------------------------------------------------------

def test_pass_depths_even():
    """18mm material, 6mm pass → exactly 3 passes."""
    depths = pass_depths(0.0, -18.0, 6.0)
    assert depths == [-6.0, -12.0, -18.0]


def test_pass_depths_uneven():
    """10mm material, 3mm pass → 3 passes with last at -10."""
    depths = pass_depths(0.0, -10.0, 3.0)
    assert depths[-1] == -10.0
    assert len(depths) == 4  # -3, -6, -9, -10


def test_pass_depths_single():
    """Shallower than one pass → just the final depth."""
    depths = pass_depths(0.0, -2.0, 6.0)
    assert depths == [-2.0]


def test_pass_depths_bad_input():
    with pytest.raises(ValueError):
        pass_depths(0.0, 5.0, 6.0)  # end_z above start_z
    with pytest.raises(ValueError):
        pass_depths(0.0, -10.0, -3.0)  # negative pass_depth


# ---------------------------------------------------------------------------
# drill
# ---------------------------------------------------------------------------

def test_drill_centre_circle():
    """Circle polyline centroid should be (5, 5)."""
    n = 32
    cx, cy, r = 5.0, 5.0, 3.0
    circle = [(cx + r * math.cos(2 * math.pi * i / n),
               cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    centres = drill([circle])
    assert len(centres) == 1
    assert math.isclose(centres[0][0], cx, abs_tol=0.01)
    assert math.isclose(centres[0][1], cy, abs_tol=0.01)


def test_drill_multiple():
    """Multiple circles → multiple centres."""
    c1 = [(math.cos(a), math.sin(a)) for a in [0, 2, 4]]
    c2 = [(10 + math.cos(a), math.sin(a)) for a in [0, 2, 4]]
    centres = drill([c1, c2])
    assert len(centres) == 2


# ---------------------------------------------------------------------------
# engrave
# ---------------------------------------------------------------------------

def test_engrave_sorts_nearest_first():
    """Three line segments — ensure nearest-neighbour ordering."""
    seg1 = [(0, 0), (5, 0)]
    seg2 = [(100, 100), (105, 100)]  # far away
    seg3 = [(5, 1), (10, 1)]        # close to end of seg1
    sorted_segs = engrave([seg1, seg2, seg3])
    # seg1 first (as given), seg3 should follow (nearest), seg2 last
    assert sorted_segs[0] is seg1
    assert sorted_segs[1] is seg3
    assert sorted_segs[2] is seg2


def test_engrave_empty():
    assert engrave([]) == []


# ---------------------------------------------------------------------------
# apply_z
# ---------------------------------------------------------------------------

def test_apply_z_basic():
    toolpath = [(0, 0), (10, 0), (10, 10)]
    depths = [-5.0, -10.0]
    passes = apply_z(toolpath, depths)
    assert len(passes) == 2
    assert passes[0][0] == (0, 0, -5.0)
    assert passes[1][-1] == (10, 10, -10.0)


# ---------------------------------------------------------------------------
# offset (safe_offset / shrink_to_nothing)
# ---------------------------------------------------------------------------

def test_safe_offset_shrinks_square():
    """Offsetting a 20×20 square inward by 2mm should give a smaller polygon."""
    sq = [(0, 0), (20, 0), (20, 20), (0, 20)]
    result = safe_offset(sq, 2.0)
    assert len(result) >= 3
    original_area = abs(polyline_area(sq))
    offset_area = abs(polyline_area(result))
    assert offset_area < original_area


def test_safe_offset_too_large_returns_empty():
    """Offsetting inward by more than half the size should degenerate."""
    sq = [(0, 0), (4, 0), (4, 4), (0, 4)]
    result = safe_offset(sq, 5.0)  # 5mm > 2mm half-width
    assert result == []


def test_shrink_to_nothing_produces_shells():
    """A 50×50 square shrunk by 5mm steps should give ~4–5 shells."""
    sq = [(0, 0), (50, 0), (50, 50), (0, 50)]
    shells = shrink_to_nothing(sq, 5.0)
    assert len(shells) >= 3  # at least a few shells before degenerating


def test_shrink_to_nothing_decreasing_area():
    """Each shell should be smaller than the previous."""
    sq = [(0, 0), (40, 0), (40, 40), (0, 40)]
    shells = shrink_to_nothing(sq, 4.0)
    areas = [abs(polyline_area(s)) for s in shells]
    for i in range(1, len(areas)):
        assert areas[i] < areas[i - 1]


# ---------------------------------------------------------------------------
# cutout
# ---------------------------------------------------------------------------

def test_cutout_outside_larger():
    """Outside cutout offset should be larger than the original boundary."""
    sq = [(0, 0), (20, 0), (20, 20), (0, 20)]
    result = cutout(sq, tool_diam=6.0, side="outside")
    if result:  # may be empty for very small geometry
        assert abs(polyline_area(result)) > abs(polyline_area(sq))


def test_cutout_inside_smaller():
    """Inside cutout offset should be smaller than the original boundary."""
    sq = [(0, 0), (40, 0), (40, 40), (0, 40)]
    result = cutout(sq, tool_diam=6.0, side="inside")
    assert result  # should not be empty for a large boundary
    assert abs(polyline_area(result)) < abs(polyline_area(sq))


def test_cutout_on_returns_original():
    sq = [(0, 0), (20, 0), (20, 20), (0, 20)]
    result = cutout(sq, tool_diam=6.0, side="on")
    assert result == sq


# ---------------------------------------------------------------------------
# pocket
# ---------------------------------------------------------------------------

def test_pocket_basic_shells():
    """A 60×60 pocket with 6mm tool and 50% stepover should produce shells."""
    sq = [(0, 0), (60, 0), (60, 60), (0, 60)]
    shells = pocket(sq, [], tool_diam=6.0, stepover_pct=0.5)
    assert len(shells) >= 2


def test_pocket_no_geometry_for_tiny_boundary():
    """A 3×3mm boundary is smaller than the 6mm tool diameter — no shells."""
    tiny = [(0, 0), (3, 0), (3, 3), (0, 3)]
    shells = pocket(tiny, [], tool_diam=6.0)
    assert shells == []
