from wake_word_detection import listen_for_wake_word
from voice_recognition import recognize_speech
from rasa_integration import process_command
from text_to_speech import speak_response
import simpleaudio as sa
import os

def assistant_workflow():

    # play boot sound
    print("Playing boot sound...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    boot_path = os.path.join(base_dir, "../audio/permanent/boot.wav").replace("\\", "/")
    sa.WaveObject.from_wave_file(boot_path).play().wait_done()

    # send greeting message to rasa
    responses, continue_conversation = process_command("wake up elisa")
    # Speak all responses
    for response in responses:
        speak_response(response)  # Speak each response

    # Keep listening while the conversation is ongoing
    while True:
        # Recognize speech after the wake word is detected
        # give three chances to recognize the command
        for attempt in range(3):
            print(f"Attempt {attempt + 1} to recognize command...")
            command = recognize_speech()
            if command is not None:
                break
            else:
                print("Retrying...")
                speak_response("I couldn't hear you. Please try again.")

        # Process the recognized command with Rasa
        responses, continue_conversation = process_command(command)

        for response in responses:
            speak_response(response)  # Speak each response
        
        if not continue_conversation:
            print("No further conversation needed.")
            break  # Exit loop if no further conversation is needed

# Start listening for the wake word
listen_for_wake_word(assistant_workflow)
