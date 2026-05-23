import asyncio                       # runs two coroutines concurrently
import websockets
import json 
import numpy as np
import sounddevice as sd                  # captures mic audio
import time 

from stt.vad import VAD
from config.settings import (
    DEEPGRAM_API_KEY,
    SAMPLE_RATE,
    CHUNK_SIZE,
    SILENCE_TRIGGER_SEC,
    SILENCE_THRESHOLD
)
# Deepgram streaming endpoint
# language=multi  → enables automatic multilingual detection
# English, French, Chinese, German all supported
DEEPGRAM_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=linear16"
    f"&sample_rate={SAMPLE_RATE}"
    "&language=multi"
    "&model=nova-2"
    "&punctuate=true"
    "&interim_results=true"
    "&vad_events=true"
)


class DeepgramSTT:
    def __init__(self):
        self.vad = VAD(
            sample_rate=SAMPLE_RATE,
            silence_threshold=SILENCE_THRESHOLD,
            silence_trigger_sec=SILENCE_TRIGGER_SEC
        )
        self.transcript_buffer = []  # accumulates final transcripts
        self.running = False

    async def _receive_transcripts(self, ws):
        """
        Coroutine: listens to incoming messages from Deepgram.
        Deepgram sends two types:
          - is_final: False  → partial transcript (still speaking)
          - is_final: True   → final transcript (word boundary confirmed)
        """
        async for message in ws:
            data = json.loads(message)

            # ignore non-transcript messages (metadata, VAD events)
            if data.get("type") != "Results":
                continue

            channel = data.get("channel", {})
            alternatives = channel.get("alternatives", [])

            if not alternatives:
                continue

            transcript = alternatives[0].get("transcript", "").strip()

            if not transcript:
                continue

            is_final = data.get("is_final", False)
            detected_language = data.get("metadata", {}).get("detected_language", "unknown")

            if is_final:
                print(f"\n[FINAL | lang: {detected_language}] {transcript}")
                self.transcript_buffer.append(transcript)
            else:
                # partial — print on same line, overwrite with \r
                print(f"  [partial] {transcript}", end="\r")

    async def _stream_audio(self, ws):
        """
        Coroutine: reads mic in chunks, runs VAD, sends speech to Deepgram.
        This is the core streaming loop.
        """
        audio_queue = asyncio.Queue()

        def mic_callback(indata, frames, time_info, status):
            """
            Called by sounddevice on every chunk.
            Runs in a separate thread — must use thread-safe queue.
            """
            audio_queue.put_nowait(indata.copy())

        # open mic stream
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            blocksize=CHUNK_SIZE,
            callback=mic_callback
        ):
            print("Listening... speak in English, French, Chinese, or German")
            print(f"Agent will respond after {SILENCE_TRIGGER_SEC}s of silence\n")

            agent_triggered = False

            while self.running:
                # get next chunk from queue
                chunk = await audio_queue.get()
                chunk_flat = chunk.flatten()

                # run VAD decision
                vad_result = self.vad.process_chunk(chunk_flat)

                if vad_result["barge_in"]:
                    print("\n[BARGE-IN detected] Person started speaking — agent should stop")
                    # In Week 3 you will wire this to stop TTS playback
                    # For now just print and keep listening
                    agent_triggered = False

                elif vad_result["trigger_agent"] and not agent_triggered:
                    agent_triggered = True
                    full_transcript = " ".join(self.transcript_buffer).strip()
                    self.transcript_buffer.clear()

                    if full_transcript:
                        print(f"\n[SILENCE {SILENCE_TRIGGER_SEC}s] Triggering agent...")
                        print(f"[FULL QUERY] {full_transcript}")
                        # In Week 3 this goes into the LLM queue
                        # For now just print

                elif vad_result["send_to_stt"]:
                    agent_triggered = False
                    # convert numpy array to bytes and send to Deepgram
                    await ws.send(chunk_flat.tobytes())

    async def run(self):
        """
        Opens WebSocket to Deepgram and runs both coroutines concurrently.
        _receive_transcripts and _stream_audio run in parallel using
        asyncio.gather — this is your first real async pipeline.
        """
        headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}
        self.running = True

        print("Connecting to Deepgram...")

        async with websockets.connect(DEEPGRAM_URL, additional_headers=headers) as ws:
            print("Connected.\n")
            # run both coroutines concurrently
            await asyncio.gather(
                self._receive_transcripts(ws),
                self._stream_audio(ws)
            )

    def stop(self):
        self.running = False