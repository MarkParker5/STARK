from typing import Optional
import os
import urllib.request
import zipfile
import anyio
import json
from queue import Queue, Empty

import sounddevice
import vosk

from .protocols import SpeechRecognizer, SpeechRecognizerDelegate


vosk.SetLogLevel(-1)

class VoskSpeechRecognizer(SpeechRecognizer):

    _delegate: SpeechRecognizerDelegate | None = None

    audio_queue: Queue
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

    def __init__(self, model_url: str, delegate: SpeechRecognizerDelegate | None = None):
        downloads = 'downloads'
        model_path = downloads + '/' + model_url.split('/')[-1].replace('.zip', '')
        zip_path = model_path + '.zip'
        
        if not os.path.isdir('downloads'):
            os.mkdir('downloads')

        if not os.path.isdir(model_path):
            print('VOSK: Downloading model...')
            urllib.request.urlretrieve(model_url, zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            zip_file.extractall(downloads)
            os.remove(zip_path)
            print('VOSK: Model downloaded!')
        
        self.delegate = delegate
        self.samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        self.model = vosk.Model(model_path)
        self.audio_queue = Queue()
        self.kaldiRecognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        
    @property
    def delegate(self):
        return self._delegate
    
    @delegate.setter
    def delegate(self, delegate: SpeechRecognizerDelegate | None):
        assert delegate is None or isinstance(delegate, SpeechRecognizerDelegate)
        self._delegate = delegate
        
    @property
    def sounddevice_parameters(self):
        return {
            'samplerate': self.samplerate,
            'blocksize': self.blocksize,
            'dtype': self.dtype,
            'channels': self.channels,
            'callback': self._audio_input_callback
        }

    def stop_listening(self):
        self._is_listening = False
        self.audio_queue = Queue()

    async def start_listening(self):
        self._is_listening = True

        with sounddevice.RawInputStream(**self.sounddevice_parameters):
            while self._is_listening:
                try:
                    if data := self.audio_queue.get(block = False):
                        await self._transcribe(data)
                except Empty:
                    pass
                await anyio.sleep(0.05)
                
    async def _transcribe(self, data):
        delegate = self.delegate
        if not delegate: return
        
        if self.kaldiRecognizer.AcceptWaveform(data):
            result = json.loads(self.kaldiRecognizer.Result())
            if (string := result.get('text')) and string != self.last_result:
                self.last_result = string
                await delegate.speech_recognizer_did_receive_final_result(string)
            else:
                self.last_result = None
                await delegate.speech_recognizer_did_receive_empty_result()
        else:
            result = json.loads(self.kaldiRecognizer.PartialResult())
            if (string := result.get('partial')) and string != self.last_partial_result:
                self.last_partial_result = string
                await delegate.speech_recognizer_did_receive_partial_result(string)

    def _audio_input_callback(self, indata, frames, time, status):
        if not self.is_recognizing: return
        self.audio_queue.put(bytes(indata))