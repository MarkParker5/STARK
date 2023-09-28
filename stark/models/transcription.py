from __future__ import annotations
from typing import Generator, NamedTuple
from pydantic import BaseModel, Field, ValidationError


class TranscriptionWord(BaseModel):
    word: str
    start: float
    end: float
    conf: float | None = None # only for TranscriptionTrack
    language_code: str = ''
    
    @property
    def duration(self):
        return self.end - self.start
    
    @property
    def middle(self):
        return self.start + self.duration / 2
    
class TranscriptionTrack(BaseModel): # TODO: rename to TranscriptionTrack
    text: str = ''
    result: list[TranscriptionWord] = Field(default_factory = list)
    spk: list[float] = Field(default_factory = list)
    spk_frames: int = 0
    language_code: str = ''
    
    @property
    def confidence(self):
        return sum(word.conf or 0 for word in self.result) / len(self.result) if self.result else 0
    
    def replace(self, substring: str, replacement: str):
        if not substring:
            return
        
        self.text = self.text.replace(substring, replacement)
        
        for word in self.result:
            word.word = word.word.replace(substring, replacement)
        
        # handle multiple words substring
        
        start_time: float | None = None
        remaining = substring[:]
        new_words: list[TranscriptionWord] = []
        to_remove: list[TranscriptionWord] = []
        to_remove_candidates: list[TranscriptionWord] = []
        
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
                new_words.append(TranscriptionWord(
                    word = replacement,
                    start = start_time,
                    end = word.end,
                    conf = 1
                ))
                to_remove.extend(to_remove_candidates)
                to_remove_candidates = []
                remaining = substring[:].strip()
                start_time = None
                
        for word in to_remove:
            self.result.remove(word)
                
        for i, word in enumerate(self.result):
            if not new_words:
                break
            
            if word.end <= new_words[0].start:
                self.result.insert(i, new_words.pop(0))
                
        if new_words:
            self.result.extend(new_words)
        
    def get_slice(self, start: float, end: float) -> 'TranscriptionTrack':
        new_track = TranscriptionTrack(
            text = '',
            result = [],
            spk = self.spk,
            spk_frames = self.spk_frames,
            language_code = self.language_code
        )
        
        for word in self.result:
            if word.end <= start:
                continue
            if word.start >= end:
                break
            new_word = TranscriptionWord(
                word = word.word,
                start = max(word.start - start, 0),
                end = min(word.end - start, end - start),
                conf = word.conf
            )
            new_track.result.append(new_word)
        
        new_track.text = ' '.join(word.word for word in new_track.result)
        return new_track
    
    def get_time(self, substring: str, from_index: int = 0, to_index: int | None = None) -> Generator[tuple[float, float], None, None]:
        if not substring:
            return
        
        start_time: float | None = None
        current_index = 0
        remaining = substring[:].strip()
        
        for word in self.result:
            current_index = self.result[current_index:].index(word)
            
            if current_index < from_index:
                continue
            
            if to_index and current_index >= to_index:
                break
            
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
    
    def __hash__(self) -> int:
        return hash(self.text)
    
class Suggestion(NamedTuple):
    variant: str
    keyword: str

class Transcription(BaseModel):
    best: TranscriptionTrack
    origins: dict[str, TranscriptionTrack] = Field(default_factory = dict)
    suggestions: list[Suggestion] = Field(default_factory = list)
    
    def replace(self, substring: str, replacement: str):
        for origin in [*self.origins.values(), self.best]:
            origin.replace(substring, replacement)
    
    def get_slice(self, start: float, end: float) -> Transcription:
        return Transcription(
            best = self.best.get_slice(start, end),
            origins = {k: v.get_slice(start, end) for k, v in self.origins.items()},
            suggestions = self.suggestions
        )

class KaldiTranscription(BaseModel):
    text: str
    result: list[TranscriptionWord] = Field(default_factory = list)
    confidence: float
    
class KaldiResult(BaseModel):
    alternatives: list[KaldiTranscription]