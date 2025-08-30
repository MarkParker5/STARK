from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, Type, TypeAlias

from typing_extensions import NamedTuple

from .expressions import dictionary

if TYPE_CHECKING:
    from ..types import Object
    ObjectType: TypeAlias = Type[Object]


@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
    parameters: dict[str, Object | None]

class ParseError(Exception):
    pass

class PatternParameter(NamedTuple):
    name: str
    type: ObjectType
    optional: bool

class ParameterMatch(NamedTuple):
    name: str
    regex_substr: str  # not sure this is needed anymore
    parsed_obj: Object | None
    parsed_substr: str

def any_of(*args: str) -> str:
    return '(' + '|'.join(args) + ')'

class Pattern:

    parameters: dict[str, PatternParameter]
    compiled: str

    _origin: str
    _parameter_regex: re.Pattern
    _parameter_types: dict[str, ObjectType] = {} # static

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_parameter_regex()
        self.parameters = dict(self._get_parameters())
        self.compiled = self._compile()

    async def match(self, string: str, objects_cache: dict[str, Object] | None = None) -> list[MatchResult]:

        if objects_cache is None:
            objects_cache = {} # TODO: improve cache structure

        matches: list[MatchResult] = []

        logger.debug(f"Starting looking for \"{self.compiled}\" in \"{string}\"")

        # forces non-greedy regex of greedy objects to stretch till the end, but has fallback tail capturing mechanism
        # TODO: triple check this and whether tail capturing group is necessary
        # trailing_anchor = r'(.*?)$'
        # trailing_anchor = r'$'
        trailing_anchor = r''

        for match in sorted(re.finditer(self.compiled+trailing_anchor, string), key = lambda match: match.start()):

            if match.start() == match.end():
                continue # skip empty

            # start and end in string, not in match.group(0)
            # TODO: consider moving it inside the loop
            # match_start = match.start()
            # match_end = match.end()
            command_str = string[match.start():match.end()].strip()
            match_str_groups = match.groupdict()

            # parsed_parameters: dict[str, ParameterMatch | None] = {}
            parsed_parameters: dict[str, ParameterMatch] = {}

            logger.debug(f'Captured candidate "{command_str}"')

            while True:

                # rerun regex to recapture parameters after previous parameter took it's substring

                # prefill parsed values with exact substrings
                # prefill = {name: parameter.parsed_substr for name, parameter in parsed_parameters.items() if parameter} # give empty matches a second chance
                # prefill = {name: parameter.parsed_substr if parameter else '' for name, parameter in parsed_parameters.items()} # empty matches
                prefill = {name: parameter.parsed_substr for name, parameter in parsed_parameters.items()}

                # re-run regex only in the current command_str
                compiled = self._compile(prefill=prefill)+trailing_anchor
                new_matches = list(re.finditer(compiled, command_str))

                logger.debug(f'Recapturing parameters command_str={command_str} prefill={prefill} compiled={compiled}')
                if not new_matches:
                    break # everything's parsed (probably not successfully)

                new_match = new_matches[0]
                # match_start = match.start()
                # match_end = match.end()
                command_str = string[match.start():match.end()].strip()

                logger.debug(f'Match: {new_match.groupdict()}')
                for k, v in new_match.groupdict().items():
                    logger.debug(f'{k}: {v}\t{k in self.parameters}\t{k not in prefill}\t{new_match.start(k) != -1}\t{new_match.start(k)}\t{bool(v.strip() if v else "")}\t{v}')

                match_str_groups = dict(filter(
                    # x: (0: name, 1: substr); TODO: named tuple
                    lambda x: \
                        # handle only own parameter names
                        x[0] in self.parameters \
                        # skip prefilled names
                        and x[0] not in prefill \
                        # skip not found names
                        and new_match.start(x[0]) != -1 \
                        # skip whitespace-only values
                        and x[1].strip(),
                    new_match.groupdict().items()
                ))

                logger.debug(f'Found parameters: {[(new_match.start(name), name, match_str_groups[name]) for name in sorted(match_str_groups.keys(), key=lambda n: (int(self.parameters[n].type.greedy), new_match.start(n)))]}')

                if not match_str_groups:
                    break # everything's parsed (probably successfully)

                # parse next parameter

                name = min(
                    match_str_groups.keys(),
                    key=lambda name: (
                        int(self.parameters[name].type.greedy), # parse greedy the last so they don't absorb neighbours
                        new_match.start(name) # parse left to right
                    )
                )
                raw_param_substr = match_str_groups[name].strip()

                logger.debug(f'Parsing {name} from {raw_param_substr}')

                # try to get object from cache
                for cached_parsed_substr, cached_parsed_obj in objects_cache.items():
                    continue
                    # TODO: review cache structure and search; current is broken
                    # if cached_parsed_substr in raw_param_substr:
                    #     logging.debug(f'Using cached object for {name}')
                    #     parsed_parameters[name] = ParameterMatch(
                    #         name=name,
                    #         regex_substr=raw_param_substr,
                    #         parsed_obj=cached_parsed_obj.copy(),
                    #         parsed_substr=cached_parsed_substr,
                    #     )
                    #     break
                else: # No cache, parse the object
                    object_type = self.parameters[name].type

                    try:
                        object_matches = await object_type.pattern.match(raw_param_substr, objects_cache)
                        if not object_matches:
                            raise ParseError(f"Failed to match object {object_type} from {raw_param_substr}")
                        object_pattern_match = object_matches[0]
                        parse_result = await object_type.parse(
                            from_string=object_pattern_match.substring,
                            parsed_parameters=object_pattern_match.parameters
                        )
                    except ParseError as e:
                        logger.error(f"Pattern.match ParseError: {e}")
                        # explicitly set match result with None obj so it won't stuck in an infinite retry loop
                        parsed_parameters[name] = ParameterMatch(
                            name=name,
                            regex_substr=raw_param_substr,
                            parsed_obj=None,
                            parsed_substr='',
                        )
                        continue

                    objects_cache[parse_result.substring] = parse_result.obj
                    parsed_parameters[name] = ParameterMatch(
                        name=name,
                        regex_substr=raw_param_substr,
                        parsed_obj=parse_result.obj,
                        parsed_substr=parse_result.substring,
                    )
                    logger.debug(f"Pattern.match: name={name} raw_param_substr={raw_param_substr} parse_result.substring={parse_result.substring}")

            # Validate parsed parameters

            # Check all required parameters are present
            # if not set(name for name, param in self.parameters.items() if not param.optional) <= set(parsed_parameters.keys()):
            #     raise ParseError(f"Did not find parameters: {set(self.parameters) - set(parsed_parameters.keys())}")

            # Fill None to missed optionals

            all_parameters = {**parsed_parameters, **{k: None for k in self.parameters if k not in parsed_parameters}}
            logger.debug(f'Parsed parameters: {all_parameters}')

            # Add match

            start = match.start()
            end = match.start() + len(command_str)

            matches.append(MatchResult(
                substring = command_str,
                start = start,
                end = end,
                parameters = {name: (parameter.parsed_obj if parameter else None) for name, parameter in all_parameters.items()}
            ))

        # Filter overlapping matches

        for prev, current in zip(matches.copy(), matches[1:]): # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.start == current.start or prev.end > current.start: # if overlap
                matches.remove(min(prev, current, key = lambda m: len(m.substring))) # remove shorter

        return sorted(matches, key = lambda m: len(m.substring), reverse = True)

    @classmethod
    def add_parameter_type(cls, object_type: ObjectType):
        error_msg = f'Can`t add parameter type "{object_type.__name__}": pattern parameters do not match properties annotated in class'
        # TODO: update schema and validation; handle optional parameters; handle short form where type is defined in object
        # assert object_type.pattern.parameters.items() <= object_type.__annotations__.items(), error_msg
        exists_type = cls._parameter_types.get(object_type.__name__)
        assert exists_type in {object_type, None}, f'Can`t add parameter type: {object_type.__name__} already exists'
        cls._parameter_types[object_type.__name__] = object_type

    # private

    def _get_parameter_regex(self) -> re.Pattern:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)(?P<optional>\?)?')

    def _get_parameters(self) -> Generator[tuple[str, PatternParameter], None, None]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_optional = bool(match.group('optional'))
            arg_type: ObjectType | None = Pattern._parameter_types.get(arg_type_name)

            if not arg_type:
                raise NameError(f'Unknown type: "{arg_type_name}" for parameter: "{arg_name}" in pattern: "{self._origin}"')

            yield arg_name, PatternParameter(arg_name, arg_type, arg_optional)

    def _compile(self, prefill: dict[str, str] | None = None) -> str: # transform Pattern to classic regex with named groups
        prefill = prefill or {}

        pattern: str = self._origin

        #   transform core expressions to regex

        for pattern_re, regex in dictionary.items():
            pattern = re.sub(pattern_re, regex, pattern)

        #   find and transform parameters like $name:Type

        for parameter in self.parameters.values():

            arg_declaration = f'\\${parameter.name}\\:{parameter.type.__name__}'
            if parameter.name in prefill:
                arg_pattern = re.escape(prefill[parameter.name])
            else:
                arg_pattern = parameter.type.pattern.compiled.replace('\\', r'\\')

            if parameter.type.greedy and arg_pattern[-1] in {'*', '+', '}', '?'}:
                arg_pattern += '?' # compensate greedy did_parse with non-greedy regex TODO: review

            pattern = re.sub(arg_declaration, f'(?P<{parameter.name}>{arg_pattern})', pattern)

        return pattern

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f'Can`t compare Pattern with {type(other)}')
        return self._origin == other._origin

    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
