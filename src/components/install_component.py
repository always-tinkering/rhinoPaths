"""
rhinoPaths Installer Component
Paste into a Python 3 Script component in Rhino 8 Grasshopper.

HOW TO USE:
  Option A (recommended): Run this one terminal command instead:
      ~/.rhinocode/py39-rh8/bin/pip install -e ~/path/to/opencam-rhino8

  Option B: Wire a Boolean Toggle to 'run_install' input in the Script Editor,
            set it True, and this component will install everything automatically.
"""

import sys
import subprocess
import os

# In Rhino 8 new Script Editor: add input param named 'run_install' (bool, optional)
# Falls back to True if not wired (runs immediately)
try:
    _should_run = bool(run_install)
except NameError:
    _should_run = True  # no input wired → run immediately

def _find_project_root():
    """Find the rhinoPaths project root (the folder containing pyproject.toml)."""
    # Strategy 1: relative to this script's location
    this_file = os.path.abspath(__file__) if "__file__" in dir() else None
    if this_file:
        candidate = os.path.abspath(os.path.join(os.path.dirname(this_file), "..", ".."))
        if os.path.exists(os.path.join(candidate, "pyproject.toml")):
            return candidate

    # Strategy 2: well-known path (edit this if you cloned elsewhere)
    known = os.path.expanduser("~/antigravity/scratch/opencam-rhino8")
    if os.path.exists(os.path.join(known, "pyproject.toml")):
        return known

    # Strategy 3: search up from current working directory
    cwd = os.getcwd()
    for _ in range(6):
        if os.path.exists(os.path.join(cwd, "pyproject.toml")):
            return cwd
        cwd = os.path.dirname(cwd)

    return None

def install():
    log = [f"Python: {sys.executable}  ({sys.version.split()[0]})"]
    pip = os.path.join(os.path.dirname(sys.executable), "pip3")
    if not os.path.exists(pip):
        pip = os.path.join(os.path.dirname(sys.executable), "pip")
    if not os.path.exists(pip):
        pip = [sys.executable, "-m", "pip"]
    else:
        pip = [pip]

    # Step 1: Install deps
    log.append("Installing numpy + clipper2...")
    r = subprocess.run(pip + ["install", "numpy", "clipper2"],
                       capture_output=True, text=True)
    log.append(r.stdout.strip() or "(no output)")
    if r.returncode != 0:
        log.append(f"  STDERR: {r.stderr.strip()}")

    # Step 2: Install rhinopaths in editable mode
    root = _find_project_root()
    if root:
        log.append(f"Installing rhinopaths from: {root}")
        r = subprocess.run(pip + ["install", "-e", root],
                           capture_output=True, text=True)
        log.append(r.stdout.strip() or "(no output)")
        if r.returncode != 0:
            log.append(f"  STDERR: {r.stderr.strip()}")
    else:
        log.append("ERROR: Could not find project root (pyproject.toml).")
        log.append("Run manually: ~/.rhinocode/py39-rh8/bin/pip install -e <path>")

    # Verify
    try:
        import rhinopaths
        log.append("✅ import rhinopaths OK")
    except ImportError as e:
        log.append(f"❌ import rhinopaths FAILED: {e}")

    return "\n".join(log)

if _should_run:
    print(install())
else:
    print("rhinoPaths Installer ready. Set run_install=True to execute.")
