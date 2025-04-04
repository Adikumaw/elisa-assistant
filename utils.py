import subprocess
import os
import glob
from difflib import get_close_matches
import requests

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

def fetch_weather(location: str) :
    """Fetches weather data from OpenWeatherMap API"""
    api_key = "b80e877092745687574e38e26b612a42"  # Replace with your OpenWeatherMap API key
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key, "units": "metric"}

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_user_location() :
    """Gets the user's current location based on IP address"""
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown")
    except Exception as e:
        print(f"Error fetching user location: {e}")
    return None

# Example Usage
# print(open_application("settings"))  # Will open 'firefox-developer-edition' if it's the best match.
