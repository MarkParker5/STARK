from typing import Optional, cast
from datetime import datetime, timedelta
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

    samplerate: int
    blocksize = 8000
    dtype = 'int16'
    channels = 1
    kaldiRecognizer: vosk.KaldiRecognizer

    last_result: Optional[str] = ''
    last_partial_result: str = ''
    last_partial_update_time: Optional[datetime] = None

    is_recognizing = True
    _is_listening = False
    
    _stored_speakers: dict[int, list[int]] = {}
    _speaker_trashold = 0.75

    def __init__(self, model_url: str, speaker_model_url: str | None = None):
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
        
        self.audio_queue = Queue()
        self.samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        vosk_model = vosk.Model(model_path)
        speaker_model = vosk.SpkModel(speaker_model_path) if speaker_model_path else None
        self.kaldiRecognizer = vosk.KaldiRecognizer(vosk_model, self.samplerate)
        if speaker_model_url:
            self.kaldiRecognizer.SetSpkModel(speaker_model)
        
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
        if self._is_listening: return

        self.last_partial_result = ''
        self.last_partial_update_time = None
        self._is_listening = True

        with sounddevice.RawInputStream(**self.sounddevice_parameters):
            while self._is_listening:
                try:
                    if data := self.audio_queue.get(block = False):
                        await self._transcribe(data)
                except Empty:
                    pass
                await anyio.sleep(0.01)
                
    async def _transcribe(self, data):
        delegate = self.delegate
        if not delegate: return
        
        if self.kaldiRecognizer.AcceptWaveform(data):
            self.last_partial_update_time = None
            result = json.loads(self.kaldiRecognizer.Result())
            
            if (string := result.get('text')):
                self.last_result = string
                await delegate.speech_recognizer_did_receive_final_result(string)
            else:
                self.last_result = None
                await delegate.speech_recognizer_did_receive_empty_result()
            
            # if spk := result.get('spk'):
            #     speaker, similarity = self._get_speaker(spk)
            #     print(f'\nSpeaker: {speaker} ({similarity * 100:.2f}%)\n')
                
        else:
            result = json.loads(self.kaldiRecognizer.PartialResult())
            
            if (string := result.get('partial')) and string != self.last_partial_result:
                self.last_partial_result = string
                self.last_partial_update_time = datetime.now()
                await delegate.speech_recognizer_did_receive_partial_result(string)
                
        # Check for partial results timeout 
        # TODO: (was bug with stucked partial results, need to check again)
        # TODO: check last string didn't change all timeout
        # if not self.last_partial_update_time: 
        #     return

        # if datetime.now() - self.last_partial_update_time > timedelta(seconds = 1):
        #     print('\nPartial timeout')
        #     self.last_partial_update_time = None
            
        #     if self.last_partial_result:
        #         await delegate.speech_recognizer_did_receive_final_result(self.last_partial_result)
        #         self.kaldiRecognizer.Reset() # avoid duplicate results
        #         self.last_partial_result = ''

    def _audio_input_callback(self, indata, frames, time, status):
        if not self.is_recognizing: return
        self.audio_queue.put(bytes(indata))
        
    def _get_speaker(self, vector: list[int]) -> tuple[int, float]:
        # TODO: search Is not working good, need to improve the algorithm
        
        matched_speaker_id = None
        best_similarity = -1.0
        
        for speaker_id, vec in self._stored_speakers.items():
            similarity = self._cosine_similarity(vector, vec)
            if similarity > best_similarity:
                best_similarity = similarity
                matched_speaker_id = speaker_id
                
        if not best_similarity or best_similarity < self._speaker_trashold:
            matched_speaker_id = len(self._stored_speakers)
            self._stored_speakers[matched_speaker_id] = vector
            print(f'New speaker: {matched_speaker_id}, similarity: {best_similarity * 100:.2f}%')
            best_similarity = 1
            
        return cast(int, matched_speaker_id), best_similarity
        
    def _cosine_similarity(self, vector_a, vector_b) -> float:
        dot_product = sum(a*b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a*a for a in vector_a) ** 0.5
        norm_b = sum(b*b for b in vector_b) ** 0.5
        return dot_product / (norm_a * norm_b)
