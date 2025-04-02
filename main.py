from wake_word_detection import listen_for_wake_word
from voice_recognition import recognize_speech
from rasa_integration import process_command
from text_to_speech import speak_response

def assistant_workflow(command):
    print(f"Processing command: {command}")
    if command is None:
        print("No command recognized.")
        return  # Exit if no command is recognized

    # Process the recognized command with Rasa
    response = process_command(command)
    speak_response(response)  # Speak the response from Rasa

# Start listening for the wake word
listen_for_wake_word(assistant_workflow)
