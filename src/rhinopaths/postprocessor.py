"""
rhinoPaths — post-processor engine.

Translates geometric toolpaths into controller-specific machine code.
Supports:
  - Generic G-code (Fanuc/GRBL dialect)
  - ShopBot SBP dialect

Key additions over the stub:
  - Tab insertion  : insert holding tabs by lifting Z at regular intervals
  - Ramp entry     : helical ramp down into material instead of direct plunge
  - Keyword-only outputs so callers can emit partial moves (x-only, z-only, etc.)
"""

import math


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _fmt(v):
    """Format a float to 3 decimal places."""
    return f"{v:.3f}"


def _kwargs_to_axes(**kwargs):
    """Build an axis string like 'X1.000 Y2.000 Z-3.000' from keyword args."""
    parts = []
    for axis in ("x", "y", "z"):
        if kwargs.get(axis) is not None:
            parts.append(f"{axis.upper()}{_fmt(kwargs[axis])}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# G-code post-processor  (Fanuc / GRBL / Mach3 compatible)
# ---------------------------------------------------------------------------

class GCodePost:
    """
    Generic G-code post-processor.

    All move methods accept keyword x/y/z so callers can emit partial axes:
        post.rapid(z=5.0)          # G0 Z5.000
        post.feed(x=10, y=20, f=1200)  # G1 X10.000 Y20.000 F1200.0
    """

    def __init__(self, units="mm", spindle_on_cmd="M3 S18000"):
        self.units = units
        self.spindle_on_cmd = spindle_on_cmd
        self._last_f = None

    def header(self):
        unit_cmd = "G21" if self.units == "mm" else "G20"
        return (
            f"G90 ; absolute coordinates\n"
            f"{unit_cmd} ; {'metric' if self.units == 'mm' else 'imperial'} units\n"
            f"{self.spindle_on_cmd} ; spindle on"
        )

    def footer(self):
        return "M5 ; spindle off\nG0 Z50.000 ; safe retract\nM30 ; end program"

    def rapid(self, **kwargs):
        axes = _kwargs_to_axes(**kwargs)
        return f"G0 {axes}" if axes else ""

    def feed(self, f=None, **kwargs):
        axes = _kwargs_to_axes(**kwargs)
        if not axes:
            return ""
        f_str = ""
        if f is not None and f != self._last_f:
            f_str = f" F{f:.1f}"
            self._last_f = f
        return f"G1 {axes}{f_str}"

    def arc_cw(self, i, j, f=None, **kwargs):
        axes = _kwargs_to_axes(**kwargs)
        f_str = f" F{f:.1f}" if f is not None else ""
        return f"G2 {axes} I{_fmt(i)} J{_fmt(j)}{f_str}"

    def arc_ccw(self, i, j, f=None, **kwargs):
        axes = _kwargs_to_axes(**kwargs)
        f_str = f" F{f:.1f}" if f is not None else ""
        return f"G3 {axes} I{_fmt(i)} J{_fmt(j)}{f_str}"

    # ------------------------------------------------------------------
    # Tab insertion
    # ------------------------------------------------------------------

    def tabs(self, polyline_pts, cut_z, safe_z, tab_width=8.0,
             tab_height=3.0, spacing=80.0, feedrate=1200.0):
        """
        Insert holding tabs along a closed polyline path.

        Tabs are raised portions of the cut that keep the part attached to
        the sheet until the final release pass.

        Args:
            polyline_pts: list of (x, y) cut-depth points (2D)
            cut_z:        float — cutting Z depth (e.g. -18.0)
            safe_z:       float — Z to retract to during tab (e.g. cut_z + tab_height)
            tab_width:    float — mm of travel at raised Z per tab
            tab_height:   float — how far to lift above cut_z for tab
            spacing:      float — distance between tab centres along path
            feedrate:     float — cutting feedrate

        Returns:
            list of G-code strings for the tabbed pass
        """
        lines = []
        n = len(polyline_pts)
        if n < 2:
            return lines

        tab_z = cut_z + tab_height
        dist_since_tab = spacing / 2.0  # start first tab at spacing/2
        in_tab = False
        tab_remaining = 0.0

        def _seg_len(a, b):
            return math.hypot(b[0] - a[0], b[1] - a[1])

        for i in range(n):
            p = polyline_pts[i]
            if i == 0:
                lines.append(self.feed(x=p[0], y=p[1], z=cut_z, f=feedrate))
                continue

            prev = polyline_pts[i - 1]
            seg_len = _seg_len(prev, p)

            if in_tab:
                tab_remaining -= seg_len
                if tab_remaining <= 0:
                    # End tab — drop back to cut depth
                    in_tab = False
                    lines.append(self.feed(x=p[0], y=p[1], z=cut_z, f=feedrate))
                else:
                    lines.append(self.feed(x=p[0], y=p[1], z=tab_z, f=feedrate))
            else:
                dist_since_tab += seg_len
                if dist_since_tab >= spacing:
                    # Start tab — lift Z
                    in_tab = True
                    tab_remaining = tab_width
                    dist_since_tab = 0.0
                    lines.append(self.feed(x=p[0], y=p[1], z=tab_z, f=feedrate))
                else:
                    lines.append(self.feed(x=p[0], y=p[1], z=cut_z, f=feedrate))

        return lines

    # ------------------------------------------------------------------
    # Ramp entry
    # ------------------------------------------------------------------

    def ramp_entry(self, polyline_pts, start_z, end_z, feedrate=600.0,
                   max_ramp_angle_deg=3.0):
        """
        Generate a helical ramp entry move along the first segment of a toolpath.

        Instead of plunging straight down, the tool descends gradually along
        the cut path. If the first segment is too short for a full ramp, the
        ramp repeats over multiple segments.

        Args:
            polyline_pts:       list of (x, y) — the toolpath (2D)
            start_z:            float — Z to start descending from (e.g. 0.5 above surface)
            end_z:              float — target cutting Z
            feedrate:           float — ramp feedrate, mm/min
            max_ramp_angle_deg: float — maximum angle of descent (degrees)

        Returns:
            list of G-code strings for the ramp entry move
        """
        if len(polyline_pts) < 2:
            return [self.feed(z=end_z, f=feedrate)]

        depth = start_z - end_z
        if depth <= 0:
            return []

        # Max XY travel for a clean ramp at given angle
        ramp_len = depth / math.tan(math.radians(max_ramp_angle_deg))

        lines = []
        z = start_z
        xy_travelled = 0.0
        seg_idx = 0
        n = len(polyline_pts)

        while z > end_z and seg_idx < n - 1:
            p_start = polyline_pts[seg_idx]
            p_end   = polyline_pts[(seg_idx + 1) % n]
            seg_len = math.hypot(p_end[0] - p_start[0], p_end[1] - p_start[1])

            # How far can we descend over this segment?
            z_drop = seg_len * (depth / ramp_len)
            new_z = max(end_z, z - z_drop)
            lines.append(self.feed(x=p_end[0], y=p_end[1], z=new_z, f=feedrate))
            z = new_z
            xy_travelled += seg_len
            seg_idx += 1

            if z <= end_z:
                break

        return lines


# ---------------------------------------------------------------------------
# ShopBot post-processor
# ---------------------------------------------------------------------------

class ShopBotPost(GCodePost):
    """
    ShopBot SBP dialect.

    ShopBot uses: J3 (rapid 3-axis), M3 (move 3-axis), MS (set speed)
    """

    def header(self):
        return (
            "SA ; set absolute mode\n"
            "MS,100,60 ; set move/jog speeds (ipm)\n"
            "C6 ; spindle on"
        )

    def footer(self):
        return "C7 ; spindle off\nJ3,0,0,1 ; safe retract\nEnd ; end program"

    def rapid(self, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        parts = []
        if x is not None: parts.append(_fmt(x))
        if y is not None: parts.append(_fmt(y))
        if z is not None: parts.append(_fmt(z))
        return f"J3,{','.join(parts)}" if parts else ""

    def feed(self, f=None, **kwargs):
        x = kwargs.get("x")
        y = kwargs.get("y")
        z = kwargs.get("z")
        parts = []
        if x is not None: parts.append(_fmt(x))
        if y is not None: parts.append(_fmt(y))
        if z is not None: parts.append(_fmt(z))
        return f"M3,{','.join(parts)}" if parts else ""


# ---------------------------------------------------------------------------
# Backwards-compatible aliases (used in existing tests)
# ---------------------------------------------------------------------------
GCodePostProcessor = GCodePost
ShopBotPostProcessor = ShopBotPost
