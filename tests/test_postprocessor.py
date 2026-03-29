import pytest
from rhinopaths.postprocessor import GCodePostProcessor, ShopBotPostProcessor

def test_generic_gcode_rapid():
    pp = GCodePostProcessor(config={"rapid_rate": 2000})
    res = pp.rapid(10.5, 20.0, 5.0)
    assert res == "G0 X10.500 Y20.000 Z5.000"

def test_generic_gcode_feed():
    pp = GCodePostProcessor(config={"default_feedrate": 1500})
    res = pp.feed(10.5, 20.0, -1.0)
    assert res == "G1 X10.500 Y20.000 Z-1.000 F1500.0"

def test_shopbot_post():
    pp = ShopBotPostProcessor(config={})
    res = pp.rapid(5.0, 5.0, 0.0)
    assert res == "J3,5.000,5.000,0.000"
    
def test_shopbot_feed():
    pp = ShopBotPostProcessor(config={})
    res = pp.feed(5.0, 5.0, -1.0)
    assert res == "M3,5.000,5.000,-1.000"
