from __future__ import annotations
from typing import Type, Generator, TypeAlias
from dataclasses import dataclass
import re

from .expressions import dictionary


VIObjectType: TypeAlias = Type['VIObject']

@dataclass
class MatchResult:
    substring: str
    parameters: dict[str, 'VIObject']

class Pattern:
    
    parameters: dict[str, VIObjectType]
    compiled: str
    
    _origin: str
    _parameter_regex: re.compile
    _parameter_types: dict[str, VIObjectType] = {} # static

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_parameter_regex()
        self.parameters = dict(self._get_parameters())
        self.compiled = self._compile()
        
    def match(self, string: str) -> MatchResult | None:
        
        if matches := sorted(re.finditer(self.compiled, string), key = lambda m: len(m.group(0))):
            # TODO: sort by parameters count instead of substring length
            match = matches[-1]
            substring = match.group(0).strip()
            str_groups = match.groupdict()
            
            parameters: dict[str, 'VIObject'] = {}
            
            for name, vi_type in self.parameters.items():
                if not str_groups.get(name):
                    continue
                parameters[name] = vi_type.parse(from_string = str_groups[name], parameters = str_groups)
            
            return MatchResult(substring, parameters)
        
        return None
    
    @classmethod
    def add_parameter_type(cls, vi_type: VIObjectType):
        error_msg = f'Can`t add parameter type "{vi_type.__name__}": pattern parameters do not match properties annotated in class'
        assert vi_type.pattern.parameters.items() <= vi_type.__annotations__.items(), error_msg
        assert cls._parameter_types.get(vi_type.__name__) is None, f'Can`t add parameter type: {vi_type.__name__} already exists'
        cls._parameter_types[vi_type.__name__] = vi_type
        
    def _get_parameter_regex(self) -> re.compile:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)')
    
    def _get_parameters(self) -> Generator[tuple[str, VIObjectType]]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_type: VIObjectType = Pattern._parameter_types.get(arg_type_name)
            
            if not arg_type: 
                raise NameError(f'Unknown type: "{arg_type_name}" for parameter: "{arg_name}" in pattern: "{self._origin}"')
            
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
