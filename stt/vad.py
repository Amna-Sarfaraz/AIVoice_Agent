import numpy as np
import time 

class VAD:
    def __init__(
            self,
            sample_rate=16000,
            silence_threshold=500,
            silence_trigger_sec=5.0
    ):
        self.sample_rate=sample_rate
        self.silence_threshold=silence_threshold
        self.silence_trigger_sec=silence_trigger_sec


        self.silence_start_time= None
        self.agent_speaking=False
        self.barge_in_detected=False

    def is_speech(self,audio_chunk:np.ndarray)->bool:
        """
        Check if chunk contains speech.
        amplitude = average absolute value of all samples in chunk.
        If it exceeds threshold, it is speech. Otherwise silence.
        """
        amplitude=np,abs(audio_chunk).mean()
        return amplitude >self.silence_threshold
    
    def Process_chunk(self,audio_chunk: np.ndarray)->dict:
         """
        Call this on every chunk.
        Returns a dict telling the caller what to do.
        """
         speech_detected=self.is_speech(audio_chunk)

          # --- barge-in detection ---
        # if agent is speaking and human starts talking again
         if self.agent_speaking and speech_detected:
            self.barge_in_detected=True
            return {"send_to_stt":True,
                    "trigger_agent":False,
                    "barge_in":True,
                    "silence_duration":0}
           # --- normal speech ---
         if speech_detected:
          self.silence_start_time=None # resset silence timer
         return{
              "send_to_stt":True,
              "trigger_agent": False,
              "barge_in":False,
               "silence_duration":0
         }
        # --- silence handling ---
         if self.silence_start_time is None:
          self.silence_start_time=time.time()
          silence_duration=time.time()-self.silence_start_time
          trigger=silence_duration > self.silence_trigger_sec
        
         return {
             "send_to_stt":False,
             "trigger_agent": trigger,
             "barge_in":False,
             "silence_duration":round(silence_duration,2)
        }
    def set_agent_speaking(self,speaking:bool):
         """Call this from orchestrator when TTS starts or stops."""
         self.agent_speaking=speaking
         self.barge_in_detected=False 