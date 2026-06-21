from __future__ import annotations

from stark.general.localisation.language_code import LanguageCode
from stark.general.localisation.locale_string import LocaleString
from stark.models.transcription_string import TranscriptionString, TranscriptionWord
from stark.models.voice_transcription import VoiceTranscriptionTrack, VoiceTranscriptionWord


class VoiceTranscriptionString(TranscriptionString):
    """A TranscriptionString that also carries a time-aligned VoiceTranscriptionTrack.

    String operations (slicing, replace, strip) maintain the track alongside
    the text and word-language map. The parser sees a TranscriptionString;
    the VA can access ``.track`` for timestamps, confidence, and speaker data.
    """

    _track: VoiceTranscriptionTrack | None

    def __new__(
        cls,
        value: str = "",
        language_code: LanguageCode | None = None,
        words: tuple[TranscriptionWord, ...] | list[TranscriptionWord] = (),
        alternative_texts: dict[str, LocaleString] | None = None,
        suggestions: tuple | list = (),
        track: VoiceTranscriptionTrack | None = None,
    ) -> VoiceTranscriptionString:
        instance = super().__new__(cls, value, language_code, words, alternative_texts, suggestions)
        instance._track = track
        return instance

    @property
    def track(self) -> VoiceTranscriptionTrack | None:
        return self._track

    def _with(self, value: str) -> VoiceTranscriptionString:
        base = super()._with(value)
        sliced_track = self._slice_track_for(value)
        return VoiceTranscriptionString(
            base, None, base._words, base._alternative_texts, base._suggestions, sliced_track,
        )

    def __getitem__(self, key) -> VoiceTranscriptionString:
        base = super().__getitem__(key)
        result_str = str.__getitem__(self, key)
        sliced_track = self._slice_track_for(result_str)
        return VoiceTranscriptionString(
            base, None, base._words, base._alternative_texts, base._suggestions, sliced_track,
        )

    def replace(self, old: str, new: str, count: int = -1) -> VoiceTranscriptionString:
        base = super().replace(old, new, count)
        track = None
        if self._track:
            track = self._track.model_copy(deep=True)
            track.replace(old, new)
        return VoiceTranscriptionString(
            base, None, base._words, base._alternative_texts, base._suggestions, track,
        )

    def strip(self, chars: str | None = None) -> VoiceTranscriptionString:
        base = super().strip(chars)
        sliced_track = self._slice_track_for(str(base)) if base else None
        return VoiceTranscriptionString(
            base, None, base._words, base._alternative_texts, base._suggestions, sliced_track,
        )

    def are_substrings_overlapping(self, a: str, b: str) -> bool | None:
        if not self._track:
            return super().are_substrings_overlapping(a, b)
        times_a = list(self._track.get_time(a))
        times_b = list(self._track.get_time(b))
        if not times_a or not times_b:
            return super().are_substrings_overlapping(a, b)
        a_start, a_end = times_a[0]
        b_start, b_end = times_b[0]
        return a_start < b_end and a_end > b_start

    def _slice_track_for(self, value: str) -> VoiceTranscriptionTrack | None:
        if not self._track or not value:
            return None
        times = list(self._track.get_time(value))
        if not times:
            return None
        start, end = times[0]
        return self._track.get_slice(start, end)

    def __repr__(self) -> str:
        has_track = self._track is not None
        return f"VoiceTranscriptionString({str.__repr__(self)}, language_code={self.language_code!r}, words={len(self._words)}, has_track={has_track})"
