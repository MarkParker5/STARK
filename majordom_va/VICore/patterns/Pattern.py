from __future__ import annotations
from typing import Type, Generator, TypeAlias, Protocol
from dataclasses import dataclass
import re

from .expressions import dictionary


VIObject: TypeAlias = 'VIObject' # type: ignore
VIObjectType: TypeAlias = Type[VIObject] # type: ignore

@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
    parameters: dict[str, VIObject]

class Pattern:
    
    parameters: dict[str, VIObjectType]
    compiled: str
    
    _origin: str
    _parameter_regex: re.Pattern
    _parameter_types: dict[str, VIObjectType] = {} # static

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_parameter_regex()
        self.parameters = dict(self._get_parameters())
        self.compiled = self._compile()
        
    def match(self, string: str, viobjects_cache: dict[str, VIObject] | None = None) -> list[MatchResult]:
        
        if viobjects_cache is None:
            viobjects_cache = {}
            
        matches: list[MatchResult] = []
        
        for match in sorted(re.finditer(self.compiled, string), key = lambda match: match.start()):
            
            if match.start() == match.end():
                continue # skip empty
            
            # start and end in string, not in match.group(0) 
            match_start = match.start()
            match_end = match.end()
            match_str_groups = match.groupdict()
            
            # parse parameters
            
            parameters: dict[str, VIObject] = {}
            
            for name, vi_type in self.parameters.items():
                if not match_str_groups.get(name):
                    continue
                
                parameter_str = match_str_groups[name].strip()
                
                for parsed_substr, parsed_obj in viobjects_cache.items():
                    if parsed_substr in parameter_str:
                        parameters[name] = parsed_obj.copy()
                        parameter_str = parsed_substr
                        break
                else:
                    parse_result = vi_type.parse(from_string = parameter_str, parameters = match_str_groups) 
                    viobjects_cache[parse_result.substring] = parse_result.obj
                    parameters[name] = parse_result.obj
                    parameter_str = parse_result.substring
                
                parameter_start = match_str_groups[name].find(parameter_str)
                parameter_end = parameter_start + len(parameter_str)
                
                # adjust start, end and substring after parsing parameters
                if match.start(name) == match.start() and parameter_start != 0:
                    match_start = match.start(name) + parameter_start
                if match.end(name) == match.end() and parameter_end != len(parameter_str):
                    match_end = match.start(name) + parameter_start + parameter_end 
                    
            # strip original string
            
            substring = string[match_start:match_end].strip()
            start = match_start + string[match_start:match_end].find(substring)
            end = start + len(substring)
            
            matches.append(MatchResult(
                substring = substring,
                start = start,
                end = end,
                parameters = parameters
            ))
            
        # filter overlapping matches
        
        for prev, current in zip(matches.copy(), matches[1:]): # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.start == current.start or prev.end > current.start: # if overlap 
                matches.remove(min(prev, current, key = lambda m: len(m.substring))) # remove shorter
            
        return sorted(matches, key = lambda m: len(m.substring), reverse = True)
    
    @classmethod
    def add_parameter_type(cls, vi_type: VIObjectType):
        error_msg = f'Can`t add parameter type "{vi_type.__name__}": pattern parameters do not match properties annotated in class'
        assert vi_type.pattern.parameters.items() <= vi_type.__annotations__.items(), error_msg
        assert cls._parameter_types.get(vi_type.__name__) is None, f'Can`t add parameter type: {vi_type.__name__} already exists'
        cls._parameter_types[vi_type.__name__] = vi_type
        
    # private
    
    def _get_parameter_regex(self) -> re.Pattern:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)')
    
    def _get_parameters(self) -> Generator[tuple[str, VIObjectType], None, None]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_type: VIObjectType | None = Pattern._parameter_types.get(arg_type_name)
            
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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f'Can`t compare Pattern with {type(other)}')
        return self._origin == other._origin
    
    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
