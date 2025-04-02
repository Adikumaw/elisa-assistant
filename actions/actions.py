# Keep your action classes as is. No major changes are required for the actions themselves.
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import subprocess
import webbrowser
import os

class ActionOpenApp(Action):
    def name(self) -> str:
        return "action_open_app"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        app_name = tracker.get_slot("app_name")
        
        try:
            if app_name.lower() == "chrome":
                subprocess.Popen(["google-chrome"])
                dispatcher.utter_message(text=f"Opening {app_name}...")
            elif app_name.lower() == "firefox":
                subprocess.Popen(["firefox"])
                dispatcher.utter_message(text=f"Opening {app_name}...")
            elif app_name.lower() == "notepad":
                subprocess.Popen(["notepad"])
                dispatcher.utter_message(text=f"Opening {app_name}...")
            else:
                dispatcher.utter_message(text=f"Sorry, I don't know how to open {app_name}.")
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

class ActionTypeInApp(Action):
    def name(self) -> str:
        return "action_type_in_app"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        app_name = tracker.get_slot("app_name")
        
        if app_name:
            dispatcher.utter_message(text=f"Starting to type in {app_name}...")
            # Simulate typing action (could be extended with pyautogui or other tools)
        else:
            dispatcher.utter_message(text="Please provide a valid application name to type in.")
        
        return []
