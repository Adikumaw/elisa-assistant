from TTS.api import TTS
import simpleaudio as sa

def speak_response(response):
    # Initialize Coqui-TTS with a pre-trained model
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
    
    # Save the generated speech to a file
    output_file = "response.wav"
    tts.tts_to_file(text=response, file_path=output_file)
    
    # Play the generated speech
    wave_obj = sa.WaveObject.from_wave_file(output_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()

# # Example test
# if __name__ == "__main__":
#     speak_response("Hello! How can I assist you?")
