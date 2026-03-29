"""
AUTOMATED INSTALLER - Grasshopper Python 3 Node
Paste this code into a fresh Python 3 Component in Rhino 8 Grasshopper.

Inputs:
    RunInstall (bool) : Set true (e.g. via boolean toggle) to run the installer
Outputs:
    Log (str) : Installation log output
"""

import sys
import subprocess
import os

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
except ImportError:
    pass  # We catch this so the IDE doesn't complain, but it will be available in GH

def get_gh_doc_path():
    """Helper to get the current Grasshopper document folder"""
    if sc.doc and hasattr(sc.doc, 'Path') and sc.doc.Path:
        return os.path.dirname(sc.doc.Path)
    return None

def install_dependencies():
    log = []
    
    # Get Python executable path used by Rhino 8 (typically CPython 3.9)
    python_exe = sys.executable
    log.append(f"Using Python: {python_exe}")
    
    # 1. Install 'clipper2' from PyPI
    log.append("Installing clipper2 from PyPI...")
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "clipper2", "numpy"], 
            capture_output=True, text=True
        )
        log.append(result.stdout)
        if result.stderr:
            log.append(result.stderr)
    except Exception as e:
        log.append(f"Error installing dependencies: {e}")
        
    # 2. Local pip install -e . for our rhinopaths library
    gh_folder = get_gh_doc_path()
    
    if not gh_folder:
        log.append("ERROR: Save the Grasshopper file first so we can find the relative 'src' directory!")
        return "\n".join(log)
        
    # Assuming the repository structure (gh doc is in definitions/)
    repo_root = os.path.abspath(os.path.join(gh_folder, ".."))
    log.append(f"Installing local rhinopaths package from: {repo_root}")
    
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "-e", repo_root],
            capture_output=True, text=True
        )
        log.append(result.stdout)
        if result.stderr:
            log.append(result.stderr)
    except Exception as e:
        log.append(f"Error installing local package: {e}")
        
    log.append("Installation routine complete. You can now use rhinoPaths components.")
    return "\n".join(log)

# Ensure the inputs map to the variables
if "RunInstall" in globals() and RunInstall:
    Log = install_dependencies()
else:
    Log = "Set RunInstall to True to execute installation."
