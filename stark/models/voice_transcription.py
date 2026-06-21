from __future__ import annotations

from typing import Generator, NamedTuple, TYPE_CHECKING

from pydantic import BaseModel, Field

from dataclasses import dataclass

from stark.general.localisation.language_code import LanguageCode
from stark.models.transcription_string import TranscriptionWord

if TYPE_CHECKING:
    from stark.models.voice_transcription_string import VoiceTranscriptionString


@dataclass(frozen=True)
class VoiceTranscriptionWord(TranscriptionWord):
    start: float = 0.0
    end: float = 0.0
    conf: float | None = None

    @property
    def duration(self):
        return self.end - self.start

    @property
    def middle(self):
        return self.start + self.duration / 2


class VoiceTranscriptionTrack(BaseModel):
    text: str = ''
    result: list[VoiceTranscriptionWord] = Field(default_factory=list)
    spk: list[float] = Field(default_factory=list)
    spk_frames: int = 0
    language_code: LanguageCode = 'base'

    @property
    def confidence(self):
        return sum(word.conf or 0 for word in self.result) / len(self.result) if self.result else 0

    def replace(self, substring: str, replacement: str):
        if not substring:
            return

        start_time: float | None = None
        remaining = substring[:]
        new_words: list[VoiceTranscriptionWord] = []
        to_remove: list[VoiceTranscriptionWord] = []
        to_remove_candidates: list[VoiceTranscriptionWord] = []

        for word in self.result:
            if remaining.startswith(word.word):
                if not start_time:
                    start_time = word.start
                remaining = remaining[len(word.word):].strip()
                to_remove_candidates.append(word)
            else:
                remaining = substring[:].strip()
                start_time = None
                to_remove_candidates = []

            if not remaining and start_time is not None:
                new_words.append(VoiceTranscriptionWord(
                    word=replacement,
                    language_code=word.language_code,
                    char_start=0,
                    char_end=len(replacement),
                    start=start_time,
                    end=word.end,
                    conf=1,
                ))
                to_remove.extend(to_remove_candidates)
                to_remove_candidates = []
                remaining = substring[:].strip()
                start_time = None

        for word in to_remove:
            self.result.remove(word)

        new_count = len(new_words)
        for i, word in enumerate(self.result):
            if not new_words:
                break
            if word.start >= new_words[0].end:
                self.result.insert(i + new_count - len(new_words), new_words.pop(0))

        if new_words:
            self.result.extend(new_words)

        self.text = ' '.join(word.word for word in self.result)

    def get_slice(self, start: float, end: float) -> VoiceTranscriptionTrack:
        new_track = VoiceTranscriptionTrack(
            text='',
            result=[],
            spk=self.spk,
            spk_frames=self.spk_frames,
            language_code=self.language_code,
        )

        for word in self.result:
            if word.middle <= start:
                continue
            if word.middle >= end:
                break
            new_track.result.append(VoiceTranscriptionWord(
                word=word.word,
                language_code=word.language_code,
                char_start=0,
                char_end=len(word.word),
                start=word.start,
                end=word.end,
                conf=word.conf,
            ))

        new_track.text = ' '.join(word.word for word in new_track.result)
        return new_track

    def get_time(self, substring: str, from_index: int = 0, to_index: int | None = None) -> Generator[tuple[float, float], None, None]:
        if not substring:
            return

        start_time: float | None = None
        current_index = 0
        remaining = substring[:].strip()

        for word in self.result:
            current_index = self.text.index(word.word, current_index)

            if current_index < from_index:
                current_index += len(word.word)
                continue

            if to_index and current_index >= to_index:
                break

            current_index += len(word.word)

            if substring in word.word:
                yield word.start, word.end
                remaining = substring[:].strip()
                start_time = None

            elif remaining.startswith(word.word):
                if start_time is None:
                    start_time = word.start
                remaining = remaining[len(word.word):].strip()
            else:
                remaining = substring[:].strip()
                start_time = None

            if not remaining and start_time is not None:
                yield start_time, word.end
                remaining = substring[:].strip()

    def to_voice_transcription_string(self) -> VoiceTranscriptionString:
        from stark.models.voice_transcription_string import VoiceTranscriptionString
        offset = 0
        adjusted: list[VoiceTranscriptionWord] = []
        for w in self.result:
            adjusted.append(VoiceTranscriptionWord(
                word=w.word,
                language_code=w.language_code or self.language_code,
                char_start=offset,
                char_end=offset + len(w.word),
                start=w.start,
                end=w.end,
                conf=w.conf,
            ))
            offset += len(w.word) + 1
        return VoiceTranscriptionString(self.text, None, tuple(adjusted), track=self)

    def __hash__(self) -> int:
        return hash(self.text)


class Suggestion(NamedTuple):
    variant: str
    keyword: str


class Transcription(BaseModel):
    best: VoiceTranscriptionTrack
    origins: dict[str, VoiceTranscriptionTrack] = Field(default_factory=dict)
    suggestions: list[Suggestion] = Field(default_factory=list)

    def replace(self, substring: str, replacement: str):
        for origin in [*self.origins.values(), self.best]:
            origin.replace(substring, replacement)

    def get_slice(self, start: float, end: float) -> Transcription:
        return Transcription(
            best=self.best.get_slice(start, end),
            origins={k: v.get_slice(start, end) for k, v in self.origins.items()},
            suggestions=self.suggestions,
        )

    def to_voice_transcription_string(self) -> VoiceTranscriptionString:
        from stark.general.localisation import LocaleString
        from stark.models.voice_transcription_string import VoiceTranscriptionString

        best = self.best
        # build per-word language codes from whichever origin provided each word
        offset = 0
        voice_words: list[VoiceTranscriptionWord] = []
        for w in best.result:
            lang = best.language_code
            # find which origin had the highest confidence for this word's time
            for origin_lang, origin_track in self.origins.items():
                for ow in origin_track.result:
                    if ow.word == w.word and abs(ow.start - w.start) < 0.1:
                        if (ow.conf or 0) >= (w.conf or 0):
                            lang = origin_lang
                        break
            voice_words.append(VoiceTranscriptionWord(
                word=w.word,
                language_code=lang,
                char_start=offset,
                char_end=offset + len(w.word),
                start=w.start,
                end=w.end,
                conf=w.conf,
            ))
            offset += len(w.word) + 1

        alternative_texts = {
            lang: LocaleString(track.text, lang)
            for lang, track in self.origins.items()
        }

        return VoiceTranscriptionString(
            best.text,
            None,
            tuple(voice_words),
            alternative_texts=alternative_texts,
            suggestions=tuple(self.suggestions),
            track=best,
        )
