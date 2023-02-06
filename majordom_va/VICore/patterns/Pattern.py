from __future__ import annotations
from typing import Type, Generator
from dataclasses import dataclass
import re

from .expressions import dictionary


@dataclass
class MatchResult:
    substring: str
    groups: dict[str, str]

class Pattern:
    
    argumentTypes: dict[str, Type['VIObject']] = {} # static
    
    arguments: dict[str, Type['VIObject']]
    compiled: str
    
    _origin: str
    _argument_regex: re.compile

    def __init__(self, origin: str):
        self._origin = origin
        self._argument_regex = self._get_argument_regex()
        self.arguments = dict(self._get_arguments())
        self.compiled = self._compile()
        
    def match(self, string: str) -> MatchResult | None:
        
        if matches := sorted(re.finditer(self.compiled, string), key = lambda m: len(m.group(0))):
            match = matches[-1]
            return MatchResult(match.group(0).strip(), match.groupdict())
        
        return None
        
    def _get_argument_regex(self) -> re.compile:
        types = '|'.join(Pattern.argumentTypes.keys())
        return re.compile(r'\$(?P<name>[A-z]+)\:(?P<type>(?:' + types + r'))')
    
    def _get_arguments(self) -> Generator[tuple[str, Type['VIObject']]]:
        for match in re.finditer(self._argument_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_type: Type['VIObject'] = Pattern.argumentTypes.get(arg_type_name)
            
            if not arg_type: 
                raise ValueError(f'Unknown type: {arg_type_name} for argument: {arg_name} in pattern: {self._origin}')
            
            yield arg_name, arg_type
            
    def _compile(self) -> str: # transform Pattern to classic regex with named groups
        
        pattern: str = self._origin

        #   transform vicore expressions to regex
        
        for vi_ptrn, regex in dictionary.items():
            pattern = re.sub(vi_ptrn, regex, pattern)

        #   find and transform arguments like $name:Type
        
        for name, vi_type in self.arguments.items():
            
            arg_declaration = f'\\${name}\\:{vi_type.__name__}'
            arg_pattern = vi_type.pattern.compiled.replace('\\', r'\\')
            pattern = re.sub(arg_declaration, f'(?P<{name}>{arg_pattern})', pattern)
        
        return pattern
    
    def __eq__(self, other: Pattern) -> bool:
        return self._origin == other._origin
    
    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
