from __future__ import annotations
from typing import Any
from collections import namedtuple
from abc import ABC

from general.classproperty import classproperty
from .. import Pattern


ParseResult = namedtuple('ParseResult', ['obj', 'substring'])

class ParseError(Exception):
    pass

class VIObject(ABC):

    value: Any
    
    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    def __init__(self, value: Any):
        '''Just init with wrapped value.'''
        self.value = value
        
    def did_parse(self, from_string: str) -> str:
        '''
        This method is called after parsing from string and setting parameters found in pattern. 
        You will very rarely, if ever, need to call this method directly.
        
        Override this method for more complex parsing from string. 
        
        Returns:
            Minimal substring that is required to parse value.
        
        Raises:
            ParseError: if parsing failed.
        '''
        self.value = from_string
        return from_string

    @classmethod
    def parse(cls, from_string: str, parameters: dict[str, str] = None) -> ParseResult:
        '''
        For internal use only.
        You will very rarely, if ever, need to override or even call this method.
        Override `def did_parse(self, from_string: str) -> str` if you need complex parsing.
        
        Raises:
            ParseError: if parsing failed.
        '''
        
        obj = cls(None)
        parameters = parameters or {}
        
        for name, vi_type in cls.pattern.parameters.items():
            if not parameters.get(name):
                continue
            value = parameters.pop(name)
            setattr(obj, name, vi_type.parse(from_string = value, parameters = parameters).obj)
        
        substring = obj.did_parse(from_string)
        
        return ParseResult(obj, substring)
    
    def __format__(self, spec) -> str:
        return f'{self.value:{spec}}'

    def __repr__(self):
        strValue = f'"{str(self.value)}"' if type(self.value) == str else str(self.value)
        return f'<{type(self).__name__} value: {strValue}>'

    def __eq__(self, other: VIObject) -> bool:
        return self.value == other.value
    