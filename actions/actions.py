# Keep your action classes as is. No major changes are required for the actions themselves.
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import webbrowser
import wikipedia
import os
from utils import open_application
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
                result = open_application(app_name)
                dispatcher.utter_message(text=result)
            else:
                dispatcher.utter_message(text="Please provide a valid application name.")
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to open {app_name}. Error: {str(e)}")
        
        return []

class ActionSearchFirefox(Action):
    def name(self) -> str:
        return "action_search_firefox"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        query = tracker.get_slot("query")
        
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            dispatcher.utter_message(text=f"Searching for '{query}' on Firefox...")
        else:
            dispatcher.utter_message(text="I couldn't find a query to search for.")
        
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
                dispatcher.utter_message(text=f"Created file: {file_name}")
            except Exception as e:
                dispatcher.utter_message(text=f"Failed to create file: {file_name}. Error: {str(e)}")
        else:
            dispatcher.utter_message(text="I need a valid file name to create a file.")
        
        return []

class ActionTypeWhatISay(Action):
    def name(self) -> Text:
        return "action_type_what_i_say"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        keyboard = Controller()
        text_to_type = next(tracker.get_latest_entity_values("text"), None)

        if text_to_type:
            dispatcher.utter_message(f"Typing: {text_to_type}")

            # Simulate real typing effect
            for char in text_to_type:
                keyboard.type(char)
                time.sleep(0.05)  # Adjust typing speed if needed
            
            keyboard.press("\n")  # Simulates pressing Enter after typing
            keyboard.release("\n")

        else:
            dispatcher.utter_message("I didn't catch what you want me to type.")

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
        dispatcher.utter_message(text=random.choice(responses))
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
                dispatcher.utter_message(text=random.choice(responses))

            except wikipedia.exceptions.DisambiguationError as e:
                dispatcher.utter_message(text=f"'{term}' has multiple meanings. Can you be more specific?")
            except wikipedia.exceptions.PageError:
                dispatcher.utter_message(text=f"Sorry, I couldn't find a definition for '{term}'.")

        else:
            # Randomized response when the word is missing
            fallback_responses = [
                "Could you please tell me the word you want the meaning of?",
                "I need a word to fetch its meaning. What do you want to know?",
                "Oops! I can't find a word. Can you provide one?",
                "Hmm, I need a word to look up. Please type it in!",
                "Give me a word, and I'll find its meaning for you!"
            ]
            dispatcher.utter_message(text=random.choice(fallback_responses))

        return []
