# Keep your action classes as is. No major changes are required for the actions themselves.
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import webbrowser
import wikipedia
import os
from utils import open_application, fetch_weather, get_user_location
from datetime import datetime
import random
from typing import Any, Text, Dict, List
from pynput.keyboard import Controller
import time



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
        term = tracker.get_slot("words")

        if term:
            try:
                # Fetch a short summary from Wikipedia
                meaning = wikipedia.summary(term, sentences=1)

                # Randomized responses
                responses = [
                    f"Here's what I found: {meaning}",
                    f"The word '{term}' means: {meaning}",
                    f"Ah, '{term}'! It means: {meaning}",
                    f"Let me tell you! '{term}' stands for: {meaning}",
                    f"Sure! '{term}' can be defined as: {meaning}",
                    f"'{term}'—that's an interesting word! It means: {meaning}"
                ]
                dispatcher.utter_message(json_message={"text": random.choice(responses), "continue": False})

                # Ask if user wants to know more
                dispatcher.utter_message(json_message={"text": "Would you like to read more details?",  "continue": True})

                SlotSet("last_word", term)

            except wikipedia.exceptions.DisambiguationError as e:
                dispatcher.utter_message(json_message={"text": f"'{term}' has multiple meanings. Can you be more specific?", "continue": False})
            except wikipedia.exceptions.PageError:
                dispatcher.utter_message(json_message={"text": f"Sorry, I couldn't find a definition for '{term}'.", "continue": False})

        else:
            # Randomized response when the word is missing
            fallback_responses = [
                "Could you please tell me the word you want the meaning of?",
                "I need a word to fetch its meaning. What do you want to know?",
                "Oops! I can't find a word. Can you provide one?",
                "Hmm, I need a word to look up. Please type it in!",
                "Give me a word, and I'll find its meaning for you!"
            ]
            dispatcher.utter_message(json_message={"text": random.choice(fallback_responses), "continue": False})

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