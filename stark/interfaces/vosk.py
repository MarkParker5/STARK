import os
import json
import zipfile
import urllib.request
from typing import Optional, cast
from queue import Queue, Empty
from datetime import datetime

import anyio
import sounddevice
import vosk

from stark.models.transcription import Transcription, KaldiMBR, KaldiResult, ValidationError
from .protocols import SpeechRecognizer, SpeechRecognizerDelegate


vosk.SetLogLevel(-1)

class VoskSpeechRecognizer(SpeechRecognizer):

    is_recognizing = True
    language_code: str
    samplerate: int

    _delegate: SpeechRecognizerDelegate | None = None
    _is_listening = False
    _audio_queue: Queue # TODO: typing
    _kaldiRecognizer: vosk.KaldiRecognizer
    _last_partial_result: str = ''
    _last_partial_update_time: Optional[datetime] = None

    def __init__(self, language_code: str, model_url: str, speaker_model_url: str | None = None, samplerate: int | None = None):
        self.language_code = language_code
        self.samplerate = samplerate or int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        
        downloads = 'downloads'
        model_path = downloads + '/' + model_url.split('/')[-1].replace('.zip', '')
        zip_path = model_path + '.zip'
        speaker_model_path = downloads + '/' + speaker_model_url.split('/')[-1].replace('.zip', '') if speaker_model_url else None
        
        if not os.path.isdir('downloads'):
            os.mkdir('downloads')

        if not os.path.isdir(model_path):
            print('VOSK: Downloading model...')
            urllib.request.urlretrieve(model_url, zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            zip_file.extractall(downloads)
            os.remove(zip_path)
            print('VOSK: Model downloaded!')
            
        if speaker_model_url and not os.path.isdir(cast(str, speaker_model_path)):
            print('VOSK: Downloading speaker model...')
            urllib.request.urlretrieve(speaker_model_url, zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            zip_file.extractall(downloads)
            os.remove(zip_path)
            print('VOSK: Speaker model downloaded!')
        
        self._audio_queue = Queue()
        
        vosk_model = vosk.Model(model_path)
        speaker_model = vosk.SpkModel(speaker_model_path) if speaker_model_path else None
        
        self._kaldiRecognizer = vosk.KaldiRecognizer(vosk_model, self.samplerate)
        self._kaldiRecognizer.SetMaxAlternatives(0) # 0 (default) returns KaldiMBR; 1+ returns KaldiResult (with bad confidence implementation)
        self._kaldiRecognizer.SetWords(True) # needs to calculate MBR average confidence; (default: False)
        
        if speaker_model_url:
            self._kaldiRecognizer.SetSpkModel(speaker_model)
        
    @property
    def delegate(self):
        return self._delegate
    
    @delegate.setter
    def delegate(self, delegate: SpeechRecognizerDelegate | None):
        assert delegate is None or isinstance(delegate, SpeechRecognizerDelegate)
        self._delegate = delegate
        
    # SpeechRecognizer Protocol Implmenetation

    def stop_listening(self):
        self._is_listening = False
        self._audio_queue = Queue()

    async def start_listening(self):
        if self._is_listening: return

        self._last_partial_result = ''
        self._last_partial_update_time = None
        self._is_listening = True
        
        while self._is_listening:
            await anyio.sleep(0.01)
            try:
                if data := self._audio_queue.get(block = False):
                    await self._transcribe(data)
            except Empty:
                pass
            
    def microphone_did_receive_sample(self, data):
        self._audio_queue.put(data)
        
    def reset(self):
        self._kaldiRecognizer.Reset()
        
    # Private
                
    async def _transcribe(self, data):
        delegate = self.delegate
        if not delegate: return
        
        if self._kaldiRecognizer.AcceptWaveform(data):
            self._last_partial_update_time = None
            raw_json = self._kaldiRecognizer.Result()
            
            try:
                result = KaldiMBR.parse_raw(raw_json)
                result.language_code = self.language_code
                
                for word in result.result:
                    word.language_code = self.language_code
                    
                transcription = Transcription(
                    best = result,
                    origins = {
                        self.language_code: result
                    }
                )
                
                await delegate.speech_recognizer_did_receive_final_transcription(self, transcription)
                
            except ValidationError as e:
                # print(e)
                await delegate.speech_recognizer_did_receive_empty_result(self)
                # try:
                #     result = KaldiResult.parse_raw(raw_json)
                #     transcription = result.alternatives[0]
                #     text = transcription.text
                # except ValidationError:
                #     text = json.loads(raw_json).get('text')    
        else:
            partial = json.loads(self._kaldiRecognizer.PartialResult())
            # partial always returns {"partial": "..."}
            if (string := partial.get('partial')) and string != self._last_partial_result:
                self._last_partial_result = string
                self._last_partial_update_time = datetime.now()
                await delegate.speech_recognizer_did_receive_partial_result(self, string)
