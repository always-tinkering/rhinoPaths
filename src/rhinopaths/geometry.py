"""
Geometry utilities for rhinoPaths Rhino8.

Provides functionality for analyzing curves, containment, and polyline conversions.
These methods act as wrappers around RhinoCommon but can be mocked for unit testing.
"""

def classify_curves(curves):
    """
    Classify a list of curves into exterior boundaries and interior holes based on containment.
    
    Args:
        curves: List of Rhino.Geometry.Curve objects.
        
    Returns:
        tuple: (exterior_curves, interior_curves)
    """
    # TODO: Implement containment logic using rg.Curve.PlanarClosedCurveRelationship
    pass

def sort_by_containment(curves):
    """
    Sort a list of curves based on containment depth.
    Curves that are innermost should be processed first.
    
    Args:
        curves: List of Rhino.Geometry.Curve objects.
        
    Returns:
        List of curves sorted from innermost to outermost.
    """
    # TODO: Implement depth sorting
    pass

def curve_to_polyline(curve, tolerance=0.01):
    """
    Discretize a NurbsCurve or geometric curve into a series of points (Polyline).
    
    Args:
        curve: Rhino.Geometry.Curve
        tolerance: Float representing maximum division error.
        
    Returns:
        list of points representing the polyline.
    """
    # TODO: Use Curve.ToPolyline()
    pass

def polyline_to_curve(points):
    """
    Rebuild a polyline from a list of points back into a NurbsCurve or LineCurve.
    
    Args:
        points: list of point coordinates.
        
    Returns:
        Rhino.Geometry.Curve
    """
    # TODO: Implement curve rebuilding
    pass

def bounding_box(curves):
    """
    Compute the axis-aligned bounding box for a set of curves.
    
    Args:
        curves: List of Rhino.Geometry.Curve objects.
        
    Returns:
        Rhino.Geometry.BoundingBox
    """
    # TODO: Aggregate bounding boxes of all curves
    pass
