from __future__ import annotations
from typing import Type, Generator, TypeAlias, TYPE_CHECKING
from dataclasses import dataclass
import re
from asyncer import create_task_group, SoonValue

from stark.models.transcription import Transcription, KaldiMBR
from stark.general.localisation import Localizer
from .expressions import dictionary
if TYPE_CHECKING:
    from ..types import Object, ParseResult, ParseError
    ObjectType: TypeAlias = Type[Object]


@dataclass
class MatchResult:
    subtrack: KaldiMBR
    start: float
    end: float
    parameters: dict[str, Object]

class Pattern:
    
    parameters: dict[str, ObjectType]
    compiled: dict[str, str]
    
    _origin: str
    _parameter_regex: re.Pattern
    _parameter_types: dict[str, ObjectType] = {} # static

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_parameter_regex()
        self.parameters = dict(self._get_parameters())
        
    def prepare(self, localizer: Localizer):
        for language in localizer.languages:
            self.compiled[language] = self._get_compiled(language, localizer)
        
    async def match(self, transcription: Transcription, localizer: Localizer, objects_cache: dict[str, Object] | None = None) -> list[MatchResult]:
        if not self._origin:
            return []
        
        if objects_cache is None:
            objects_cache = {}
            
        matches: list[MatchResult] = []
        
        for language_code, track in transcription.origins.items():
            
            string = track.text
            compiled = self._get_compiled(language_code, localizer)
            
            # map suggestions to more comfortable data structure
            
            suggestions: dict[str, set[str]] = dict()
            for variant, keyword in transcription.suggestions:
                if not keyword in suggestions:
                    suggestions[keyword] = set()
                suggestions[keyword].add(variant)
            
            # update compiled re to match keyword variants
            
            for keyword, variants in suggestions.items():
                if keyword in compiled:
                    compiled = compiled.replace(keyword, f'[{keyword}|{"|".join(variants)}]')
                    
            # search all matches
            
            for match in sorted(re.finditer(compiled, string), key = lambda match: match.start()):
                
                if match.start() == match.end():
                    continue # skip empty
                
                # start and end in string, not in match.group(0) 
                match_start = match.start()
                match_end = match.end()
                match_str_groups = match.groupdict()
                
                # parse parameters
                
                parameters: dict[str, Object] = {}
                substrings: dict[str, str] = {}
                futures: list[tuple[str, SoonValue[ParseResult | None]]] = []
                
                # run concurrent objects parsing
                async with create_task_group() as group:
                    for name, object_type in self.parameters.items():
                        if not match_str_groups.get(name):
                            continue
                        
                        parameter_str = match_str_groups[name].strip()
                        
                        for parsed_substr, parsed_obj in objects_cache.items():
                            if parsed_substr in parameter_str:
                                parameters[name] = parsed_obj.copy()
                                parameter_str = parsed_substr
                                substrings[name] = parsed_substr
                                break
                        else:
                            
                            start_index = match.start(name)
                            end_index = match.end(name)
                            time_range = next(iter(track.get_time(parameter_str, start_index, end_index)))
                            subtrack = track.get_slice(*time_range)
                            subtranscription = transcription.get_slice(*time_range)
                            subtranscription.suggestions = [s for s in subtranscription.suggestions if s[0] in subtrack.text]
                            
                            async def parse() -> ParseResult | None:
                                try:
                                    parse_result = await object_type.parse(subtrack, subtranscription, match_str_groups)
                                except ParseError:
                                    return None
                                objects_cache[parse_result.substring] = parse_result.obj
                                return parse_result
                            
                            futures.append((name, group.soonify(parse)()))
                
                # read futures
                for name, future in futures:
                    parse_result = future.value
                    if not parse_result:
                        continue
                    parameters[name] = parse_result.obj
                    substrings[name] = parse_result.substring
                    
                # save parameters
                for name in parameters.keys():
                    parameter_str = substrings[name]
                    parameter_start = match_str_groups[name].find(parameter_str)
                    parameter_end = parameter_start + len(parameter_str)
                    
                    # adjust start, end and substring after parsing parameters
                    if match.start(name) == match.start() and parameter_start != 0:
                        match_start = match.start(name) + parameter_start
                    if match.end(name) == match.end() and parameter_end != len(parameter_str):
                        match_end = match.start(name) + parameter_start + parameter_end 
                        
                # strip original string
                
                substring = string[match_start:match_end].strip()
                start, end = next(iter(track.get_time(substring)))
                subtrack = track.get_slice(start, end)
                
                matches.append(MatchResult(
                    subtrack = subtrack,
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
    def add_parameter_type(cls, object_type: ObjectType):
        error_msg = f'Can`t add parameter type "{object_type.__name__}": pattern parameters do not match properties annotated in class'
        assert object_type.pattern.parameters.items() <= object_type.__annotations__.items(), error_msg
        exists_type = cls._parameter_types.get(object_type.__name__)
        assert exists_type in {object_type, None}, f'Can`t add parameter type: {object_type.__name__} already exists'
        cls._parameter_types[object_type.__name__] = object_type
        
    # private
    
    def _get_parameter_regex(self) -> re.Pattern:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)')
    
    def _get_parameters(self) -> Generator[tuple[str, ObjectType], None, None]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_type: ObjectType | None = Pattern._parameter_types.get(arg_type_name)
            
            if not arg_type: 
                raise NameError(f'Unknown type: "{arg_type_name}" for parameter: "{arg_name}" in pattern: "{self._origin}"')
            
            yield arg_name, arg_type
            
    def _get_compiled(self, language: str, localizer: Localizer) -> str: # transform Pattern to classic regex with named groups
        if language in self.compiled:
            return self.compiled[language]
        
        pattern: str = localizer.get_localizable(self._origin, language) or self._origin

        #   transform core expressions to regex
        
        for pattern_re, regex in dictionary.items():
            pattern = re.sub(pattern_re, regex, pattern)

        #   find and transform parameters like $name:Type
        
        for name, object_type in self.parameters.items():
            
            arg_declaration = f'\\${name}\\:{object_type.__name__}'
            arg_pattern = object_type.pattern.compiled.replace('\\', r'\\')
            pattern = re.sub(arg_declaration, f'(?P<{name}>{arg_pattern})', pattern)
        
        return pattern
    
    # magic methods
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f'Can`t compare Pattern with {type(other)}')
        return self._origin == other._origin
    
    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
