import os                                 # os is a Python standard library module that lets your Python code talk to the operating system — Windows, Linux, or Mac — underneath it.
from dotenv import load_dotenv

load_dotenv("config/.env")

# Audio
SAMPLE_RATE=16000
CHUNK_SIZE=3200
CHANNELS=1

# VAD
SILENCE_THRESHOLD=500
SILENCE_TRIGGER_SEC=5.0


# API KEY
DEEPGRAM_API_KEY=os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY=os.getenv("ELEVENLABS_API_KEY")
