from ._bootstrap import COMMON_BOOTSTRAP

# We store all components in this master list. The generator script reads this.
COMPONENTS = []

# 1. Cutout
COMPONENTS.append({
    "name": "rhinoPaths Cutout",
    "nickname": "rpCutout",
    "description": "Profile toolpath — inside, outside, or on-line offset with climb/conventional direction.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("boundary", "Curve", "Outer boundary curve"),
        ("tool_diam", "float", "Tool diameter, mm"),
        ("side", "str", "Offset side: outside/inside/on"),
        ("climb", "bool", "True: climb, False: conventional"),
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Cutting depth, mm (negative)"),
        ("stepdown", "float", "Max step-down per pass, mm"),
    ],
    "outputs": [
        ("toolpath", "List of Curves", "2D toolpath curves at cut side"),
        ("passes", "List of Curves", "3D toolpath curves at each Z level"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import cutout, pass_depths, apply_z

# Defaults
if tool_diam is None: tool_diam = 6.35
if side is None: side = "outside"
if climb is None: climb = True
if start_z is None: start_z = 0.0
if end_z is None: end_z = -19.05
if stepdown is None: stepdown = 3.175

toolpath = []
passes = []

try:
    if boundary:
        tol = 0.01
        pts = curve_to_polyline(boundary, tol)
        
        path_2d = cutout(pts, tool_diam, side, climb)
        
        if path_2d:
            toolpath = [polyline_to_curve(path_2d)]
            
            # Apply Z passes
            depths = pass_depths(start_z, end_z, stepdown)
            passes_3d = apply_z(path_2d, depths)
            passes = [polyline_to_curve(p) for p in passes_3d]

except Exception as e:
    print(f"Error computing cutout: {e}")
    print(traceback.format_exc())
"""
})

# 2. Pocket
COMPONENTS.append({
    "name": "rhinoPaths Pocket",
    "nickname": "rpPocket",
    "description": "Concentric pocketing with optional islands and Z-level passes.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("boundary", "Curve", "Outer pocket boundary"),
        ("islands", "List of Curves", "Optional island curves (bosses to avoid)"),
        ("tool_diam", "float", "Tool diameter, mm"),
        ("stepover", "float", "Stepover fraction (0.0–1.0), default 0.5"),
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Pocket depth, mm (negative)"),
        ("stepdown", "float", "Max step-down per pass, mm"),
    ],
    "outputs": [
        ("shells", "List of Curves", "2D toolpath shells"),
        ("passes", "List of Curves", "3D toolpath curves at each Z level"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import pocket, pass_depths, apply_z

if tool_diam is None: tool_diam = 6.35
if stepover is None: stepover = 0.4
if start_z is None: start_z = 0.0
if end_z is None: end_z = -12.7
if stepdown is None: stepdown = 3.175

shells = []
passes = []

try:
    if boundary:
        tol = 0.01
        boundary_pts = curve_to_polyline(boundary, tol)
        island_pts_list = [curve_to_polyline(c, tol) for c in (islands or [])]

        shells_2d = pocket(boundary_pts, island_pts_list, tool_diam, stepover)
        
        if shells_2d:
            shells = [polyline_to_curve(s) for s in shells_2d]
            
            depths = pass_depths(start_z, end_z, stepdown)
            passes_3d = []
            for shell in shells_2d:
                passes_3d.extend(apply_z(shell, depths))
            passes = [polyline_to_curve(p) for p in passes_3d]

except Exception as e:
    print(f"Error computing pocket: {e}")
    print(traceback.format_exc())
"""
})

# 3. Drill
COMPONENTS.append({
    "name": "rhinoPaths Drill",
    "nickname": "rpDrill",
    "description": "Drill cycles at circle centres.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("circles", "List of Curves", "Circles to drill"),
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Drill depth, mm (negative)"),
        ("peck_depth", "float", "Max peck depth per plunge, mm"),
    ],
    "outputs": [
        ("centres", "List of Points", "Extracted drill centres"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
import Rhino.Geometry as rg
from rhinopaths.geometry import curve_to_polyline
from rhinopaths.toolpaths import drill

if start_z is None: start_z = 0.0
if end_z is None: end_z = -19.05
if peck_depth is None: peck_depth = 5.0

centres = []

try:
    if circles:
        tol = 0.01
        polys = [curve_to_polyline(c, tol) for c in circles]
        pts = drill(polys)
        
        for pt in pts:
            # Drop the centre to end_z so the postprocessor drills to that Z
            centres.append(rg.Point3d(pt[0], pt[1], end_z))

except Exception as e:
    print(f"Error extracting drill centres: {e}")
    print(traceback.format_exc())
"""
})

# 4. Engrave
COMPONENTS.append({
    "name": "rhinoPaths Engrave",
    "nickname": "rpEngrave",
    "description": "Engraving pass sorted by nearest-neighbour.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("curves", "List of Curves", "Curves to engrave"),
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Engraving depth, mm (negative)"),
    ],
    "outputs": [
        ("passes", "List of Curves", "Sorted and Z-aligned engraving curves"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.toolpaths import engrave

if start_z is None: start_z = 0.0
if end_z is None: end_z = -1.5

passes = []

try:
    if curves:
        tol = 0.01
        polys = [curve_to_polyline(c, tol) for c in curves]
        
        # apply end_z locally before sort
        z_polys = []
        for poly in polys:
            z_polys.append([(p[0], p[1], end_z) for p in poly])

        sorted_polys = engrave(z_polys)
        passes = [polyline_to_curve(p) for p in sorted_polys]

except Exception as e:
    print(f"Error sorting engrave passes: {e}")
    print(traceback.format_exc())
"""
})

# 5. Dogbone
COMPONENTS.append({
    "name": "rhinoPaths Dogbone",
    "nickname": "rpDogBone",
    "description": "Inserts dogbone reliefs at concave corners.",
    "category": "rhinoPaths",
    "subcategory": "Operations",
    "inputs": [
        ("boundary", "Curve", "Outer boundary curve"),
        ("tool_diam", "float", "Tool diameter, mm"),
        ("climb", "bool", "True: climb milling, False: conventional"),
    ],
    "outputs": [
        ("dogboned", "Curve", "Boundary with dogbones inserted"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline, polyline_to_curve
from rhinopaths.dogbone import add_dogbones

if tool_diam is None: tool_diam = 6.35
if climb is None: climb = True

dogboned = boundary

try:
    if boundary:
        tol = 0.01
        pts = curve_to_polyline(boundary, tol)
        
        path_2d = add_dogbones(pts, tool_diam, climb)
        if path_2d:
            dogboned = polyline_to_curve(path_2d)

except Exception as e:
    print(f"Error computing dogbones: {e}")
    print(traceback.format_exc())
"""
})

# 6. Feedrate
COMPONENTS.append({
    "name": "rhinoPaths Feedrate",
    "nickname": "rpFeed",
    "description": "Calculates feedrates based on chipload and tool parameters.",
    "category": "rhinoPaths",
    "subcategory": "Utilities",
    "inputs": [
        ("tool_diam", "float", "Tool diameter, mm"),
        ("flutes", "int", "Number of cutter flutes"),
        ("rpm", "int", "Spindle RPM"),
        ("chipload", "float", "Target chipload mm/tooth"),
    ],
    "outputs": [
        ("feed_mm_min", "float", "Calculated feedrate in mm/min"),
        ("plunge_mm_min", "float", "Calculated plunge rate in mm/min"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.feedrate import feedrate

if tool_diam is None: tool_diam = 6.35
if flutes is None: flutes = 2
if rpm is None: rpm = 18000
if chipload is None: chipload = 0.05

feed_mm_min = None
plunge_mm_min = None

try:
    feed_mm_min = feedrate(tool_diam, flutes, rpm, chipload)
    if feed_mm_min: plunge_mm_min = feed_mm_min * 0.4
except Exception as e:
    print(f"Error calculating feedrate: {e}")
    print(traceback.format_exc())
"""
})

# 7. PostProcessor
COMPONENTS.append({
    "name": "rhinoPaths PostProcessor",
    "nickname": "rpPost",
    "description": "Converts toolpaths into G-code or ShopBot SBP files.",
    "category": "rhinoPaths",
    "subcategory": "Export",
    "inputs": [
        ("cut_passes", "List of Curves", "Nested list of cut curves (e.g., from Cutout/Pocket)"),
        ("drill_pts", "List of Points", "List of drill centres (e.g., from Drill)"),
        ("machine", "str", "'gcode' or 'shopbot'"),
        ("clearance_height", "float", "Rapid retract height, mm"),
        ("spindle_rpm", "int", "Spindle rotation speed"),
        ("peck_depth", "float", "Peck depth for drilling, mm"),
        ("ramp_dist", "float", "Helical ramp entry length, mm"),
        ("tabs", "bool", "Insert tabs automatically"),
        ("tab_width", "float", "Width of generated tabs, mm"),
        ("tab_thickness", "float", "Height of generated tabs, mm"),
        ("feedrate", "float", "Cutting feedrate, mm/min"),
        ("plunge", "float", "Plunge speed, mm/min"),
    ],
    "outputs": [
        ("file_content", "str", "Generated G-code / SBP text"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.geometry import curve_to_polyline
from rhinopaths.postprocessor import GCodePost, ShopBotPost

if machine is None: machine = "gcode"
if clearance_height is None: clearance_height = 12.7
if spindle_rpm is None: spindle_rpm = 18000
if peck_depth is None: peck_depth = 5.0
if ramp_dist is None: ramp_dist = 0.0
if tabs is None: tabs = False
if tab_width is None: tab_width = 8.0
if tab_thickness is None: tab_thickness = 3.0
if feedrate is None: feedrate = 2500.0
if plunge is None: plunge = 800.0

file_content = ""

try:
    post_cls = ShopBotPost if str(machine).lower() == "shopbot" else GCodePost
    spindle_cmd = f"M3 S{int(spindle_rpm)}"
    post = post_cls(spindle_on_cmd=spindle_cmd, clearance_height=clearance_height, feedrate=feedrate, plunge_speed=plunge)
    
    post.header()
    
    # Process cutting passes
    if cut_passes:
        tol = 0.01
        for pass_group in cut_passes:
            if not pass_group: continue
            
            # Unpack branches if data trees are passed in
            if hasattr(pass_group, 'BranchCount'):
                path_list = [crv for i in range(pass_group.BranchCount) for crv in pass_group.Branch(i)]
            elif isinstance(pass_group, (list, tuple)):
                path_list = pass_group
            else:
                path_list = [pass_group]
                
            for crv in path_list:
                pts = curve_to_polyline(crv, tol)
                if not pts: continue
                
                # Check tabs/ramps
                z_start = pts[0][2] if len(pts[0]) > 2 else 0.0
                if ramp_dist > 0:
                    pts = post.ramp_entry(pts, ramp_dist)
                
                if tabs:
                    post.tabs(pts, cut_z=z_start, tab_width=tab_width, tab_height=tab_thickness, feedrate=feedrate)
                else:
                    post.toolpath(pts)
    
    # Process drills
    if drill_pts:
        pts = [(p.X, p.Y, p.Z) for p in drill_pts]
        post.drill_points(pts, peck_depth=peck_depth)

    post.footer()
    file_content = post.get_code()

except Exception as e:
    print(f"Error generating code: {e}")
    print(traceback.format_exc())
"""
})

# 8. Previewer
COMPONENTS.append({
    "name": "rhinoPaths G-Code Preview",
    "nickname": "rpPreview",
    "description": "Parses G-code text back into line curves for previewing.",
    "category": "rhinoPaths",
    "subcategory": "Utilities",
    "inputs": [
        ("gcode_text", "str", "The raw G-code text to preview"),
    ],
    "outputs": [
        ("rapid_moves", "List of Curves", "Red rapid/travel moves (G0)"),
        ("feed_moves", "List of Curves", "Blue cutting moves (G1/G2/G3)"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
import Rhino.Geometry as rg

rapid_moves = []
feed_moves = []

try:
    if gcode_text:
        lines = str(gcode_text).split("\\n")
        
        last_pt = rg.Point3d(0, 0, 0)
        mode = "G0"
        
        for line in lines:
            line = line.split(";")[0].strip().upper()
            if not line: continue
            
            if "G0" in line: mode = "G0"
            elif "G1" in line: mode = "G1"
            
            x, y, z = last_pt.X, last_pt.Y, last_pt.Z
            has_move = False
            
            for part in line.split():
                if part.startswith("X"):
                    x = float(part[1:])
                    has_move = True
                elif part.startswith("Y"):
                    y = float(part[1:])
                    has_move = True
                elif part.startswith("Z"):
                    z = float(part[1:])
                    has_move = True
                    
            if has_move:
                next_pt = rg.Point3d(x, y, z)
                line_crv = rg.LineCurve(last_pt, next_pt)
                
                if mode == "G0":
                    rapid_moves.append(line_crv)
                else:
                    feed_moves.append(line_crv)
                    
                last_pt = next_pt

except Exception as e:
    print(f"Error previewing code: {e}")
    print(traceback.format_exc())
"""
})

# 9. Pass Depths
COMPONENTS.append({
    "name": "rhinoPaths Pass Depths",
    "nickname": "rpZDepths",
    "description": "Calculates Z-level slice depths.",
    "category": "rhinoPaths",
    "subcategory": "Utilities",
    "inputs": [
        ("start_z", "float", "Top of material, mm"),
        ("end_z", "float", "Target cutting depth, mm (negative)"),
        ("stepdown", "float", "Max step-down per pass, mm"),
    ],
    "outputs": [
        ("depths", "List of Floats", "Calculated Z depths from start_z to end_z"),
    ],
    "code": COMMON_BOOTSTRAP + """
import traceback
from rhinopaths.toolpaths import pass_depths as calc_depths

if start_z is None: start_z = 0.0
if end_z is None: end_z = -19.05
if stepdown is None: stepdown = 3.175

depths = []

try:
    depths = calc_depths(start_z, end_z, stepdown)
except Exception as e:
    print(f"Error calculating pass depths: {e}")
    print(traceback.format_exc())
"""
})
