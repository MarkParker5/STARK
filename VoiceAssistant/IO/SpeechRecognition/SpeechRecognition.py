from typing import Callable, Optional
from abc import ABC, abstractmethod
import asyncio
import os, sys
import queue
import json

import sounddevice
import vosk

import config

vosk.SetLogLevel(-1)

class SpeechRecognizerDelegate(ABC):
    @abstractmethod
    def speechRecognizerReceiveFinalResult(self, result: str): pass

    @abstractmethod
    def speechRecognizerReceivePartialResult(self, result: str): pass

    @abstractmethod
    def speechRecognizerReceiveEmptyResult(self): pass


class SpeechRecognizer:

    delegate: SpeechRecognizerDelegate

    lastResult: Optional[str] = ""
    lastPartialResult: str = ""

    isRecognizing = True
    _isListening = False

    audioQueue = queue.Queue()
    model = vosk.Model(config.vosk_model)

    samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
    blocksize = 8000
    dtype = 'int16'
    channels = 1
    kaldiRecognizer = vosk.KaldiRecognizer(model, samplerate)

    def __init__(self, delegate: SpeechRecognizerDelegate):
        self.delegate = delegate
        self.parameters = {
            'samplerate': self.samplerate,
            'blocksize': self.blocksize,
            'dtype': self.dtype,
            'channels': self.channels,
            'callback': self.audioInputCallback
        }

    def audioInputCallback(self, indata, frames, time, status):
        if not self.isRecognizing: return
        self.audioQueue.put(bytes(indata))

    def stopListening(self):
        self._isListening = False
        audioQueue = queue.Queue()

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
                        self.delegate.speechRecognizerReceiveFinalResult(string)
                    else:
                        self.lastResult = None
                        self.delegate.speechRecognizerReceiveEmptyResult()
                else:
                    result = json.loads(self.kaldiRecognizer.PartialResult())
                    if (string := result.get('partial')) and string != self.lastPartialResult:
                        self.lastPartialResult = string
                        self.delegate.speechRecognizerReceivePartialResult(result['partial'])
