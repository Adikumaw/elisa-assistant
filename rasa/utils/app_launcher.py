import subprocess
import os
import glob
from difflib import get_close_matches

def get_installed_gui_apps():
    """Fetch GUI applications from .desktop entries."""
    desktop_files = glob.glob("/usr/share/applications/*.desktop")
    app_names = [os.path.basename(file).replace(".desktop", "") for file in desktop_files]
    return app_names

def find_best_match(app_name, installed_apps):
    """Find the closest matching app name using fuzzy matching."""
    matches = get_close_matches(app_name.lower(), [app.lower() for app in installed_apps], n=1, cutoff=0.5)
    if matches:
        # Return the original casing of the closest match
        for app in installed_apps:
            if app.lower() == matches[0]:
                return app
    return None

def open_application(app_name):
    """Open an application by finding the closest matching name."""
    installed_apps = get_installed_gui_apps()
    best_match = find_best_match(app_name, installed_apps)

    if best_match:
        subprocess.run(["kstart", best_match])
        return f"Opening {best_match} via KRunner..."
    else:
        return f"Error: No matching application found for '{app_name}'."