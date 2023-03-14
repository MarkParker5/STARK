from typing import Protocol


class SpeechRecognizerDelegate(Protocol):
    def speech_recognizer_did_receive_final_result(self, result: str): pass
    def speech_recognizer_did_receive_partial_result(self, result: str): pass
    def speech_recognizer_did_receive_empty_result(self): pass
   
class SpeechRecognizer(Protocol):
    is_recognizing: bool
    delegate: SpeechRecognizerDelegate
    
    async def start_listening(self): pass
    async def stop_listening(self): pass
 
class SpeechSynthesizerResult(Protocol):
    def play(self): pass
    
class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str) -> SpeechSynthesizerResult: pass