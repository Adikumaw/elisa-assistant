from TTS.api import TTS
import simpleaudio as sa
import logging
import os
import sys
import json
import subprocess
from datetime import datetime
from pytz import timezone
from scheduler_core import scheduler  # ✅ Now this works cleanly


REMINDER_FILE = "reminders.json"

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

def remove_reminder(task_name: str):
    """Removes both early and on-time reminders from the scheduler by task_name."""
    removed = False
    for suffix in ["early", "on_time"]:
        job_id = f"{task_name}_{suffix}"
        job = scheduler.get_job(job_id)
        if job:
            scheduler.remove_job(job_id)
            print(f"[Scheduler] Removed job: {job_id}")
            removed = True
    return removed