import pyaudio
import wave
import webrtcvad
import collections
import subprocess
import simpleaudio as sa
import uuid
import os

# === CONFIGURABLE SETTINGS ===
RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
FRAME_DURATION = 30  # in ms
CHUNK = int(RATE * FRAME_DURATION / 1000)
MAX_SILENCE_FRAMES = int(1000 / FRAME_DURATION * 1.0)  # 1 sec silence
VAD_AGGRESSIVENESS = 2  # 0-3, 3 is most aggressive

# Paths (based on running from core/)
BASE_DIR = os.path.dirname(__file__)
AUDIO_TEMP_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'audio', 'temporary'))
AUDIO_PERM_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'audio', 'permanent'))
WHISPER_CLI = os.path.abspath(os.path.join(BASE_DIR, '..', 'whisper.cpp', 'build', 'bin', 'whisper-cli'))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'whisper.cpp', 'models', 'ggml-medium.bin'))
BEEP_PATH = os.path.join(AUDIO_PERM_DIR, 'beep.wav')

# Ensure TEMP_DIR exists
os.makedirs(AUDIO_TEMP_DIR, exist_ok=True)

# === DEBUG PRINT FUNCTION ===
def debug(msg):
    print(f"🔍 DEBUG: {msg}")


# === PLAY BEEP SOUND ===
def play_beep(path=BEEP_PATH):
    debug("Playing beep sound")
    try:
        sa.WaveObject.from_wave_file(path).play().wait_done()
    except Exception as e:
        print(f"⚠️ Beep sound failed: {e}")


# === RECORD AUDIO USING VAD ===
def vad_record(audio_temp_path):
    debug("Setting up VAD and PyAudio")
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    ring_buffer = collections.deque(maxlen=MAX_SILENCE_FRAMES)
    triggered = False
    debug("Listening started. Waiting for speech...")

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        is_speech = vad.is_speech(data, RATE)

        if not triggered:
            ring_buffer.append((data, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.8 * ring_buffer.maxlen:
                debug("Speech detected! Starting to record...")
                triggered = True
                frames.extend([f for f, s in ring_buffer])
                ring_buffer.clear()
        else:
            frames.append(data)
            ring_buffer.append((data, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                debug("Silence detected. Ending recording...")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()
    debug("Saving audio to {audio_temp_path}")

    wf = wave.open(audio_temp_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    debug("Audio saved successfully")


def recognize_with_whisper_cpp(audio_path, model_path=MODEL_PATH):
    debug(f"Running whisper.cpp with model {model_path} on file {audio_path}")
    
    # whisper_cli_path = os.path.abspath("./whisper.cpp/build/bin/whisper-cli")
    output_txt_path = audio_path + ".txt"

    command = [
        WHISPER_CLI,
        "-m", model_path,
        "-f", audio_path,
        "-otxt",         # Output to text file
        "-l", "en",      # Language
        "-nt"            # No timestamps
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        debug("Transcription completed by whisper-cli")

        if os.path.exists(output_txt_path):
            with open(output_txt_path, "r") as f:
                transcription = f.read().strip()
            os.remove(output_txt_path)  # Optional: clean up after reading
            debug("Transcription read and cleaned up")
            return transcription
        else:
            debug("❌ Transcription file not found")
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ whisper-cli failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return None



# === MAIN FUNCTION TO RECORD AND RECOGNIZE ===
def recognize_speech():
    audio_temp_filename = f"temp_{uuid.uuid4().hex}.wav"
    audio_temp_path = os.path.join(AUDIO_TEMP_DIR, audio_temp_filename)
    debug("=== Speech recognition started ===")

    try:
        play_beep()
        vad_record(audio_temp_path)
        result = recognize_with_whisper_cpp(audio_temp_path)
        if result:
            print(f"✅ Recognized: {result}")
        else:
            print("❌ No recognizable speech.")
        return result
    except Exception as e:
        print(f"⚠️ Error during recognition: {e}")
        return None
    finally:
        if os.path.exists(audio_temp_path):
            os.remove(audio_temp_path)
            debug("Temporary audio file removed")


# # === DIRECT RUNNER ===
# if __name__ == "__main__":
#     print("🔊 Starting speech recognizer...")
#     command = recognize_speech()
#     if command:
#         print(f"\n🗣️ Final Output: {command}")
#     else:
#         print("\n🚫 No speech detected or recognized.")
