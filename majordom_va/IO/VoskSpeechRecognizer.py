from typing import Optional
import asyncio
import queue
import json

import sounddevice
import vosk

import config
from .protocols import SpeechRecognizer, SpeechRecognizerDelegate


vosk.SetLogLevel(-1)

class VoskSpeechRecognizer(SpeechRecognizer):

    delegate: SpeechRecognizerDelegate

    audio_queue: queue.Queue
    model: vosk.Model

    samplerate: int
    blocksize = 8000
    dtype = 'int16'
    channels = 1
    kaldiRecognizer: vosk.KaldiRecognizer

    last_result: Optional[str] = ""
    last_partial_result: str = ""

    is_recognizing = True
    _is_listening = False

    def __init__(self):
        self.samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        self.model = vosk.Model(config.vosk_model)
        self.audio_queue = queue.Queue()
        self.kaldiRecognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        
        self.parameters = {
            'samplerate': self.samplerate,
            'blocksize': self.blocksize,
            'dtype': self.dtype,
            'channels': self.channels,
            'callback': self._audio_input_callback
        }

    def stop_listening(self):
        self._is_listening = False
        self.audio_queue = queue.Queue()

    async def start_listening(self):
        self._is_listening = True

        with sounddevice.RawInputStream(**self.parameters):
            while self._is_listening:

                await asyncio.sleep(0.05)
                data = self.audio_queue.get()

                if self.kaldiRecognizer.AcceptWaveform(data):
                    result = json.loads(self.kaldiRecognizer.Result())
                    if (string := result.get('text')) and string != self.last_result:
                        self.last_result = string
                        self.delegate.speech_recognizer_did_receive_final_result(string)
                    else:
                        self.last_result = None
                        self.delegate.speech_recognizer_did_receive_empty_result()
                else:
                    result = json.loads(self.kaldiRecognizer.PartialResult())
                    if (string := result.get('partial')) and string != self.last_partial_result:
                        self.last_partial_result = string
                        self.delegate.speech_recognizer_did_receive_partial_result(string)

    def _audio_input_callback(self, indata, frames, time, status):
        if not self.is_recognizing: return
        self.audio_queue.put(bytes(indata))