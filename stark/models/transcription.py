from pydantic import BaseModel, Field, ValidationError


class KaldiWord(BaseModel):
    word: str
    start: float
    end: float
    conf: float | None = None # only for KaldiMBR
    language_code: str = ''
    
    @property
    def duration(self):
        return self.end - self.start
    
    @property
    def middle(self):
        return self.start + self.duration / 2
    
class KaldiMBR(BaseModel):
    text: str = ''
    result: list[KaldiWord] = Field(default_factory = list)
    spk: list[float] = Field(default_factory = list)
    spk_frames: int = 0
    language_code: str = ''
    
    @property
    def confidence(self):
        return sum(word.conf for word in self.result) / len(self.result) if self.result else 0
    
    def __hash__(self) -> int:
        return hash(self.text)

class KaldiTranscription(BaseModel):
    text: str
    result: list[KaldiWord] = Field(default_factory = list)
    confidence: float
    
class KaldiResult(BaseModel):
    alternatives: list[KaldiTranscription]

class Transcription(BaseModel):
    best: KaldiMBR
    origins: dict[str, KaldiMBR] = Field(default_factory = dict)
    # suggestions: dict[str, KaldiWord] # list[tuple(str, str)]
