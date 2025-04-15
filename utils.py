import subprocess
import os
import glob
from difflib import get_close_matches
import threading
from pytz import timezone
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import json
from datetime import datetime, timedelta, timezone
from scheduler_core import scheduler  # ✅ Now this works cleanly
import sys
from TTS.api import TTS
import simpleaudio as sa
import logging

REMINDER_FILE = "reminders.json"

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


def notify(response):

    logging.getLogger("TTS").setLevel(logging.ERROR)  # Suppress info/debug logs
    logging.getLogger("numba").setLevel(logging.WARNING)  # Suppress Numba warnings
    tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False)

    output_file = "response.wav"

    # Redirect stdout and stderr to suppress logs
    with open(os.devnull, 'w') as f:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = f, f
        try:
            tts.tts_to_file(text=response, file_path=output_file)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr  # Restore stdout and stderr

    # Play the generated speech
    sa.WaveObject.from_wave_file("notification.wav").play().wait_done()
    sa.WaveObject.from_wave_file(output_file).play().wait_done()
    # play_obj = wave_obj.play()
    # play_obj.wait_done()

def remind(task_name, early=False):
    msg = f"⏰ Reminder: '{task_name}'"
    if early:
        msg = f"⚠️ Upcoming in 10 mins: '{task_name}'"
        notify("Upcoming in 10 mins: " + task_name)
    else:
        notify("Reminder: " + task_name)
    print(msg)
    # You can add system notification or audio here too

    # Display a system notification (Linux)
    subprocess.run(['notify-send', 'Reminder', msg])
    
    # Optionally, play a sound
    # subprocess.run(['aplay', '/path/to/sound.wav'])

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return {}
    with open(REMINDER_FILE, "r") as file:
        return json.load(file)

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as file:
        json.dump(reminders, file, indent=4)

def schedule_reminder(task_name, iso_time_str, early=False):
    reminder_time = datetime.fromisoformat(iso_time_str)

    if reminder_time.tzinfo is None:
        reminder_time = reminder_time.replace(tzinfo=timezone("Asia/Kolkata"))

    job_id = f"{task_name}_{'early' if early else 'on_time'}"

    # Remove old duplicate if exists
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        remind,  # Now using the global `remind` function
        trigger='date',
        run_date=reminder_time,
        id=job_id,
        replace_existing=True,
        args=[task_name, early]  # Pass task_name and early as arguments
    )

# Example Usage
# print(open_application("settings"))  # Will open 'firefox-developer-edition' if it's the best match.
