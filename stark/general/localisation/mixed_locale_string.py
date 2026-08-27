from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Self

from stark.general.localisation.language_code import LanguageCode
from stark.general.localisation.locale_string import LocaleString


@dataclass(frozen=True)
class SpeechSegment:
    text: str
    language_code: LanguageCode


class MixedLocaleString(LocaleString):
    """A LocaleString whose content spans multiple languages.

    Stores an ordered sequence of SpeechSegments. The top-level
    ``language_code`` returns the majority language by character count.
    Useful as ``Response.voice`` when a single utterance mixes languages,
    e.g. "Turn on свет" (English command, Russian noun).
    """

    _segments: tuple[SpeechSegment, ...]

    def __new__(cls, segments: list[SpeechSegment] | tuple[SpeechSegment, ...]) -> Self:
        text = " ".join(s.text for s in segments)
        lang = _majority_language(segments) or "base"
        instance = super().__new__(cls, text, lang)
        instance._segments = tuple(segments)
        return instance

    @property
    def segments(self) -> tuple[SpeechSegment, ...]:
        return self._segments

    @property
    def language_code(self) -> LanguageCode:
        return _majority_language(self._segments) or "base"

    @language_code.setter
    def language_code(self, value: LanguageCode):
        pass  # immutable; majority-derived

    def _with(self, value: str) -> LocaleString:
        return LocaleString(value, self.language_code)

    def __repr__(self) -> str:
        return f"MixedLocaleString({self._segments!r})"


def _majority_language(segments: list[SpeechSegment] | tuple[SpeechSegment, ...]) -> LanguageCode | None:
    if not segments:
        return None
    counts: Counter[LanguageCode] = Counter()
    for s in segments:
        counts[s.language_code] += len(s.text)
    return counts.most_common(1)[0][0]
