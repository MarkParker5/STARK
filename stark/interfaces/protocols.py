from __future__ import annotations
from typing import Protocol, runtime_checkable
from stark.models.transcription import Transcription


@runtime_checkable
class SpeechRecognizerDelegate(Protocol):
    async def speech_recognizer_did_receive_final_transcription(self, speech_recognizer: SpeechRecognizer, transcription: Transcription): pass
    async def speech_recognizer_did_receive_partial_result(self, speech_recognizer: SpeechRecognizer, result: str): pass
    async def speech_recognizer_did_receive_empty_result(self, speech_recognizer: SpeechRecognizer): pass
   
@runtime_checkable
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    language_code: str
    delegate: SpeechRecognizerDelegate | None
    
    async def start_listening(self): pass
    def stop_listening(self): pass
    def microphone_did_receive_sample(self, data): ...
 
@runtime_checkable
class SpeechSynthesizerResult(Protocol):
    async def play(self): pass

@runtime_checkable   
class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str) -> SpeechSynthesizerResult: pass
