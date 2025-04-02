import sounddevice as sd
import numpy as np

# Record a short clip to test microphone input
fs = 44100  # Sample rate
duration = 5  # seconds

print("Recording...")
audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
sd.wait()
print("Recording finished.")

# Check if audio data contains any sound
if np.any(audio_data):
    print("Microphone is working!")
else:
    print("Microphone is not picking up sound.")
