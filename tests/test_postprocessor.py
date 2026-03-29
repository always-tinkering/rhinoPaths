"""Tests for rhinopaths.postprocessor — fully headless."""
import math
import pytest
from rhinopaths.postprocessor import GCodePost, ShopBotPost

# ---- Backwards-compat aliases still importable ----
from rhinopaths.postprocessor import GCodePostProcessor, ShopBotPostProcessor


# ---------------------------------------------------------------------------
# G-code basic moves
# ---------------------------------------------------------------------------

def test_rapid_all_axes():
    pp = GCodePost()
    assert pp.rapid(x=10.5, y=20.0, z=5.0) == "G0 X10.500 Y20.000 Z5.000"

def test_rapid_z_only():
    pp = GCodePost()
    assert pp.rapid(z=5.0) == "G0 Z5.000"

def test_rapid_xy_only():
    pp = GCodePost()
    assert pp.rapid(x=1.0, y=2.0) == "G0 X1.000 Y2.000"

def test_feed_with_feedrate():
    pp = GCodePost()
    result = pp.feed(x=10.5, y=20.0, z=-1.0, f=1500.0)
    assert result == "G1 X10.500 Y20.000 Z-1.000 F1500.0"

def test_feed_suppresses_repeated_feedrate():
    """Feedrate should only appear when it changes."""
    pp = GCodePost()
    pp.feed(x=0, y=0, z=0, f=1200.0)           # first — includes F
    result2 = pp.feed(x=10, y=0, z=-5, f=1200.0)  # same F — omit
    assert "F" not in result2

def test_feed_emits_new_feedrate():
    pp = GCodePost()
    pp.feed(x=0, y=0, f=1200.0)
    result = pp.feed(x=10, y=0, f=2400.0)   # different F — include
    assert "F2400.0" in result

def test_header_contains_required_gcodes():
    pp = GCodePost()
    h = pp.header()
    assert "G90" in h   # absolute mode
    assert "G21" in h   # metric

def test_footer_contains_required_gcodes():
    pp = GCodePost()
    f = pp.footer()
    assert "M5" in f    # spindle off
    assert "M30" in f   # program end

def test_arc_cw():
    pp = GCodePost()
    result = pp.arc_cw(i=5.0, j=0.0, x=10.0, y=0.0, z=-1.0, f=1200.0)
    assert result.startswith("G2")
    assert "I5.000" in result
    assert "J0.000" in result

def test_arc_ccw():
    pp = GCodePost()
    result = pp.arc_ccw(i=5.0, j=0.0, x=10.0, y=0.0, z=-1.0, f=1200.0)
    assert result.startswith("G3")


# ---------------------------------------------------------------------------
# ShopBot dialect
# ---------------------------------------------------------------------------

def test_shopbot_rapid():
    pp = ShopBotPost()
    assert pp.rapid(x=5.0, y=5.0, z=0.0) == "J3,5.000,5.000,0.000"

def test_shopbot_feed():
    pp = ShopBotPost()
    assert pp.feed(x=5.0, y=5.0, z=-1.0) == "M3,5.000,5.000,-1.000"

def test_shopbot_rapid_z_only():
    pp = ShopBotPost()
    assert pp.rapid(z=5.0) == "J3,5.000"

def test_shopbot_header():
    pp = ShopBotPost()
    assert "SA" in pp.header()

def test_shopbot_footer():
    pp = ShopBotPost()
    assert "End" in pp.footer()


# ---------------------------------------------------------------------------
# Tab insertion
# ---------------------------------------------------------------------------

def test_tabs_produces_output():
    """tabs() should produce G-code lines for a simple square path."""
    pp = GCodePost()
    sq = [(0, 0), (50, 0), (50, 50), (0, 50), (0, 0)]
    lines = pp.tabs(sq, cut_z=-18.0, tab_width=8.0, spacing=40.0)
    assert len(lines) > 0
    assert all(isinstance(l, str) for l in lines)

def test_tabs_lifts_z():
    """Some tab lines should contain a Z value above cut_z."""
    pp = GCodePost()
    cut_z = -18.0
    tab_z = -15.0
    sq = [(0, 0)] + [(i * 10, 0) for i in range(1, 20)]  # 190mm straight line
    lines = pp.tabs(sq, cut_z=cut_z,
                    tab_width=8.0, spacing=30.0, feedrate=1200.0)
    # At least one line should have Z above cut_z
    lifted = [l for l in lines if f"Z{tab_z:.3f}" in l]
    assert len(lifted) > 0

def test_tabs_returns_to_cut_z():
    """After each tab the Z should return to cut_z."""
    pp = GCodePost()
    cut_z = -12.0
    tab_z = -9.0
    path = [(i * 5, 0) for i in range(40)]  # 200mm
    lines = pp.tabs(path, cut_z=cut_z,
                    tab_width=6.0, spacing=40.0)
    cut_lines = [l for l in lines if f"Z{cut_z:.3f}" in l]
    tab_lines  = [l for l in lines if f"Z{tab_z:.3f}" in l]
    # Should have both cut-depth and tab-height moves
    assert len(cut_lines) > 0
    assert len(tab_lines) > 0


# ---------------------------------------------------------------------------
# Ramp entry
# ---------------------------------------------------------------------------

def test_ramp_entry_produces_output():
    pp = GCodePost()
    sq = [(0, 0), (50, 0), (50, 50), (0, 50)]
    lines = pp.ramp_entry(sq, start_z=0.0, end_z=-6.0, feedrate=600.0)
    assert len(lines) > 0

def test_ramp_entry_reaches_end_z():
    """Last ramp move should reach (or surpass) end_z."""
    pp = GCodePost()
    path = [(i * 20, 0) for i in range(10)]  # 200mm straight
    end_z = -6.0
    lines = pp.ramp_entry(path, start_z=0.0, end_z=end_z,
                          max_ramp_angle_deg=3.0)
    # Extract Z values from ramp lines
    import re
    zvals = []
    for l in lines:
        m = re.search(r"Z([-\d.]+)", l)
        if m:
            zvals.append(float(m.group(1)))
    assert zvals, "No Z values in ramp output"
    assert min(zvals) <= end_z + 0.001  # reached target depth

def test_ramp_descent_is_gradual():
    """Z values should monotonically decrease during ramp."""
    pp = GCodePost()
    path = [(i * 10, 0) for i in range(20)]
    lines = pp.ramp_entry(path, start_z=0.0, end_z=-6.0, max_ramp_angle_deg=3.0)
    import re
    zvals = []
    for l in lines:
        m = re.search(r"Z([-\d.]+)", l)
        if m:
            zvals.append(float(m.group(1)))
    # Each Z should be <= previous (always going deeper or staying)
    for i in range(1, len(zvals)):
        assert zvals[i] <= zvals[i - 1] + 0.001
