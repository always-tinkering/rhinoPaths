"""
High-level 2.5-axis toolpath generators for rhinoPaths Rhino8.

These combine raw geometry components into usable CAM operations.
"""

from .offset import safe_offset

def cutout(curve, tool_diam, side="outside", climb=True, tabs=0, tab_height=0, tab_width=0):
    """
    Generate a 2D cutout/profile toolpath.
    
    Args:
        curve: Rhino.Geometry.Curve
        tool_diam: float, mm
        side: str, "outside", "inside", or "on"
        climb: bool, True for climb milling, False for conventional
        tabs: int, number of holding tabs to generate
        tab_height: float, mm
        tab_width: float, mm
        
    Returns:
        List of Rhino.Geometry.Curve at Z=0. Caller applies pass depths.
    """
    # 1. Determine offset direction based on 'side' and 'climb' parameters.
    # 2. Call safe_offset()
    # 3. If tabs > 0, generate Z-hops at evenly spaced intervals.
    pass

def pocket(boundary, islands, tool_diam, stepover, angle=0.0):
    """
    Generate a 2.5D raster or concentric pocket.
    
    Args:
        boundary: Rhino.Geometry.Curve representing the outer wall.
        islands: List of Rhino.Geometry.Curve representing avoidance zones.
        tool_diam: float, mm
        stepover: float, mm
        angle: float, degrees. Used if raster strategy is implemented.
        
    Returns:
        List of Rhino.Geometry.Curve shells/lines connecting the pocket.
    """
    # 1. Compute valid cutting area = boundary - (islands + tool_radius offset).
    # 2. Iterate shrink_to_nothing() shells.
    pass

def drill(curve_or_point):
    """
    Generate plunge coordinates for drilling.
    
    Args:
        curve_or_point: Rhino.Geometry.Curve (e.g., circles) or Point.
        
    Returns:
        Rhino.Geometry.Point3d specifying the drill center.
    """
    # Simply extract the center of a planar closed curve or use the point.
    pass

def engrave(curves):
    """
    Generate a v-carve or 2D engrave toolpath (on-curve).
    
    Args:
        curves: List of Rhino.Geometry.Curve
        
    Returns:
        List of Rhino.Geometry.Curve sorted for efficient traversal.
    """
    # Return sorted curves natively on Z=0.
    pass

def pass_depths(curves, start_z, end_z, pass_depth):
    """
    Given a set of Z=0 base curves, duplicate and translate them to target depths.
    
    Args:
        curves: List of Rhino.Geometry.Curve
        start_z: float, material top surface
        end_z: float, material bottom (or target pocket depth)
        pass_depth: float, maximum cut step-down
        
    Returns:
        List of tuples (Curve, depth) representing passes.
    """
    # Calculate ceil( (start_z - end_z) / pass_depth ) passes
    # Duplicate geometry and translate along -Z axis.
    pass
