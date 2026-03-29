"""
Feedrate planning and calculations for rhinoPaths Rhino8.

Tools for chipload, surface speed cutting, and arc-feedrate compensation.
"""

def recommended_chipload(material_name, tool_diam):
    """
    Look up a recommended chipload (mm/tooth) based on material category.
    
    Args:
        material_name: str ("plywood", "hardwood", "aluminum", "acrylic")
        tool_diam: float, mm
        
    Returns:
        float: recommended chipload in mm per tooth.
    """
    # TODO: Provide basic data table
    pass

def feedrate(tool_diam, flutes, rpm, chipload):
    """
    Calculate the linear feedrate in mm/min given tool properties and target chipload.
    
    Formula: Feedrate = RPM * Number of flutes * Chipload
    
    Args:
        tool_diam: float, the diameter of the cutter (mm)
        flutes: int, how many cutting edges the tool has
        rpm: float, the spindle speed (revs per min)
        chipload: float, the actual chip cut (mm)
        
    Returns:
        float: Feedrate mm/min
    """
    return rpm * flutes * chipload

def feedrate_for_arcs(linear_feedrate, tool_r, arc_r):
    """
    Adjust feedrate for arc cutting (internal vs external circular interpolation).
    
    When cutting inside curves, the tool's outside edge is traveling faster.
    This compensation slows down internal cuts.
    
    Args:
        linear_feedrate: float, mm/min
        tool_r: float, radius of tool (mm)
        arc_r: float, radius of the arc toolpath (mm)
        
    Returns:
        float: Compensated feedrate in mm/min
    """
    # Inside cut compensation: F = F_linear * (R_arc - R_tool) / R_arc
    # If arc_r < tool_r it's physically impossible or an external cut
    pass
