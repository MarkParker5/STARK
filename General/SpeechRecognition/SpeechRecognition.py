from typing import Callable
import os, sys
import json
import queue

import sounddevice
import vosk

import config

vosk.SetLogLevel(-1)

class SpeechRecognizer:
    didReceivePartialResult: Callable[[str], None] = lambda self, _: None
    didReceiveFinalResult: Callable[[str], None] = lambda self, _: None

    _isListening = False

    audioQueue = queue.Queue()
    model = vosk.Model(config.vosk_model)

    samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
    blocksize = 8000
    dtype = 'int16'
    channels = 1
    kaldiRecognizer = vosk.KaldiRecognizer(model, samplerate)

    def audioInputCallback(self, indata, frames, time, status):
        self.audioQueue.put(bytes(indata))

    def stopListening(self):
        self._isListening = False

    def startListening(self):
        self._isListening = True

        callback = lambda indata, frames, time, status: self.audioInputCallback(indata, frames, time, status)
        kwargs = {
            'samplerate': self.samplerate,
            'blocksize': self.blocksize,
            'dtype': self.dtype,
            'channels': self.channels,
            'callback': callback
        }

        with sounddevice.RawInputStream(**kwargs):
            while self._isListening:
                data = self.audioQueue.get()

                if self.kaldiRecognizer.AcceptWaveform(data):
                    result = json.loads(self.kaldiRecognizer.Result())
                    self.didReceiveFinalResult(result['text'])
                else:
                    result = json.loads(self.kaldiRecognizer.PartialResult())
                    self.didReceivePartialResult(result['partial'])
