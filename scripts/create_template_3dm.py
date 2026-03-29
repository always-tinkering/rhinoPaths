"""
scripts/create_template_3dm.py
rhinoPaths — run this inside the Rhino 8 Python Script Editor to create
the standard CNC template file with pre-configured layers.

Usage inside Rhino:
    RunPythonScript  →  select this file
    or drag-and-drop onto the Rhino viewport

Layers created:
    BOUNDARY    – outer stock boundary (orange)
    TOOLPATH    – computed toolpath curves (cyan)
    ISLANDS     – pocket islands / bosses (magenta)
    HOLES       – drill circles (yellow)
    ENGRAVE     – engraving curves (green)
    DOGBONE     – modified dogbone curves (white)
    STOCK       – stock volume / bounding box (grey, locked)
    OUTPUT      – exported G-code path annotation (red)
"""

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing


def _rgb(r, g, b):
    return System.Drawing.Color.FromArgb(r, g, b)


LAYER_CONFIG = [
    # (name,         color_rgb,          locked)
    ("BOUNDARY",     _rgb(255, 140,   0), False),  # orange
    ("TOOLPATH",     _rgb(  0, 220, 220), False),  # cyan
    ("ISLANDS",      _rgb(220,   0, 220), False),  # magenta
    ("HOLES",        _rgb(255, 220,   0), False),  # yellow
    ("ENGRAVE",      _rgb( 80, 200,  80), False),  # green
    ("DOGBONE",      _rgb(240, 240, 240), False),  # near-white
    ("STOCK",        _rgb(160, 160, 160), True ),  # grey, locked
    ("OUTPUT",       _rgb(220,  40,  40), False),  # red
]


def create_layers():
    doc = sc.doc
    for name, color, locked in LAYER_CONFIG:
        idx = doc.Layers.Find(name, True)
        if idx < 0:
            layer = Rhino.DocObjects.Layer()
            layer.Name    = name
            layer.Color   = color
            layer.IsLocked = locked
            doc.Layers.Add(layer)
            print(f"  Created layer: {name}")
        else:
            # Update colour on existing layer
            doc.Layers[idx].Color = color
            print(f"  Updated layer: {name}")


def set_document_units():
    """Set document units to millimetres."""
    Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem = Rhino.UnitSystem.Millimeters
    print("  Units set to Millimetres")


def add_title_text():
    """Add an informational text annotation at the origin."""
    plane = Rhino.Geometry.Plane.WorldXY
    txt = Rhino.Geometry.TextEntity()
    txt.Plane = plane
    txt.PlainText = "rhinoPaths CNC Template\nSet BOUNDARY layer active before drawing."
    txt.TextHeight = 5.0
    sc.doc.Objects.AddText(txt)


if __name__ == "__main__":
    print("rhinoPaths: creating CNC template layers...")
    set_document_units()
    create_layers()
    add_title_text()
    sc.doc.Views.Redraw()
    print("Done. Save as rhinoPaths_template.3dm")
