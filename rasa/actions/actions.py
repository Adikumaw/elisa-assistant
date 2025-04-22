# Keep your action classes as is. No major changes are required for the actions themselves.
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import webbrowser
import wikipedia
import os
from utils.app_launcher import open_application
from utils.weather_info import fetch_weather, get_user_location
from utils.reminder_manager import load_reminders, save_reminders, schedule_reminder, remove_reminder
from utils.response_loader import get_random_response
from datetime import datetime, timedelta, timezone
import random
from typing import Any, Text, Dict, List
from pynput.keyboard import Controller
import time
import difflib


class ActionOpenApp(Action):
    def name(self) -> str:
        return "action_open_app"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        app_name = tracker.get_slot("app_name")
        
        try:
            if app_name:
                # lowercase the app name to ensure consistency
                result = open_application(app_name.lower())
                dispatcher.utter_message(json_message={"text": result, "continue": False})
            else:
                dispatcher.utter_message(json_message={"text": "Please provide a valid application name.", "continue": False})
        except Exception as e:
            dispatcher.utter_message(json_message={"text": f"Failed to open {app_name}. Error: {str(e)}", "continue": False})
        
        return []

class ActionSearchFirefox(Action):
    def name(self) -> str:
        return "action_search_firefox"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        query = tracker.get_slot("query")

        # Collect all query entities into a single query
        entity_queries = [
            entity.get("value") for entity in tracker.latest_message.get("entities", [])
            if entity.get("entity") == "query"
        ]
        
        if entity_queries:
            query = " ".join(entity_queries).strip()
        
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            dispatcher.utter_message(json_message={"text": f"Searching for '{query}' on Firefox...", "continue": False})
        else:
            dispatcher.utter_message(json_message={"text": "I couldn't find a query to search for.", "continue": False})
        
        return []

class ActionCreateFile(Action):
    def name(self) -> str:
        return "action_create_file"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        file_name = tracker.get_slot("file_name")
        directory = os.getcwd()
        
        if file_name:
            try:
                with open(os.path.join(directory, file_name), 'w') as file:
                    file.write("New file created.")
                dispatcher.utter_message(json_message={"text": f"Created file: {file_name}", "continue": False})
            except Exception as e:
                dispatcher.utter_message(json_message={"text": f"Failed to create file: {file_name}. Error: {str(e)}", "continue": False})
        else:
            dispatcher.utter_message(json_message={"text": "I need a valid file name to create a file.", "continue": False})
        
        return []

class ActionTypeWhatISay(Action):
    def name(self) -> Text:
        return "action_type_what_i_say"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        keyboard = Controller()
        text_to_type = next(tracker.get_latest_entity_values("text"), None)

        # Collect all text entities into a single text
        entity_queries = [
            entity.get("value") for entity in tracker.latest_message.get("entities", [])
            if entity.get("entity") == "text"
        ]
        
        if entity_queries:
            text_to_type = " ".join(entity_queries).strip()

        if text_to_type:
            dispatcher.utter_message(json_message={"text": f"Typing: {text_to_type}", "continue": False})

            # Simulate real typing effect
            for char in text_to_type:
                keyboard.type(char)
                time.sleep(0.05)  # Adjust typing speed if needed
            
            keyboard.press("\n")  # Simulates pressing Enter after typing
            keyboard.release("\n")

        else:
            dispatcher.utter_message(json_message={"text": "I didn't catch what you want me to type.", "continue": False})

        return []

class ActionCurrentDateTime(Action):
    def name(self) -> str:
        return "action_current_date_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get current date and time in a friendly format
        current_time = datetime.now().strftime("%A, %d %B %Y - %I:%M %p")

        # Define multiple response variations
        responses = [
            f"The current date and time is {current_time}.",
            f"Right now, it's {current_time}.",
            f"As per my clock, it's {current_time}.",
            f"Currently, it's {current_time}. Hope that helps!",
            f"Time check! It's {current_time}.",
            f"Hey! It's {current_time}. Anything else?"
        ]

        # Choose a random response
        dispatcher.utter_message(json_message={"text": random.choice(responses), "continue": False})
        return []

class ActionMeaningOf(Action):
    def name(self) -> str:
        return "action_meaning_of"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        word = tracker.get_slot("words")

        if word:
            try:
                # Fetch a short summary from Wikipedia
                meaning = wikipedia.summary(word, sentences=1)

                # Randomized response for the meaning
                dispatcher.utter_message(json_message=get_random_response("action_meaning_of", "success", word=word, meaning=meaning))

                # Ask if user wants to know more
                dispatcher.utter_message(json_message=get_random_response("action_meaning_of", "offer_deep_dive"))

                SlotSet("last_word", word)

            except wikipedia.exceptions.DisambiguationError as e:
                dispatcher.utter_message(json_message=get_random_response("action_meaning_of", "disambiguation"))
            except wikipedia.exceptions.PageError:
                dispatcher.utter_message(json_message=get_random_response("action_meaning_of", "not_found"))

        else:
            # Randomized response when the word is missing
            dispatcher.utter_message(json_message=get_random_response("action_meaning_of", "missing_word"))

        return []

class ActionOpenBrowser(Action):
    def name(self) -> str:
        return "action_open_browser"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        term = tracker.get_slot("words")

        if term:
            url = f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}"
            webbrowser.open(url)
            dispatcher.utter_message(json_message={"text": f"Opening more details about '{term}' in your browser.", "continue": False})
        else:
            dispatcher.utter_message(json_message={"text": "I don't remember which word you wanted. Could you say it again?", "continue": False})

        return []

class ActionWeatherUpdate(Action):
    def name(self) -> Text:
        return "action_weather_update"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        # Extract location entity from user input
        location = None
        for entity in tracker.latest_message.get("entities", []):
            if entity.get("entity") == "GPE":
                location = entity.get("value")
                break

        # If location is not provided, get the user's current location
        if not location:
            location = get_user_location()
            if not location:
                dispatcher.utter_message(text="I couldn't detect your location. Please provide a city name.")
                return []

        # Fetch weather details
        weather_data = fetch_weather(location)

        if weather_data:
            temp = weather_data["main"]["temp"]
            condition = weather_data["weather"][0]["description"]
            dispatcher.utter_message(text=f"The current weather in {location} is {condition} with a temperature of {temp}°C.")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't fetch the weather for {location}. Please try again later.")

        return []
    
class ActionSetReminder(Action):
    def name(self) -> Text:
        return "action_set_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = tracker.get_slot("task_name") or next(tracker.get_latest_entity_values("task_name"), None)
        time_value = tracker.get_slot("time") or next(tracker.get_latest_entity_values("time"), None)

        if not task or not time_value:
            dispatcher.utter_message(text="I need both the task and the time for the reminder.")
            return []

        try:
            reminder_time = datetime.fromisoformat(time_value)
        except Exception as e:
            print(f"[Reminder Parse Error] Couldn't parse time: {time_value}, error: {e}")
            dispatcher.utter_message(text="I couldn't understand the time you mentioned. Try saying 'remind me at 5pm'.")
            return []

        reminders = load_reminders()
        reminders[task] = reminder_time.isoformat()
        save_reminders(reminders)

        # Schedule reminders
        ten_minutes_before = reminder_time - timedelta(minutes=10)
        schedule_reminder(task, ten_minutes_before.isoformat(), early=True)
        schedule_reminder(task, reminder_time.isoformat(), early=False)

        dispatcher.utter_message(
            text=f"✅ Reminder set for '{task}' at {reminder_time.strftime('%I:%M %p')}."
        )
        return []

class ActionListReminders(Action):
    def name(self) -> Text:
        return "action_list_reminders"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now(timezone.utc)  # make `now` timezone-aware in UTC
        reminders = load_reminders()
        active_reminders = {}

        for task, time_str in reminders.items():
            try:
                reminder_time = datetime.fromisoformat(time_str)

                # Ensure both are timezone-aware
                if reminder_time.tzinfo is None:
                    reminder_time = reminder_time.replace(tzinfo=timezone.utc)

                if reminder_time > now:
                    active_reminders[task] = time_str
            except Exception as e:
                print(f"[Reminder Check] Failed to parse time for {task}: {e}")


        # Overwrite with filtered active ones
        save_reminders(active_reminders)

        if not active_reminders:
            dispatcher.utter_message(text="You don't have any active reminders.")
            return []

        message = "Here are your current reminders:\n"
        for task, time in active_reminders.items():
            formatted_time = datetime.fromisoformat(time).strftime('%I:%M %p')
            message += f"• {task} at {formatted_time}\n"

        dispatcher.utter_message(text=message)
        dispatcher.utter_message(text="Would you like to update the time for a task or remove one?")
        return []

class ActionRemoveReminder(Action):
    def name(self) -> Text:
        return "action_remove_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = next(tracker.get_latest_entity_values("task_name"), None)
        reminders = load_reminders()

        if not reminders:
            dispatcher.utter_message(text="You don't have any reminders set.")
            return []

        task_names = list(reminders.keys())
        best_match = difflib.get_close_matches(task, task_names, n=1, cutoff=0.5)

        if best_match:
            matched_task = best_match[0]

            # ❌ Remove from reminder list
            reminders.pop(matched_task)
            save_reminders(reminders)

            # ❌ Remove scheduled jobs
            remove_reminder(matched_task)

            dispatcher.utter_message(text=f"✅ Removed the reminder for '{matched_task}'.")
        else:
            dispatcher.utter_message(text="❌ Couldn't find any matching reminder.")

        return []

class ActionUpdateReminder(Action):
    def name(self) -> Text:
        return "action_update_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        task = next(tracker.get_latest_entity_values("task_name"), None)
        new_time = tracker.get_slot("time")

        reminders = load_reminders()

        if not task or not new_time:
            dispatcher.utter_message(text="Please specify both the task and the new time.")
            return []

        # 🔍 Fuzzy match task
        task_names = list(reminders.keys())
        best_match = difflib.get_close_matches(task, task_names, n=1, cutoff=0.5)

        if not best_match:
            dispatcher.utter_message(text="Couldn't find a matching reminder to update.")
            return []

        matched_task = best_match[0]

        try:
            updated_time = datetime.fromisoformat(new_time)
        except Exception:
            # updated_time = datetime.now() + timedelta(minutes=30)
            dispatcher.utter_message(text="Couldn't understand the new time. Please try again.")
            return []

        # 🔁 Update in the reminder JSON
        reminders[matched_task] = updated_time.isoformat()
        save_reminders(reminders)

        # 📆 Re-schedule the reminder with dual notifications
        schedule_reminder(matched_task, (updated_time - timedelta(minutes=10)).isoformat(), early=True)
        schedule_reminder(matched_task, updated_time.isoformat(), early=False)

        dispatcher.utter_message(
            text=f"🕒 Reminder for '{matched_task}' updated to {updated_time.strftime('%Y-%m-%d %H:%M')}."
        )
        return []
