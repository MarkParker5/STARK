import json
import logging
import os
import urllib.request
import zipfile
from datetime import datetime
from queue import Empty, Queue
from typing import Optional, cast

import anyio
import sounddevice
import vosk
from pydantic import BaseModel, Field, ValidationError

from .protocols import SpeechRecognizer, SpeechRecognizerDelegate

logger = logging.getLogger(__name__)

vosk.SetLogLevel(-1)

class KaldiTranscriptionWord(BaseModel):
    word: str
    start: float
    end: float
    conf: float | None = None # only for KaldiMBR

class KaldiMBR(BaseModel):
    text: str
    result: list[KaldiTranscriptionWord] = Field(default_factory = list)
    spk: list[float]
    spk_frames: int

    @property
    def confidence(self):
        return sum(word.conf for word in self.result) / len(self.result)

class KaldiTranscription(BaseModel):
    text: str
    result: list[KaldiTranscriptionWord] = Field(default_factory = list)
    confidence: float

class KaldiResult(BaseModel):
    alternatives: list[KaldiTranscription]

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
            logger.info('VOSK: Downloading model...')
            urllib.request.urlretrieve(model_url, zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            zip_file.extractall(downloads)
            os.remove(zip_path)
            logger.info('VOSK: Model downloaded!')

        if speaker_model_url and not os.path.isdir(cast(str, speaker_model_path)):
            logger.info('VOSK: Downloading speaker model...')
            urllib.request.urlretrieve(speaker_model_url, zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            zip_file.extractall(downloads)
            os.remove(zip_path)
            logger.info('VOSK: Speaker model downloaded!')

        self.audio_queue = Queue()
        self.samplerate = int(sounddevice.query_devices(kind = 'input')['default_samplerate'])
        vosk_model = vosk.Model(model_path)
        speaker_model = vosk.SpkModel(speaker_model_path) if speaker_model_path else None
        self.kaldiRecognizer = vosk.KaldiRecognizer(vosk_model, self.samplerate)
        self.kaldiRecognizer.SetMaxAlternatives(0) # 0 (default) returns KaldiMBR; 1+ returns KaldiResult (with bad confidence implementation)
        self.kaldiRecognizer.SetWords(True) # needs to calculate MBR average confidence; (default: False)
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
            raw_json = self.kaldiRecognizer.Result()
            text: str | None = None

            try:
                result = KaldiMBR.parse_raw(raw_json)
                text = result.text
                # print('\nConfidence:', result.confidence) # TODO: log or  os.getenv("STARK_VOICE_CLI", "0") == "1"
            except ValidationError:
                try:
                    result = KaldiResult.parse_raw(raw_json)
                    transcription = result.alternatives[0]
                    text = transcription.text
                except ValidationError:
                    text = json.loads(raw_json).get('text')

            if text:
                # if result.spk:
                #     speaker, similarity = self._get_speaker(result.spk)
                #     print(f'\nSpeaker: {speaker} ({similarity * 100:.2f}%)\n') # TODO: log or  os.getenv("STARK_VOICE_CLI", "0") == "1"

                self.last_result = text
                await delegate.speech_recognizer_did_receive_final_result(text)
            else:
                self.last_result = None
                await delegate.speech_recognizer_did_receive_empty_result()

        else:
            result = json.loads(self.kaldiRecognizer.PartialResult())
            # partial always returns {"partial": "..."}
            if (string := result.get('partial')) and string != self.last_partial_result:
                self.last_partial_result = string
                self.last_partial_update_time = datetime.now()
                await delegate.speech_recognizer_did_receive_partial_result(string)

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
            # print(f'New speaker: {matched_speaker_id}, similarity: {best_similarity * 100:.2f}%') # TODO: log or  os.getenv("STARK_VOICE_CLI", "0") == "1"
            best_similarity = 1

        return cast(int, matched_speaker_id), best_similarity

    def _cosine_similarity(self, vector_a, vector_b) -> float:
        dot_product = sum(a*b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a*a for a in vector_a) ** 0.5
        norm_b = sum(b*b for b in vector_b) ** 0.5
        return dot_product / (norm_a * norm_b)
