import sys
import os
from TTS.api import TTS
import simpleaudio as sa
import logging


def speak_response(response):

    logging.getLogger("TTS").setLevel(logging.ERROR)  # Suppress info/debug logs
    logging.getLogger("numba").setLevel(logging.WARNING)  # Suppress Numba warnings
    tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False)

    output_file = "response.wav"

    # Redirect stdout and stderr to suppress logs
    with open(os.devnull, 'w') as f:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = f, f
        try:
            tts.tts_to_file(text=response, file_path=output_file)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr  # Restore stdout and stderr

    # Play the generated speech
    wave_obj = sa.WaveObject.from_wave_file(output_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()
