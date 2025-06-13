from __future__ import annotations
from typing import Any
from collections import namedtuple
from abc import ABC
import copy

from stark.general.classproperty import classproperty
from .. import Pattern


ParseResult = namedtuple('ParseResult', ['obj', 'substring'])

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

    async def did_parse(self, from_string: str) -> str:
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
    async def parse(cls, from_string: str, parameters: dict[str, str] | None = None) -> ParseResult:
        '''
        For internal use only.
        You will very rarely, if ever, need to override or even call this method.
        Override `def did_parse(self, from_string: str) -> str` if you need complex parsing.

        Raises:
            ParseError: if parsing failed.
        '''

        obj = cls(None)
        parameters = parameters or {}

        for name, object_type in cls.pattern.parameters.items():
            if not parameters.get(name):
                continue
            value = parameters.pop(name)
            # TODO: check whether all pattern parameters must be assigned as object attributes
            setattr(obj, name, (await object_type.parse(from_string = value, parameters = parameters)).obj)

        substring = await obj.did_parse(from_string)
        assert substring in from_string, ValueError(f'Parsed substring must be a part of the original string. There is no {substring} in {from_string}.')
        assert obj.value is not None, ValueError(f'Parsed object {obj} must have a `value` property set in did_parse method. It is not set in {type(obj)}.')

        return ParseResult(obj, substring)

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
