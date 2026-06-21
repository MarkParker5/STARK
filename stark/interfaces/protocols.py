from typing import Protocol, runtime_checkable

from stark.general.localisation import LocaleString


@runtime_checkable
class SpeechRecognizerDelegate(Protocol):
    async def speech_recognizer_did_receive_final_result(self, result: str | LocaleString): pass
    async def speech_recognizer_did_receive_partial_result(self, result: str): pass
    async def speech_recognizer_did_receive_empty_result(self): pass
   
@runtime_checkable
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    delegate: SpeechRecognizerDelegate | None

    def microphone_did_receive_sample(self, data): pass
    async def start_listening(self): pass
    def stop_listening(self): pass
 
@runtime_checkable
class SpeechSynthesizerResult(Protocol):
    async def play(self): pass

@runtime_checkable   
class SpeechSynthesizer(Protocol):
    async def synthesize(self, text: str) -> SpeechSynthesizerResult: pass
