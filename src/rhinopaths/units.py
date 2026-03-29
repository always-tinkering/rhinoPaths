"""
rhinoPaths — mm/inch conversion helpers and unit-aware value types.
"""

MM_PER_INCH = 25.4
INCH_PER_MM = 1.0 / 25.4


def mm_to_inch(value):
    """Convert millimetres to inches."""
    return value * INCH_PER_MM


def inch_to_mm(value):
    """Convert inches to millimetres."""
    return value * MM_PER_INCH


def to_mm(value, unit="mm"):
    """
    Coerce a value to millimetres.

    Args:
        value: float
        unit: str — "mm" or "inch" / "in"

    Returns:
        float in mm
    """
    if unit in ("inch", "in", "inches"):
        return inch_to_mm(value)
    return float(value)


def to_inch(value, unit="mm"):
    """
    Coerce a value to inches.

    Args:
        value: float
        unit: str — "mm" or "inch" / "in"

    Returns:
        float in inches
    """
    if unit in ("inch", "in", "inches"):
        return float(value)
    return mm_to_inch(value)


def normalise(value, from_unit, to_unit):
    """
    Generic unit conversion.

    Args:
        value: float
        from_unit: str ("mm" | "inch")
        to_unit:   str ("mm" | "inch")

    Returns:
        float in to_unit
    """
    mm_value = to_mm(value, from_unit)
    return to_inch(mm_value) if to_unit in ("inch", "in", "inches") else mm_value
