from typing import Optional, Protocol
import asyncio
import queue
import json

import sounddevice
import vosk

import config


vosk.SetLogLevel(-1)

class SpeechRecognizerDelegate(Protocol):
    def speech_recognizer_did_receive_final_result(self, result: str): pass
    def speech_recognizer_did_receive_partial_result(self, result: str): pass
    def speech_recognizer_did_receive_empty_result(self): pass

class SpeechRecognizer:

    delegate: SpeechRecognizerDelegate

    audioQueue: queue.Queue
    model: vosk.Model

    samplerate: int
    blocksize = 8000
    dtype = 'int16'
    channels = 1
    kaldiRecognizer: vosk.KaldiRecognizer

    lastResult: Optional[str] = ""
    lastPartialResult: str = ""

    is_recognizing = True
    _isListening = False

    def __init__(self, delegate: SpeechRecognizerDelegate):
        self.delegate = delegate
        
        self.samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        self.model = vosk.Model(config.vosk_model)
        self.audioQueue = queue.Queue()
        self.kaldiRecognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        
        self.parameters = {
            'samplerate': self.samplerate,
            'blocksize': self.blocksize,
            'dtype': self.dtype,
            'channels': self.channels,
            'callback': self.audioInputCallback
        }

    def audioInputCallback(self, indata, frames, time, status):
        if not self.is_recognizing: return
        self.audioQueue.put(bytes(indata))

    def stopListening(self):
        self._isListening = False
        self.audioQueue = queue.Queue()

    async def startListening(self):
        self._isListening = True

        with sounddevice.RawInputStream(**self.parameters):
            while self._isListening:

                await asyncio.sleep(0.1)
                data = self.audioQueue.get()

                if self.kaldiRecognizer.AcceptWaveform(data):
                    result = json.loads(self.kaldiRecognizer.Result())
                    if (string := result.get('text')) and string != self.lastResult:
                        self.lastResult = string
                        self.delegate.speech_recognizer_did_receive_final_result(string)
                    else:
                        self.lastResult = None
                        self.delegate.speech_recognizer_did_receive_empty_result()
                else:
                    result = json.loads(self.kaldiRecognizer.PartialResult())
                    if (string := result.get('partial')) and string != self.lastPartialResult:
                        self.lastPartialResult = string
                        self.delegate.speech_recognizer_did_receive_partial_result(string)
