import speech_recognition as sr
import simpleaudio as sa

def recognize_speech():
    recognizer = sr.Recognizer()
    
    # Use default microphone
    with sr.Microphone() as source:
        try:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust based on background noise

            print("Listening for command...")
            recognizer.pause_threshold = 2  # Adjust to prevent early cutoff
            recognizer.non_speaking_duration = 0.5  # Small pauses allowed
            recognizer.energy_threshold = 400  # Set manually if needed

            # play beep sound
            wave_obj = sa.WaveObject.from_wave_file("beep.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()

            # Capture audio with timeout & phrase limit
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

            print("Recognizing speech...")
            command = recognizer.recognize_google(audio)
            print(f"Recognized command: {command}")
            return command

        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# # Example test
# if __name__ == "__main__":
#     command = recognize_speech()
#     if command:
#         print(f"Recognized command: {command}")
#     else:
#         print("No command recognized.")
