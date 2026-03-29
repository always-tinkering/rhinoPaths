COMMON_BOOTSTRAP = """import sys as _sys, os as _os
_SRC = _os.path.normpath(_os.path.expanduser("~/antigravity/scratch/opencam-rhino8/src"))
if _os.path.exists(_SRC) and _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

_RHINO_SITE = _os.path.expanduser("~/.rhinocode/py39-rh8/lib/python3.9/site-packages")
if _os.path.exists(_RHINO_SITE) and _RHINO_SITE not in _sys.path:
    _sys.path.insert(0, _RHINO_SITE)
"""
