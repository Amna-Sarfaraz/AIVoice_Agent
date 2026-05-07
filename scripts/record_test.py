
import sounddevice as sd
import numpy as np
from scipy.io import wavfile        

# Define recording parameters
SAMPLE_RATE=16000  #capturing 16,000 pressure readings every second. Over 5 seconds that's 80,000 numbers. That array of 80,000 numbers
duration=5   #seconds to record
CHANNELS=1   # mono one- mic one recording

print("Starting recording...")

# Record audio for the specified duration
auido=sd.rec(
    frames=duration*SAMPLE_RATE,  # total number of samples to record
    samplerate=SAMPLE_RATE,  # how many samples per second)
    channels=CHANNELS,  # number of audio channels (mono)
    dtype='int16'  # data type for the audio samples (16-bit integers)
)

sd.wait()   #sd.rec() is non-blocking — it starts recording and immediately returns. The recording happens in a background thread. So right after it you need
# Confirm and Save

print("Recording complete. Saving to file...")
#wavfile.write takes three arguments: path, sample rate, and the numpy array. It handles all the .wav header formatting for you.
OUTPIUT_FILE="data/logs/recording.wav"
wavfile.write(OUTPIUT_FILE, SAMPLE_RATE, auido)
print(f"Audio saved to {OUTPIUT_FILE}")