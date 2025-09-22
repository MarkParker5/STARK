from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generator, Type, TypeAlias

from typing_extensions import NamedTuple

from .rules import rules_list

if TYPE_CHECKING:
    from ..types import Object
    ObjectType: TypeAlias = Type[Object]
import logging

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
    parameters: dict[str, Object | None] # TODO: use ParameterMatch

from .parsing import ObjectParser, ParseError, parse_object


@dataclass
class PatternParameter:
    name: str
    group_name: str # includes tree prefix
    type_name: str
    optional: bool

class RegisteredParameterType(NamedTuple):
    name: str
    type: ObjectType
    parser: ObjectParser

class ParameterMatch(NamedTuple):
    name: str
    regex_substr: str  # not sure this is needed anymore
    parsed_obj: Object | None
    parsed_substr: str
    # TODO: add and use start and/end span to resolve duplication

class Pattern:

    parameters: dict[str, PatternParameter]
    compiled: str

    _origin: str
    _parameter_regex: re.Pattern
    _parameter_types: dict[str, RegisteredParameterType] = {}

    def __init__(self, origin: str):
        self._origin = origin
        self._parameter_regex = self._get_pattern_parameter_annotation_regex()
        self.parameters = dict(self._get_parameters_annotation_from_pattern())
        self.compiled = self.compile() # TODO: remove or redo
        self._update_group_name_to_param()

    @classmethod
    def add_parameter_type(cls, object_type: ObjectType, parser: ObjectParser | None = None):
        from ..types import Object
        assert issubclass(object_type, Object), f'Can`t add parameter type "{object_type.__name__}": it is not a subclass of Object'
        error_msg = f'Can`t add parameter type "{object_type.__name__}": pattern parameters do not match properties annotated in class'
        # TODO: update schema and validation; handle optional parameters; handle short form where type is defined in object
        # assert object_type.pattern.parameters.items() <= object_type.__annotations__.items(), error_msg
        exists_type = Pattern._parameter_types.get(object_type.__name__)
        assert exists_type is None or exists_type.type == object_type, f'Can`t add parameter type: {object_type.__name__} already exists'
        Pattern._parameter_types[object_type.__name__] = RegisteredParameterType(
            name=object_type.__name__,
            type=object_type,
            parser=parser or ObjectParser()
        )

    async def match(self, string: str, objects_cache: dict[str, Object] | None = None) -> list[MatchResult]:
        if objects_cache is None:
            objects_cache = {} # TODO: improve cache structure

        compiled = self.compiled # self.compile()
        logger.debug(f"Starting looking for \"{self._origin}\" \"{compiled=}\" in \"{string}\"")

        matches = []
        initial_matches = self._find_initial_matches(compiled, string)
        for match in initial_matches:
            if match.start() == -1 or match.start() == match.end():
                continue # skip empty

            new_match = None
            command_substr = string[match.start():match.end()]
            new_match, parsed_parameters = await self._parse_parameters_for_match(command_substr, objects_cache)
            assert new_match is not None, "new_match should not be None"
            new_match = new_match or match

            # Validate parsed parameters

            # Check all required parameters are present TODO: properly mark optional ones
            # if not set(name for name, param in self.parameters.items() if not param.optional) <= set(k for k, v in parsed_parameters.items() if v.parsed_obj is not None):
            #     raise ParseError(f"Did not find parameters: {set(self.parameters.keys()) - set(k for k, v in parsed_parameters.items() if v.parsed_obj is not None)}")

            all_parameters = {
                **{param.name: None for param in self.parameters.values()}, # all with optional
                **{k:v for k,v in parsed_parameters.items() if v.parsed_obj is not None}, # set parsed values
            }
            logger.debug(f'Parsed parameters: {all_parameters}')

            # Add match

            start = match.start() + new_match.start()
            end = match.start() + new_match.end()
            command_str = string[start:end].strip()

            matches.append(MatchResult(
                substring = command_str,
                start = start,
                end = end,
                parameters = {name: (parameter.parsed_obj if parameter else None) for name, parameter in all_parameters.items()}
            ))
            logger.debug(f'Match result: {matches[-1]}')

        matches = self._filter_overlapping_matches(matches)
        return sorted(matches, key = lambda m: len(m.substring), reverse = True)

    def _find_initial_matches(self, compiled: str, string: str) -> list[re.Match]:
        return sorted(re.finditer(compiled, string), key = lambda match: match.start())

    async def _parse_parameters_for_match(self, string: str, objects_cache: dict[str, Object]) -> tuple[re.Match | None, dict[str, ParameterMatch]]:
        parsed_parameters: dict[str, ParameterMatch] = {}

        logger.debug(f'Captured candidate "{string}"')

        new_match = None

        while True:

            # rerun regex to recapture parameters after previous parameter took it's substring

            # prefill parsed values with exact substrings
            # prefill = {name: parameter.parsed_substr for name, parameter in parsed_parameters.items() if parameter} # give empty matches a second chance
            # prefill = {name: parameter.parsed_substr if parameter else '' for name, parameter in parsed_parameters.items()} # empty matches
            prefill = {name: parameter.parsed_substr for name, parameter in parsed_parameters.items()}

            # re-run regex only in the current command_str
            compiled = self.compile(prefill=prefill)
            new_matches = list(re.finditer(compiled, string))

            logger.debug(f'Re capturing parameters string="{string}" prefill={prefill} compiled="{compiled}"')

            if not new_matches:
                break # everything's parsed (probably not successfully)

            new_match = new_matches[0]

            logger.debug(f'Re Match: {new_match.groupdict()}')

            # Log

            for group_name, param in self.group_name_to_param.items():
                v = new_match.group(group_name)
                logger.debug(f'{group_name}: {v}\t{param is not None}\t{group_name not in prefill}\t{new_match.start(group_name) != -1}\t{new_match.start(group_name)}\t{bool(v.strip() if v else "")}\t{v}')

            # Filter remaining regex matched params to parse next

            match_str_groups = {
                name: new_match.group(name)
                for name in self.group_name_to_param
                # skip prefilled names
                if name not in prefill
                # skip not found names
                and new_match.start(name) != -1
                # skip whitespace-only values
                and new_match.group(name) and new_match.group(name).strip()
            }

            # Log

            logger.debug(f'Found re groups: {[(new_match.start(name), name, match_str_groups[name]) for name in sorted(match_str_groups.keys(), key=lambda name: (int(Pattern._parameter_types[self.group_name_to_param[name].type_name].type.greedy), new_match.start(name)))]}')

            if not match_str_groups:
                break # everything's parsed (probably successfully)

            # Parse next parameter

            parameter_name = min(
                match_str_groups.keys(),
                key=lambda name: (
                    int(Pattern._parameter_types[self.parameters[name].type_name].type.greedy), # parse greedy the last so they don't absorb neighbours
                    new_match.start(name) # parse left to right
                )
            )
            parameter_match = await self._parse_single_parameter(parameter_name, match_str_groups[parameter_name].strip(), parsed_parameters, objects_cache)
            if parameter_match is not None:
                parsed_parameters[parameter_name] = parameter_match

        return new_match, parsed_parameters

    async def _parse_single_parameter(self, parameter_name: str, raw_param_substr: str, parsed_parameters: dict[str, ParameterMatch], objects_cache: dict[str, Object]) -> ParameterMatch | None:
        param = self.group_name_to_param[parameter_name]
        parameter_reg_type = Pattern._parameter_types[param.type_name]
        parameter_type = parameter_reg_type.type

        logger.debug(f'Parsing parameter "{parameter_name}" from "{raw_param_substr}"')

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
            try:
                object_matches = await parameter_type.pattern.match(raw_param_substr, objects_cache)
                if not object_matches:
                    raise ParseError(f"Failed to match object {parameter_type} from {raw_param_substr}")
                object_pattern_match = object_matches[0]
                parse_result = await parse_object(
                    parameter_reg_type.type,
                    parameter_reg_type.parser,
                    from_string=object_pattern_match.substring,
                    parsed_parameters=object_pattern_match.parameters
                )
            except ParseError as e:
                logger.debug(f"Pattern.match ParseError: {e}")
                # explicitly set match result with None obj so it won't stuck in an infinite retry loop
                return ParameterMatch(
                    name=param.name,
                    regex_substr=raw_param_substr,
                    parsed_obj=None,
                    parsed_substr='',
                )

            objects_cache[parse_result.substring] = parse_result.obj
            return ParameterMatch(
                name=param.name,
                regex_substr=raw_param_substr,
                parsed_obj=parse_result.obj,
                parsed_substr=parse_result.substring,
            )
        return None

    def _filter_overlapping_matches(self, matches: list[MatchResult]) -> list[MatchResult]:
        filtered = matches.copy()
        for prev, current in zip(filtered.copy(), filtered[1:]): # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.start == current.start or prev.end > current.start: # if overlap
                filtered.remove(min(prev, current, key = lambda m: len(m.substring))) # remove shorter
        return filtered

    def compile(self, group_prefix: str = '', prefill: dict[str, str] | None = None) -> str: # transform Pattern to classic regex with named groups
        prefill = prefill or {}

        pattern: str = self._origin

        #   transform core expressions to regex

        for rule in rules_list:
            if rule.func:
                pattern = re.sub(rule.pattern, rule.func, pattern)
            elif rule.replace:
                pattern = re.sub(rule.pattern, rule.replace, pattern)
            else:
                raise RuntimeError(f'Invalid rule: {rule}')

        #   find and transform parameters like $name:Type

        for parameter in self.parameters.values():
            parameter_type = Pattern._parameter_types[parameter.type_name].type

            arg_declaration = f'\\${parameter.name}\\:{parameter_type.__name__}' # NOTE: special chars escaped for regex
            if parameter.name in prefill:
                arg_pattern = re.escape(prefill[parameter.name])
            else: # replace pattern annotation with compiled regex
                parameter.group_name = ((group_prefix + '_') if group_prefix else '') + parameter.name
                arg_pattern = parameter_type.pattern.compile(group_prefix=parameter.group_name).replace('\\', r'\\')

                if parameter_type.greedy and arg_pattern[-1] in {'*', '+', '}', '?'}:
                    # compensate greedy did_parse with non-greedy regex, so it won't consume next params during initial regex
                    arg_pattern += '?'
                    if pattern.endswith(f'${parameter.name}:{parameter_type.__name__}'): # NOTE: regex chars are NOT escaped
                        # compensate the last non_greedy regex to allow consuming till the end of the string
                        # middle greedy params are limited/stretched by neighbor params
                        arg_pattern += '$'

            pattern = re.sub(arg_declaration, f'(?P<{parameter.group_name}>{arg_pattern})', pattern)

        return pattern

    # processing pattern

    def _get_pattern_parameter_annotation_regex(self) -> re.Pattern:
        # types = '|'.join(Pattern._parameter_types.keys())
        # return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>(?:' + types + r'))')
        # do not use types list because it prevents validation of unknown types
        return re.compile(r'\$(?P<name>[A-z][A-z0-9]*)\:(?P<type>[A-z][A-z0-9]*)(?P<optional>\?)?')

    def _get_parameters_annotation_from_pattern(self) -> Generator[tuple[str, PatternParameter], None, None]:
        for match in re.finditer(self._parameter_regex, self._origin):
            arg_name = match.group('name')
            arg_type_name = match.group('type')
            arg_optional = bool(match.group('optional'))

            reg_type: RegisteredParameterType | None = Pattern._parameter_types.get(arg_type_name)

            if not reg_type:
                raise NameError(f'Unknown type: "{arg_type_name}" for parameter: "{arg_name}" in pattern: "{self._origin}"')

            yield arg_name, PatternParameter(arg_name, arg_name, arg_type_name, arg_optional)

    def _update_group_name_to_param(self):
        self.group_name_to_param = {param.group_name: param for param in self.parameters.values()}

    # dunder methods

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f'Can`t compare Pattern with {type(other)}')
        return self._origin == other._origin

    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
