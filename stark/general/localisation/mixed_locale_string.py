from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, Self

from stark.general.localisation.language_code import LanguageCode
from stark.general.localisation.locale_string import LocaleString

if TYPE_CHECKING:
    from lingua import LanguageDetector


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

    @classmethod
    def detect(cls, text: str) -> MixedLocaleString:
        """Detect language boundaries in *text* and return a segmented MixedLocaleString.

        Requires ``lingua-language-detector``.  The detector is built once and cached.
        Adjacent spans that resolve to the same language are merged.
        """
        detector = _get_detector()
        spans = detector.detect_multiple_languages_of(text)

        if not spans:
            return cls([SpeechSegment(text.strip() or text, "base")])

        raw: list[SpeechSegment] = []
        for span in spans:
            chunk = text[span.start_index:span.end_index].strip()
            if not chunk:
                continue
            lang: LanguageCode = span.language.iso_code_639_1.name.lower()  # type: ignore[assignment]
            raw.append(SpeechSegment(chunk, lang))

        # merge adjacent same-language segments
        merged: list[SpeechSegment] = []
        for seg in raw:
            if merged and merged[-1].language_code == seg.language_code:
                merged[-1] = SpeechSegment(f"{merged[-1].text} {seg.text}", seg.language_code)
            else:
                merged.append(seg)

        return cls(merged) if merged else cls([SpeechSegment(text, "base")])

    def __repr__(self) -> str:
        return f"MixedLocaleString({self._segments!r})"


@cache
def _get_detector() -> LanguageDetector:
    try:
        from lingua import LanguageDetectorBuilder
    except ImportError:
        raise ImportError(
            "lingua-language-detector is required for MixedLocaleString.detect(). "
            "Install it with: pip install lingua-language-detector"
        ) from None
    return LanguageDetectorBuilder.from_all_languages().build()


def _majority_language(segments: list[SpeechSegment] | tuple[SpeechSegment, ...]) -> LanguageCode | None:
    if not segments:
        return None
    counts: Counter[LanguageCode] = Counter()
    for s in segments:
        counts[s.language_code] += len(s.text)
    return counts.most_common(1)[0][0]
