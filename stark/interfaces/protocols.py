from typing import Protocol, runtime_checkable


@runtime_checkable
class SpeechRecognizerDelegate(Protocol):
    def speech_recognizer_did_receive_final_result(self, result: str): pass
    def speech_recognizer_did_receive_partial_result(self, result: str): pass
    def speech_recognizer_did_receive_empty_result(self): pass
   
@runtime_checkable
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    delegate: SpeechRecognizerDelegate | None
    
    async def start_listening(self): pass
    def stop_listening(self): pass
 
@runtime_checkable
class SpeechSynthesizerResult(Protocol):
    def play(self): pass

@runtime_checkable   
class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str) -> SpeechSynthesizerResult: pass
