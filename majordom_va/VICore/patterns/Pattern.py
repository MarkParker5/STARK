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
    
    parameters: dict[str, Type['VIObject']]
    compiled: str
    
    _origin: str
    _parameter_regex: re.compile
    _parameter_types: dict[str, Type['VIObject']] = {} # static

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_parameter_regex()
        self.parameters = dict(self._get_parameters())
        self.compiled = self._compile()
        
    def match(self, string: str) -> MatchResult | None:
        
        if matches := sorted(re.finditer(self.compiled, string), key = lambda m: len(m.group(0))):
            match = matches[-1]
            return MatchResult(match.group(0).strip(), match.groupdict())
        
        return None
    
    @classmethod
    def add_parameter_type(cls, vi_type: Type['VIObject']):
        error_msg = f'Can`t add parameter type {vi_type.__name__}: pattern parameters does not match class properties'
        assert vi_type.pattern.parameters.items() <= vi_type.__annotations__.items(), error_msg
        assert cls._parameter_types.get(vi_type.__name__) is None, f'Can`t add parameter type: {vi_type.__name__} already exists'
        cls._parameter_types[vi_type.__name__] = vi_type
        
    def _get_parameter_regex(self) -> re.compile:
        types = '|'.join(Pattern._parameter_types.keys())
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
    
    def _get_parameters(self) -> Generator[tuple[str, Type['VIObject']]]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_type: Type['VIObject'] = Pattern._parameter_types.get(arg_type_name)
            
            if not arg_type: 
                raise ValueError(f'Unknown type: {arg_type_name} for parameter: {arg_name} in pattern: {self._origin}')
            
            yield arg_name, arg_type
            
    def _compile(self) -> str: # transform Pattern to classic regex with named groups
        
        pattern: str = self._origin

        #   transform vicore expressions to regex
        
        for vi_ptrn, regex in dictionary.items():
            pattern = re.sub(vi_ptrn, regex, pattern)

        #   find and transform parameters like $name:Type
        
        for name, vi_type in self.parameters.items():
            
            arg_declaration = f'\\${name}\\:{vi_type.__name__}'
            arg_pattern = vi_type.pattern.compiled.replace('\\', r'\\')
            pattern = re.sub(arg_declaration, f'(?P<{name}>{arg_pattern})', pattern)
        
        return pattern
    
    def __eq__(self, other: Pattern) -> bool:
        return self._origin == other._origin
    
    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
