from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from stark.general.localisation import LanguageCode, LocaleString
from stark.general.localisation.mixed_locale_string import MixedLocaleString, SpeechSegment


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


class CompositeSpeechSynthesizerResult:
    """Plays multiple SpeechSynthesizerResults sequentially."""

    def __init__(self, parts: list[SpeechSynthesizerResult]):
        self._parts = parts

    async def play(self):
        for part in self._parts:
            await part.play()


class SpeechSynthesizer(ABC):
    """Two-level TTS abstraction.

    Subclass and implement ``synthesize_segment`` to plug in an engine.
    Override ``synthesize`` only to customise mixing behaviour.
    """

    async def synthesize(self, voice: str | LocaleString) -> SpeechSynthesizerResult:
        if isinstance(voice, MixedLocaleString):
            parts = [
                await self.synthesize_segment(s.text, s.language_code)
                for s in voice.segments
            ]
            return CompositeSpeechSynthesizerResult(parts)
        lang: LanguageCode = voice.language_code if isinstance(voice, LocaleString) else "base"
        return await self.synthesize_segment(str(voice), lang)

    @abstractmethod
    async def synthesize_segment(self, text: str, language_code: LanguageCode) -> SpeechSynthesizerResult:
        pass
