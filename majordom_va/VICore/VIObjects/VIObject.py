from __future__ import annotations
from typing import Any
from collections import namedtuple
from abc import ABC

from general.classproperty import classproperty
from .. import Pattern


ParseResult = namedtuple('ParseResult', ['obj', 'start', 'end'])

class VIObject(ABC):

    value: Any

    def __init__(self, value: Any):
        self.value = value

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')

    @classmethod
    def parse(cls, from_string: str, parameters: dict[str, str] = None) -> ParseResult | None:
        obj = cls(from_string)
        parameters = parameters or {}
        
        for name, vi_type in cls.pattern.parameters.items():
            if not parameters.get(name):
                continue
            value = parameters.pop(name)
            setattr(obj, name, vi_type.parse(from_string = value, parameters = parameters))
        
        return ParseResult(obj, 0, len(from_string))
    
    def __format__(self, spec) -> str:
        return f'{self.value:{spec}}'

    def __repr__(self):
        strValue = f'"{str(self.value)}"' if type(self.value) == str else str(self.value)
        return f'<{type(self).__name__} value: {strValue}>'

    def __eq__(self, other: VIObject) -> bool:
        return self.value == other.value
    