from __future__ import annotations

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

        for match in sorted(re.finditer(self.compiled, string), key = lambda match: match.start()):

            if match.start() == match.end():
                continue # skip empty

            # start and end in string, not in match.group(0)
            match_start = match.start()
            match_end = match.end()
            command_str = string[match_start:match_end]
            match_str_groups = match.groupdict()

            parsed_parameters: dict[str, tuple[str, Object] | None] = {} # name: (substr, Object), TODO: named tuple

            found_parameters = sorted(
                (name for name in match_str_groups.keys() if name in self.parameters and match.start(name) != -1), # just in case; startup check should cover most cases and enforce them via regex
                key=lambda name: (
                    int(self.parameters[name].type.greedy), # greedy parsed after non-greedy claimed substrings
                    match.start(name) # parse left to right
                )
            ) # TODO: populate after re-regex

            print('Gonna parse', [(i, name, match_str_groups[name], match.start(name)) for i, name in dict(enumerate(found_parameters)).items()])

            while found_parameters:
                name = found_parameters.pop(0)
                raw_param_substr = match_str_groups[name]

                if not raw_param_substr:
                    print(f'{name} is empty')
                    continue

                raw_param_substr = raw_param_substr.strip()

                print(f'Parsing {name} from {raw_param_substr}')

                # TODO: double-check optional parameter

                for cached_parsed_substr, cached_parsed_obj in objects_cache.items():
                    # try to get object from cache
                    if cached_parsed_substr in raw_param_substr:
                        parsed_parameters[name] = (cached_parsed_substr, cached_parsed_obj.copy())
                        break
                else: # No cache, parse the object
                    object_type = self.parameters[name].type

                    try:
                        parse_result = await object_type.parse(
                            from_string = raw_param_substr,
                            parameters = match_str_groups, # TODO: rename to raw_parameters
                        )
                        objects_cache[parse_result.substring] = parse_result.obj
                        parsed_parameters[name] = (parse_result.substring, parse_result.obj)
                    except ParseError as e:
                        print(f"Pattern.match ParseError: {e}")
                        continue

                # recapture next raw parameters after stripping the parsed parameter

                prefill = {name: substr for name, (substr, _) in parsed_parameters.items()} # TODO: handle None
                updated_matches = list(re.finditer(self._compile(prefill=prefill), command_str))
                print('Recapturing parameters', self._compile(prefill=prefill), command_str)
                assert updated_matches, "Unexpected Error: No matches found after recapturing parameters" # TODO: handle
                match_str_groups = updated_matches[0].groupdict()
                # TODO: update found_parameters in case empty match became not empty; also might be useful to handle the opposite: some parameter raw substr became empty
                # TODO: remove duplicating and put in the start of the do_while loop

            # Validate parsed parameters

            # Check all required parameters are present
            assert set(name for name, param in self.parameters.items() if not param.optional) <= set(parsed_parameters.keys()), f"Unexpected Error: Missing parameters {set(self.parameters) - set(parsed_parameters.keys())}"
            # Fill None to missed optionals
            parsed_parameters |= {k: None for k in self.parameters if k not in parsed_parameters}

            # Strip full command

            for name, parameter in parsed_parameters.items():
                if parameter is None: continue
                parameter_substr, _ = parameter
                parameter_start = match_str_groups[name].find(parameter_substr)
                parameter_end = parameter_start + len(parameter_substr)

                # adjust start, end and substring after parsing parameters
                if match.start(name) == match.start() and parameter_start != 0:
                    match_start = match.start(name) + parameter_start
                if match.end(name) == match.end() and parameter_end != len(parameter_substr):
                    match_end = match.start(name) + parameter_start + parameter_end

            substring = string[match_start:match_end].strip()
            start = match_start + string[match_start:match_end].find(substring)
            end = start + len(substring)

            matches.append(MatchResult(
                substring = substring,
                start = start,
                end = end,
                parameters = {name: (parameter[1] if parameter else None) for name, parameter in parsed_parameters.items()}
            ))

        # filter overlapping matches

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
            pattern = re.sub(arg_declaration, f'(?P<{parameter.name}>{arg_pattern})', pattern)

        return pattern

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pattern):
            raise NotImplementedError(f'Can`t compare Pattern with {type(other)}')
        return self._origin == other._origin

    def __repr__(self) -> str:
        return f'<Pattern \'{self._origin}\'>'
