from __future__ import annotations
from typing import Type, Generator, TypeAlias
from dataclasses import dataclass
import re

from .expressions import dictionary


VIObjectType: TypeAlias = Type['VIObject']

@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
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
        
    def match(self, string: str, viobjects_cache: dict[str, 'VIObject'] = None) -> list[MatchResult]:
        
        viobjects_cache = viobjects_cache or {}
        matches: list[MatchResult] = []
        
        for match in sorted(re.finditer(self.compiled, string), key = lambda match: match.start()):
            
            match_start = match.start()
            match_end = match.end()
            match_str_groups = match.groupdict()
            
            # parse parameters
            
            parameters: dict[str, 'VIObject'] = {}
            
            for name, vi_type in self.parameters.items():
                if not match_str_groups.get(name):
                    continue
                
                parameter_str = match_str_groups[name]
                
                for parsed_substr, parsed_obj in viobjects_cache.items():
                    if parsed_substr in parameter_str:
                        parameters[name] = parsed_obj.copy()
                        parameter_start = parameter_str.find(parsed_substr)
                        parameter_end = parameter_start + len(parsed_substr)
                        break
                else:
                    parameters[name], parameter_start, parameter_end = vi_type.parse(from_string = parameter_str, parameters = match_str_groups) 
                    parameter_substr = parameter_str[parameter_start:parameter_end]
                    viobjects_cache[parameter_substr] = parameters[name]
                    
                # adjust start, end and substring after parsing parameters
                if match.start(name) == 0 and parameter_start != 0:
                    match_start = parameter_start
                if match.end(name) == len(string) and parameter_end != len(parameter_str):
                    match_end = parameter_end 
            
            matches.append(MatchResult(
                substring = match.group(0).strip()[match_start:match_end],
                start = match_start,
                end = match_end,
                parameters = parameters
            ))
            
        # filter overlapping matches
        
        for prev, current in zip(matches.copy(), matches[1:]): # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.start == current.start or prev.end > current.start: # if overlap 
                matches.remove(min(prev, current, key = lambda m: len(m.substring))) # remove shorter
                
        # TODO: filter by unique parameters | handle the same command with the same parameters
            
        return matches
    
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
