from __future__ import annotations
from typing import Any
from typing import NamedTuple
from abc import ABC
import copy

from stark.general.classproperty import classproperty
from stark.models.transcription import Transcription, TranscriptionTrack
from .. import Pattern


class ParseResult(NamedTuple):
    obj: Object
    track: TranscriptionTrack
    transcription: Transcription

class ParseError(Exception):
    pass

class Object(ABC):

    value: Any
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    def __init__(self, value: Any):
        '''Just init with wrapped value.'''
        self.value = value
        
    async def did_parse(self, track: TranscriptionTrack, transcription: Transcription, re_match_groups: dict[str, str]) -> tuple[TranscriptionTrack, Transcription]:
        '''
        This method is called after parsing from string and setting parameters found in pattern. 
        You will very rarely, if ever, need to call this method directly.
        
        Override this method for more complex custom parsing from string. 
        
        Returns:
            Minimal transcription slice that is required to parse value. See `Transcription.slice`.
        
        Raises:
            ParseError: if parsing failed.
        '''
        self.value = track.text
        return track, transcription

    @classmethod
    async def parse(cls, track: TranscriptionTrack, transcription: Transcription, re_match_groups: dict[str, str] | None = None) -> ParseResult:
        '''
        For internal use only.
        You will very rarely, if ever, need to override or even call this method.
        Override `async def did_parse(...) -> Transcription` if you need custom complex parsing.
        
        Returns:
            Minimal transcription slice that is required to parse value.
        
        Raises:
            ParseError: if parsing failed.
        '''
        
        obj = cls(None)
        re_match_groups = re_match_groups or {}
        
        for name, object_type in cls.pattern.parameters.items():
            if not re_match_groups.get(name):
                continue
            
            value = re_match_groups.pop(name)
            time_range = next(iter(track.get_time(value)))
            sub_track = track.get_slice(*time_range)
            sub_transcription = transcription.get_slice(*time_range)
            setattr(obj, name, (await object_type.parse(sub_track, sub_transcription, re_match_groups)).obj)
        
        return ParseResult(obj, *(await obj.did_parse(track, transcription, re_match_groups)))
    
    def copy(self) -> Object:
        return copy.copy(self)
    
    def __format__(self, spec) -> str:
        return f'{self.value:{spec}}'

    def __repr__(self):
        strValue = f'"{str(self.value)}"' if type(self.value) == str else str(self.value)
        return f'<{type(self).__name__} value: {strValue}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            raise NotImplementedError(f'Cannot compare {type(self)} with {type(other)}')
        return self.value == other.value
    