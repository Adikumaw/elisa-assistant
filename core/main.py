from wake_word_detection import listen_for_wake_word
from voice_recognition import recognize_speech
from rasa_integration import process_command
from text_to_speech import speak_response
from websocket import create_ui_logger, ui_controller
import simpleaudio as sa
import os
import time

# Create UI logger for this module
ui_logger = create_ui_logger("Main")

def assistant_workflow():

    # ============================== PLAY BOOT SOUND AND GREETING =============================
    # Set UI to boot state
    ui_logger.set_state("boot")
    ui_logger.log_info("System booting...")
    # play boot sound before listening the command
    ui_logger.log_info("Playing boot sound...")
    print("Playing boot sound...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    boot_path = os.path.join(base_dir, "../audio/permanent/boot.wav").replace("\\", "/")
    try:
        sa.WaveObject.from_wave_file(boot_path).play().wait_done()
        # ui_logger.log_success("Boot sound completed")
    except Exception as e:
        ui_logger.log_error(f"Failed to play boot sound: {str(e)}")

    # =============================== GREETING =============================
    # Set UI to processing state for Rasa greeting
    ui_logger.set_state("processing")
    ui_logger.log_info("starting Greeting Sequence...")
    
    # Send greeting message to rasa
    try:
        responses, continue_conversation = process_command("wake up elisa")
        ui_logger.log_success(f"Received {len(responses)} responses from Rasa")
    except Exception as e:
        ui_logger.log_error(f"Failed to process greeting: {str(e)}")
        return
    
    # Set UI to speaking state
    ui_logger.set_state("speaking")
    # Speak all responses that rasa sent
    for i, response in enumerate(responses):
        ui_logger.log_info(f"Speaking response {i+1}: {response[:50]}{'...' if len(response) > 50 else ''}")
        try:
            speak_response(response)  # Speak each response
        except Exception as e:
            ui_logger.log_error(f"Failed to speak response: {str(e)}")

    ui_logger.log_success("Greeting sequence completed")

    # ================================ LISTEN FOR COMMAND =============================
    # Keep listening while the conversation is ongoing
    while True:

        # Set UI to listening state
        # Recognize speech after the wake word is detected
        # Give three chances to recognize the command
        command = None
        for attempt in range(3):
            ui_logger.log_info("Setting up Voice Recognition...")
            # ui_logger.log_info(f"Attempt {attempt + 1} to recognize command...")
            
            try:
                command = recognize_speech()
                if command is not None:
                    ui_logger.log_success(f"Command recognized: '{command}'")
                    break
                else:
                    ui_logger.log_warning(f"No speech detected on attempt {attempt + 1}")
                    if attempt < 2:  # Don't speak on last attempt
                        ui_logger.set_state("speaking")
                        ui_logger.log_info("Speaking retry message...")
                        speak_response("I couldn't hear you. Please try again.")
            except Exception as e:
                ui_logger.log_error(f"Error during speech recognition: {str(e)}")
        
        if command is None:
            ui_logger.log_error("Failed to recognize command after 3 attempts")
            ui_logger.set_state("speaking")
            speak_response("I'm sorry, I couldn't understand you. Please try again later.")
            continue
        
        # Set UI to processing state
        ui_logger.set_state("processing")
        ui_logger.log_info(f"Processing command with Rasa: '{command}'")
        
        # Process the recognized command with Rasa
        try:
            responses, continue_conversation = process_command(command)
            ui_logger.log_success(f"Rasa processed command, got {len(responses)} responses")
            ui_logger.log_info(f"Continue conversation: {continue_conversation}")
        except Exception as e:
            ui_logger.log_error(f"Failed to process command with Rasa: {str(e)}")
            continue
        
        # Set UI to speaking state
        ui_logger.set_state("speaking")
        
        # Speak all responses
        for i, response in enumerate(responses):
            ui_logger.log_info(f"Speaking response {i+1}: {response[:50]}{'...' if len(response) > 50 else ''}")
            try:
                speak_response(response)  # Speak each response
            except Exception as e:
                ui_logger.log_error(f"Failed to speak response: {str(e)}")
        
        if not continue_conversation:
            ui_logger.log_info("No further conversation needed - ending session")
            ui_logger.set_state("idle")
            break  # Exit loop if no further conversation is needed
        else:
            ui_logger.log_info("Conversation continuing...")


def main():
    """Main function to start the assistant with UI"""
    
    # Start the WebSocket server
    ui_logger.log_info("Starting Elisa Assistant...")
    ui_logger.log_info("Initializing WebSocket server...")
    
    try:
        server_thread = ui_controller.start_server(host="localhost", port=8765)
        ui_logger.log_success("WebSocket server started on ws://localhost:8765")
        ui_logger.log_info("Open the UI in your browser and refresh to connect")
        
        # Give server time to start
        time.sleep(2)
        
        # Start listening for the wake word with our workflow
        ui_logger.log_info("Starting wake word detection...")
        listen_for_wake_word(assistant_workflow)
        
    except Exception as e:
        ui_logger.log_error(f"Failed to start assistant: {str(e)}")
        raise

if __name__ == "__main__":
    main()