from typing import Type
from dataclasses import dataclass
import re

from .expressions import dictionary
# from ..VIObjects import VIObject


@dataclass
class MatchResult:
    substring: str
    groups: dict[str, str]

class Pattern:
    
    argumentTypes: dict[str, Type['VIObject']] = {} # static
    
    _origin: str
    _compiled: str | None = None

    def __init__(self, origin: str):
        self._origin = origin

    @property
    def compiled(self) -> str: # transform Pattern to classic regex with named groups
        if self._compiled: return self._compiled
        
        pattern: str = self._origin

        #   transform vicore expressions to regex
        
        for ptrn, regex in dictionary.items():
            if res := re.search(ptrn, pattern):
                pattern = re.sub(ptrn, regex, pattern)

        #   find and transform arguments like $name:Type
        
        types = '|'.join(Pattern.argumentTypes.keys())
        argumentRegex = re.compile(r'\$(?P<name>[A-z]+)\:(?P<type>(?:' + types + r'))')
        argumentMatches = re.finditer(argumentRegex, pattern)
        
        for match in argumentMatches:
            
            argName = match.group('name')
            argTypeName = match.group('type')
            argType: Type['VIObject'] = Pattern.argumentTypes.get(argTypeName)
            
            if not argType: 
                raise ValueError(f'Unknown type: {argTypeName} for argument: {argName} in pattern: {self._origin}')
            
            pattern = re.sub('\\' + match.group(0), f'(?P<{argName}>{argType.pattern.compiled})', pattern)
            
        #   save and return
        
        self._compiled = pattern
        print(self._compiled)
        return self._compiled

    def match(self, string: str) -> MatchResult | None:
        
        if matches := sorted(re.finditer(self.compiled, string), key = lambda m: len(m.group(0))):
            match = matches[-1]
            return MatchResult(match.group(0).strip(), match.groupdict())
        
        return None
