from wake_word_detection import listen_for_wake_word
from voice_recognition import recognize_speech
from rasa_integration import process_command
from text_to_speech import speak_response
import simpleaudio as sa

def assistant_workflow():

    # play boot sound
    print("Playing boot sound...")
    wave_obj = sa.WaveObject.from_wave_file("boot.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

    # send greeting message to rasa
    response = process_command("wake up elisa")
    speak_response(response)  # Speak the response from Rasa

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
    response = process_command(command)
    speak_response(response)  # Speak the response from Rasa

# Start listening for the wake word
listen_for_wake_word(assistant_workflow)
