from __future__ import annotations

from stark.general.localisation.language_code import LanguageCode
from stark.general.localisation.locale_string import LocaleString
from stark.models.transcription_string import TranscriptionString, TranscriptionWord
from stark.models.voice_transcription import VoiceTranscriptionTrack


class VoiceTranscriptionString(TranscriptionString):
    """A TranscriptionString that also carries a time-aligned VoiceTranscriptionTrack.

    String operations (slicing, replace, strip) maintain the track alongside
    the text and word-language map. The parser sees a TranscriptionString;
    the VA can access ``.track`` for timestamps, confidence, and speaker data.
    """

    _track: VoiceTranscriptionTrack | None
    _alternative_tracks: dict[str, VoiceTranscriptionTrack]

    def __new__(
        cls,
        value: str = "",
        language_code: LanguageCode | None = None,
        words: tuple[TranscriptionWord, ...] | list[TranscriptionWord] = (),
        alternative_texts: dict[str, LocaleString] | None = None,
        recognizable_alternatives: list | None = None,
        track: VoiceTranscriptionTrack | None = None,
        alternative_tracks: dict[str, VoiceTranscriptionTrack] | None = None,
    ) -> VoiceTranscriptionString:
        instance = super().__new__(cls, value, language_code, words, alternative_texts, recognizable_alternatives)
        instance._track = track
        instance._alternative_tracks = alternative_tracks or {}
        return instance

    @property
    def track(self) -> VoiceTranscriptionTrack | None:
        return self._track

    def _with(self, value: str) -> VoiceTranscriptionString:
        base = super()._with(value)
        sliced_track = self._slice_track_for(value)
        return VoiceTranscriptionString(
            base,
            None,
            base._words,
            base._alternative_texts,
            base.recognizable_alternatives,
            sliced_track,
            self._alternative_tracks,
        )

    def __getitem__(self, key) -> VoiceTranscriptionString:
        base = super().__getitem__(key)
        result_str = str.__getitem__(self, key)
        sliced_track = self._slice_track_for(result_str)
        return VoiceTranscriptionString(
            base,
            None,
            base._words,
            base._alternative_texts,
            base.recognizable_alternatives,
            sliced_track,
            self._alternative_tracks,
        )

    def replace(self, old: str, new: str, count: int = -1) -> VoiceTranscriptionString:
        base = super().replace(old, new, count)
        track = None
        if self._track:
            track = self._track.model_copy(deep=True)
            track.replace(old, new)
        return VoiceTranscriptionString(
            base,
            None,
            base._words,
            base._alternative_texts,
            base.recognizable_alternatives,
            track,
            self._alternative_tracks,
        )

    def strip(self, chars: str | None = None) -> VoiceTranscriptionString:
        base = super().strip(chars)
        sliced_track = self._slice_track_for(str(base)) if base else None
        return VoiceTranscriptionString(
            base,
            None,
            base._words,
            base._alternative_texts,
            base.recognizable_alternatives,
            sliced_track,
            self._alternative_tracks,
        )

    def translate_position(self, position: int, from_track: str, to_track: str) -> int:
        if not self._track or from_track == to_track:
            return position
        from_vt = self._get_track_for(from_track)
        if not from_vt:
            return position
        time = from_vt.position_to_time(position)
        if time is None:
            return position
        to_vt = self._get_track_for(to_track)
        if not to_vt:
            return position
        return to_vt.time_to_position(time)

    def _get_track_for(self, text: str) -> VoiceTranscriptionTrack | None:
        if self._track and self._track.text == text:
            return self._track
        for alt_track in self._alternative_tracks.values():
            if alt_track.text == text:
                return alt_track
        return self._track

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
