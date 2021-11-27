from typing import Type, Optional
import re

from .expressions import expressions
from ..ACObjects import *

class Pattern:
    origin: str
    compiled: str #getonly

    def __init__(self, origin: str):
        self.origin = origin

    @property
    def compiled(self) -> str: # transform pattern to classic regex with named groups
        pattern: str = self.origin

        #   transform patterns to regexp
        for ptrn, regex in expressions.items():
            pattern = re.sub(re.compile(ptrn), regex, pattern)

        #   find and transform arguments like $name:Type
        argumentRegex = re.compile(r'\$[:word:]:[:word:]')
        while match := re.search(argumentRegex, pattern)[0]:
            arg: str = match[1:]
            argName, argTypeName = arg.split(':')
            argType: Type[ACObject] = classFromString(argTypeName)
            pattern = re.sub('\\'+link[0], f'(?P<{arg}>{argType.pattern.compiled})', pattern)

        return re.compile(pattern)


    def match(self, string: str) -> Optional[dict[str, str]]:
        if match := re.search(self.compiled, string):
            return match.groupdict()
        return None
