from typing import Generator
import time
import anyio
from asyncer._main import TaskGroup
from stark.interfaces.protocols import SpeechRecognizer
from stark.models.transcription import Transcription, KaldiMBR, KaldiWord
from stark.interfaces.protocols import SpeechRecognizerDelegate
from stark.general.localisation import Localizer


class SpeechRecognizerRelay:
    
    language_code: str = ''
    localizer: Localizer
    
    _speech_recognizers: list[SpeechRecognizer]
    _current_transcription: Transcription | None = None
    _delegate: SpeechRecognizerDelegate | None = None
    _is_recognizing: bool = False
    
    def __init__(self, speech_recognizers: list[SpeechRecognizer], localizer: Localizer):
        for recognizer in speech_recognizers:
            assert isinstance(recognizer, SpeechRecognizer)
        assert isinstance(localizer, Localizer)
        assert {sr.language_code for sr in speech_recognizers} == localizer.languages, 'Languages of SpeechRecognizers must be equal to Localizer languages'
        self.speech_recognizers = speech_recognizers
        self.localizer = localizer
        
    # properties
        
    @property
    def is_recognizing(self) -> bool:
        return self._is_recognizing
    
    @is_recognizing.setter
    def is_recognizing(self, is_recognizing: bool):
        self._is_recognizing = is_recognizing
        
        for recognizer in self.speech_recognizers:
            recognizer.is_recognizing = is_recognizing
        
    @property
    def delegate(self) -> SpeechRecognizerDelegate | None:
        return self._delegate
    
    @delegate.setter
    def delegate(self, delegate: SpeechRecognizerDelegate | None):
        assert delegate is None or isinstance(delegate, SpeechRecognizerDelegate)
        self._delegate = delegate
        
    # methods
    
    def start_speech_recognizers(self, task_group: TaskGroup):
        self.is_recognizing = True
        for recognizer in self.speech_recognizers:    
            recognizer.delegate = self
            task_group.soonify(recognizer.start_listening)()
            
    # SpeechRecognizer Protocol Implmenetation
    
    async def start_listening(self):
        assert NotImplementedError('Start listening in relay is not implemented, use `start_speech_recognizers` instead')
        
    def stop_listening(self):
        for recognizer in self.speech_recognizers:
            recognizer.stop_listening()
        
    def microphone_did_receive_sample(self, data):
        if not self.is_recognizing:
            return
        for recognizer in self.speech_recognizers:
            recognizer.microphone_did_receive_sample(data)
            
    def reset(self):
        for recognizer in self.speech_recognizers:
            recognizer.reset()
        
    # SpeechRecognizerDelegate Protocol Implmenetation
    
    async def speech_recognizer_did_receive_final_transcription(self, speech_recognizer: SpeechRecognizer, transcription: Transcription): 
        # NOTE: this executes for each SR, be aware of duplicating output

        current_transcription = self._current_transcription or transcription
        self._current_transcription = current_transcription
        
        current_transcription.origins.update(transcription.origins) # TODO: append instead of override, update timestamps if needed
        
        start_time = time.monotonic()
        timeout = 2 # TODO: make configurable
        languages = set(sr.language_code for sr in self.speech_recognizers)
        
        # wait other languages
        while current_transcription.origins.keys() != languages or time.monotonic() - start_time < timeout:
            await anyio.sleep(0.01)
        
        # avoid duplicating because SRs calling this method concurrently
        if not self._current_transcription:
            return
        
        # use recognizable dictioanry
        
        for language, origin in current_transcription.origins.items():
            for key, string in self.localizer.recognizable[language].strings.items():
                origin.replace(key, string.value)
        
        # TODO: add suggestions
        
        # build best confedence
        
        current_transcription.best = self._build_best_confidence(set(current_transcription.origins.values()))
        current_transcription.best.language_code = 'best'
        
        # finish
            
        self.current_transcription = None # reset for next recognition and exit concurrent calls\
        
        for recognizer in self.speech_recognizers:
            recognizer.reset()
        
        if delegate := self.delegate:
            await delegate.speech_recognizer_did_receive_final_transcription(self, current_transcription)
    
    async def speech_recognizer_did_receive_partial_result(self, speech_recognizer: SpeechRecognizer, result: str): 
        pass
    
    async def speech_recognizer_did_receive_empty_result(self, speech_recognizer: SpeechRecognizer): 
        pass
    
    # Private
    
    def _build_best_confidence(self, tracks: set[KaldiMBR], until: float | None = None) -> KaldiMBR:
        if not tracks: return KaldiMBR()
        
        best = KaldiMBR()
        
        while tracks:
            # check tracks are not empty within `until`
            
            tracks = set(filter(lambda track: track.result and (until is None or track.result[0].middle < until), tracks))
            
            if not tracks:
                break
            
            # reqursive part: go down to min by removing max and limiting to end=min(max.end, until) where until is previous level end
            
            longest = max(tracks, key = lambda track: track.result[0].end if until is None or track.result[0].middle < until else 0)
            end = min(longest.result[0].end, until) if not until is None else longest.result[0].end
            other = self._build_best_confidence(tracks - {longest}, until = end)
            
            # Compare two tracks
            
            base_word = longest.result.pop(0)
            alternative_words = list(self._pop_words_until_time(other, end))
            
            if not alternative_words:
                best.result.append(base_word)
                continue
            
            # build complex
            complex_alternative = KaldiWord(word = '', start = base_word.start, end = base_word.end)
            complex_alternative.word = ' '.join(word.word for word in alternative_words)
            complex_alternative.end = max(word.end for word in alternative_words)
            complex_alternative.start = min(word.start for word in alternative_words)
            complex_alternative.conf = sum(word.conf or 0 for word in alternative_words) / len(alternative_words) # TODO: conf * dutation instead of AVG
            complex_alternative.language_code = alternative_words[0].language_code # TODO: improve
            
            if complex_alternative.conf == base_word.conf and base_word.language_code == 'ru-RU': # attempt of native language priority TODO: fix
                best.result.append(base_word)
            elif(base_word.conf or 0) > (complex_alternative.conf or 0): # TODO: conf * dutation instead of AVG
                best.result.append(base_word)
            else:
                best.result.append(complex_alternative)
            
        best.text = ' '.join(word.word for word in best.result)
            
        return best
    
    def _pop_words_until_time(self, track: KaldiMBR, time: float) -> Generator[KaldiWord, None, None]:
        for word in track.result:
            if word.middle > time:
                break
            track.result.remove(word)
            yield word
