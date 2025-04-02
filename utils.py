import subprocess
import os
import glob

def get_installed_packages():
    """Fetch list of installed packages using pacman."""
    result = subprocess.run(["pacman", "-Q"], capture_output=True, text=True)
    return [line.split()[0] for line in result.stdout.strip().split("\n")]

def get_gui_apps():
    """Fetch GUI applications from .desktop entries."""
    desktop_files = glob.glob("/usr/share/applications/*.desktop")
    return [os.path.basename(file).replace(".desktop", "") for file in desktop_files]


def open_application(app_name):
    """Open an application using kstart with full path."""
    try:
        result = subprocess.run(["/usr/bin/kstart", app_name], capture_output=True, text=True)
        return f"Opening {app_name} via KRunner...\n{result.stdout}"
    except FileNotFoundError:
        return "Error: kstart not found. Make sure you're using KDE."
    except Exception as e:
        return f"Failed to open {app_name}. Error: {str(e)}"

# Example Usage
print(open_application("spotify"))  # Try "firefox" or "vlc"
