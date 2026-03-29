COMMON_BOOTSTRAP = """import sys as _sys, os as _os

def _get_rhinopaths_path():
    # 1. Check local dev environment (for authors/contributors)
    _dev = _os.path.normpath(_os.path.expanduser("~/antigravity/scratch/opencam-rhino8/src"))
    if _os.path.exists(_os.path.join(_dev, "rhinopaths")):
        return _dev
        
    # 2. Check standard Rhino scripts folder
    _scripts_mac = _os.path.expanduser("~/Library/Application Support/McNeel/Rhinoceros/8.0/scripts")
    _scripts_win = _os.path.expanduser("~\\\\AppData\\\\Roaming\\\\McNeel\\\\Rhinoceros\\\\8.0\\\\scripts")
    if _os.path.exists(_os.path.join(_scripts_mac, "rhinopaths")): return _scripts_mac
    if _os.path.exists(_os.path.join(_scripts_win, "rhinopaths")): return _scripts_win

    # 3. Check Yak package folders (installed via package manager)
    import glob
    _yak_mac = _os.path.expanduser("~/Library/Application Support/McNeel/Rhinoceros/packages/8.0/rhinoPaths/*/src")
    _yak_win = _os.path.expanduser("~\\\\AppData\\\\Roaming\\\\McNeel\\\\Rhinoceros\\\\packages\\\\8.0\\\\rhinoPaths\\\\*\\\\src")
    
    for p in glob.glob(_yak_mac) + glob.glob(_yak_win):
        if _os.path.exists(p):
            return p
            
    return None

_SRC = _get_rhinopaths_path()
if _SRC and _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

_RHINO_SITE = _os.path.expanduser("~/.rhinocode/py39-rh8/lib/python3.9/site-packages")
if _os.path.exists(_RHINO_SITE) and _RHINO_SITE not in _sys.path:
    _sys.path.insert(0, _RHINO_SITE)
"""
