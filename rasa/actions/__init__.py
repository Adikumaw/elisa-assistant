# actions/__init__.py
from utils.reminder_manager import load_reminders, schedule_reminder
from datetime import datetime, timezone

# Re-schedule all existing reminders
try:
    reminders = load_reminders()
    for task, time_str in reminders.items():
        reminder_time = datetime.fromisoformat(time_str)
        if reminder_time > datetime.now(reminder_time.tzinfo or timezone.utc):
            schedule_reminder(task, time_str)
except Exception as e:
    print(f"[Reminder Restore Error] {e}")
