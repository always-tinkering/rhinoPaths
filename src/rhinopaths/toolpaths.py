"""
rhinoPaths — 2.5-axis toolpath generators.

All functions operate on plain (x, y[, z]) tuple polylines and return the same,
so they are fully headless and unit-testable without Rhino.

At the Grasshopper boundary, component wrappers convert Rhino Curve ↔ polyline tuples
using geometry.curve_to_polyline / polyline_to_curve.
"""

import math
from .offset import safe_offset, shrink_to_nothing
from .geometry import (
    classify_curves, sort_by_containment,
    polyline_area, bounding_box, dist2, point_in_polygon, is_ccw
)


# ---------------------------------------------------------------------------
# pass_depths  — pure Python, fully headless
# ---------------------------------------------------------------------------

def pass_depths(start_z, end_z, stepdown):
    """
    Generate a list of Z depths for multi-pass cutting.

    Slices from start_z down to end_z in steps of pass_depth.
    Always includes end_z as the final pass.

    Args:
        start_z:    float, material top surface (e.g. 0.0)
        end_z:      float, target depth (e.g. -18.0)
        stepdown: float, maximum step-down per pass (positive number)

    Returns:
        list of float z-values, e.g. [-6.0, -12.0, -18.0]
    """
    if stepdown <= 0:
        raise ValueError("stepdown must be positive")
    if end_z >= start_z:
        raise ValueError("end_z must be below start_z")

    depths = []
    z = start_z - abs(stepdown)
    while z > end_z:
        depths.append(round(z, 6))
        z -= abs(stepdown)
    depths.append(round(end_z, 6))  # always include the final depth
    return depths


# ---------------------------------------------------------------------------
# drill  — pure Python
# ---------------------------------------------------------------------------

def drill(circles):
    """
    Extract drill-point centres from a list of circular polylines.

    For each circle (represented as a closed polyline approximation),
    the centre is computed as the centroid of the polyline points.

    Args:
        circles: list of polylines (each a list of (x, y) or (x, y, z))

    Returns:
        list of (x, y, z) drill centre points
    """
    centres = []
    for poly in circles:
        n = len(poly)
        if n == 0:
            continue
        cx = sum(p[0] for p in poly) / n
        cy = sum(p[1] for p in poly) / n
        cz = poly[0][2] if len(poly[0]) > 2 else 0.0
        centres.append((cx, cy, cz))
    return centres


# ---------------------------------------------------------------------------
# engrave  — pure Python
# ---------------------------------------------------------------------------

def engrave(curves):
    """
    Sort a list of curves for efficient engraving (nearest-neighbour traversal).

    Args:
        curves: list of polylines (each a list of (x, y[, z]))

    Returns:
        sorted list of polylines
    """
    if not curves:
        return []

    remaining = list(curves)
    sorted_curves = [remaining.pop(0)]
    last_end = sorted_curves[-1][-1]  # last point of last curve

    while remaining:
        # Find the curve whose start point is nearest to the last endpoint
        best_idx = 0
        best_dist = float('inf')
        for i, curve in enumerate(remaining):
            d = dist2(last_end, curve[0])
            if d < best_dist:
                best_dist = d
                best_idx = i
        next_curve = remaining.pop(best_idx)
        sorted_curves.append(next_curve)
        last_end = next_curve[-1]

    return sorted_curves


# ---------------------------------------------------------------------------
# cutout  — polygon offset based
# ---------------------------------------------------------------------------

def cutout(boundary_pts, tool_diam, side="outside", climb=True):
    """
    Generate a profile/cutout toolpath by offsetting the boundary.

    Args:
        boundary_pts: list of (x, y) — closed boundary polygon
        tool_diam:    float, mm
        side:         str — "outside" (default), "inside", or "on"
        climb:        bool — True for climb milling (CCW for outside cuts),
                             False for conventional

    Returns:
        list of (x, y) — the offset toolpath polygon
        (empty list if offset produces no valid geometry)
    """
    tool_r = tool_diam / 2.0

    if side == "on":
        return list(boundary_pts)

    if side == "outside":
        # Offset outward = negative inward distance
        offset_dist = -tool_r
    else:  # "inside"
        offset_dist = tool_r

    result = safe_offset(boundary_pts, offset_dist)

    # Reverse winding for conventional milling
    if result and not climb:
        result = list(reversed(result))

    return result


# ---------------------------------------------------------------------------
# pocket  — concentric shell raster
# ---------------------------------------------------------------------------

def pocket(boundary_pts, island_pts_list, tool_diam, stepover_pct=0.5):
    """
    Generate a 2.5-axis concentric raster pocket.

    Strategy:
      1. Start with the boundary offset inward by tool_radius (first cutting shell)
      2. Shrink inward by stepover per pass until no geometry remains
      3. Subtract island exclusion zones from each shell

    Args:
        boundary_pts:    list of (x, y) — outer boundary
        island_pts_list: list of polylines — regions to avoid (holes/bosses)
        tool_diam:       float, mm
        stepover_pct:    float — 0.0–1.0, fraction of tool_diam for stepover

    Returns:
        list of shells (each a list of (x, y) tuples), outermost first
    """
    tool_r = tool_diam / 2.0
    stepover = tool_diam * stepover_pct

    # Quick rejection: if the bounding box is smaller than one full tool diameter
    # in any dimension, no pocket shell can fit.
    from .geometry import bounding_box
    bbox = bounding_box([boundary_pts])
    width  = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if width < tool_diam or height < tool_diam:
        return []

    # First shell: offset boundary inward by tool_radius
    first_shell = safe_offset(boundary_pts, tool_r)
    if not first_shell:
        return []

    # Generate all concentric shells
    all_shells = [first_shell] + shrink_to_nothing(first_shell, stepover)

    # Filter out points inside any island (simple point-exclusion per shell)
    # A proper implementation would boolean-subtract island offsets;
    # this is a conservative approximation for convex islands.
    if island_pts_list:
        island_offsets = [safe_offset(isl, -tool_r) or isl for isl in island_pts_list]
        filtered = []
        for shell in all_shells:
            # Keep the shell only if its centroid is not inside any island
            n = len(shell)
            cx = sum(p[0] for p in shell) / n
            cy = sum(p[1] for p in shell) / n
            in_island = any(point_in_polygon((cx, cy), isl) for isl in island_offsets)
            if not in_island:
                filtered.append(shell)
        all_shells = filtered

    return all_shells


# ---------------------------------------------------------------------------
# apply_z  — apply a list of depths to a 2D toolpath
# ---------------------------------------------------------------------------

def apply_z(toolpath_2d, z_depths):
    """
    Duplicate a 2D toolpath for each Z depth pass.

    Args:
        toolpath_2d: list of (x, y) or (x, y, z) points
        z_depths:    list of float Z values (from pass_depths())

    Returns:
        list of passes — each pass is list of (x, y, z) tuples
    """
    passes = []
    for z in z_depths:
        pass_pts = [(p[0], p[1], z) for p in toolpath_2d]
        passes.append(pass_pts)
    return passes
