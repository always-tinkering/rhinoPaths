import pytest
from rhinopaths.feedrate import feedrate

def test_feedrate_basic():
    """
    Test basic linera feedrate calculation.
    Feedrate = RPM * flutes * chipload
    """
    # 10,000 RPM * 2 flutes * 0.05 chipload = 1000 mm/min
    f = feedrate(tool_diam=6.35, flutes=2, rpm=10000, chipload=0.05)
    assert f == 1000.0

def test_feedrate_high_speed():
    f = feedrate(tool_diam=12.7, flutes=3, rpm=18000, chipload=0.1)
    assert f == 5400.0
