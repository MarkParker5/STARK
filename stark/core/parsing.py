from __future__ import annotations

import re
from abc import ABC
from dataclasses import dataclass

from typing_extensions import NamedTuple

from stark.core.patterns.pattern import Pattern
from stark.core.patterns.rules import rules_list
from stark.core.types import Object
from stark.core.types.string import String
from stark.core.types.word import Word

type ObjectType = type[Object]


import logging

logger = logging.getLogger(__name__)


class ParseResult(NamedTuple):
    obj: Object
    substring: str


class ParseError(Exception):
    pass


class RegisteredParameterType(NamedTuple):  # TODO: use dataclasses instead of names tuples
    name: str
    type: ObjectType
    parser: ObjectParser


@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
    parameters: dict[str, Object | None]  # TODO: use ParameterMatch?


class ParameterMatch(NamedTuple):
    name: str
    # regex_substr: str  # not sure this is needed anymore
    parsed_obj: Object | None
    parsed_substr: str
    # TODO: add and use start and/end span to resolve duplication


@dataclass
class RecognizedEntity:
    # span: Span
    substring: str
    type: ObjectType
    key: str | None = None


# TODO: implement lru cache for (substr, Type[NLObject]) -> NLObject and for pattern.compile


class ObjectParser(ABC):
    async def did_parse(self, obj: Object, from_string: str) -> str:
        """
        This method is called after parsing from string and setting parameters found in pattern.
        You will very rarely, if ever, need to call this method directly.

        Override this method for more complex parsing from string.

        Returns:
            Minimal substring that is required to parse value.

        Raises:
            ParseError: if parsing failed.
        """
        return from_string


class PatternParser:
    parameter_types_by_name: dict[str, RegisteredParameterType] = {}

    def __init__(self):
        self.parameter_types_by_name = {}
        self.register_parameter_type(Word)
        self.register_parameter_type(String)

    def register_parameter_type(
        self,
        object_type: ObjectType,
        parser: ObjectParser | None = None,
        # TODO: consider adding lang parameter
    ):
        assert issubclass(object_type, Object), f'Can`t add parameter type "{object_type.__name__}": it is not a subclass of Object'
        # error_msg = f'Can`t add parameter type "{object_type.__name__}": pattern parameters do not match properties annotated in class'
        # TODO: update schema and validation; handle optional parameters; handle short form where type is defined in object
        # assert object_type.pattern.parameters.items() <= object_type.__annotations__.items(), error_msg
        exists_type = self.parameter_types_by_name.get(object_type.__name__)
        assert exists_type is None or exists_type.type == object_type, f"Can`t add parameter type: {object_type.__name__} already exists"
        self.parameter_types_by_name[object_type.__name__] = RegisteredParameterType(
            name=object_type.__name__, type=object_type, parser=parser or ObjectParser()
        )

    async def parse_object_name(self, class_name: str, from_string: str, parsed_parameters: dict[str, Object | None] | None = None) -> ParseResult:
        return await self.parse_object(self.parameter_types_by_name[class_name].type, from_string, parsed_parameters)

    async def parse_object(
        self,
        object_type: ObjectType,
        from_string: str,
        parsed_parameters: dict[str, Object | None] | None = None,
    ) -> ParseResult:
        parser: ObjectParser = self.parameter_types_by_name[object_type.__name__].parser
        obj = object_type(from_string)  # temp/default value, may be overridden by did_parse
        parsed_parameters = parsed_parameters or {}
        assert parsed_parameters.keys() <= {p.name for p in object_type.pattern.parameters.values() if not p.optional}

        for name in object_type.pattern.parameters:
            value = parsed_parameters[name]
            setattr(obj, name, value)

        substring = await parser.did_parse(obj, from_string)
        substring = await obj.did_parse(substring)

        assert substring.strip(), ValueError(f"Parsed substring must not be empty. Object: {obj}, Parser: {parser}")
        assert substring in from_string, ValueError(
            f"Parsed substring must be a part of the original string. There is no {substring} in {from_string}. Object: {obj}, Parser: {parser}"
        )
        assert obj.value is not None, ValueError(
            f"Parsed object {obj} must have a `value` property set in did_parse method. Object: {obj}, Parser: {parser}"
        )

        return ParseResult(obj, substring)

    async def match(self, pattern: Pattern, string: str, recognized_entities: list[RecognizedEntity] | None = None) -> list[MatchResult]:
        recognized_entities = recognized_entities or []
        compiled = self._compile_pattern(pattern)  # TODO: consider caching
        logger.debug(f'Starting looking for "{pattern=}" "{compiled=}" in "{string}"')

        matches = []
        initial_matches = self._find_initial_matches(compiled, string)
        for match in initial_matches:
            if match.start() == -1 or match.start() == match.end():
                continue  # skip empty

            new_match = None
            command_substr = string[match.start() : match.end()]
            new_match, parsed_parameters = await self._parse_parameters_for_match(pattern, command_substr, recognized_entities)
            assert new_match is not None, "new_match should not be None"
            new_match = new_match or match

            # Validate parsed parameters

            # Check all required parameters are present TODO: properly mark optional ones
            # if not set(name for name, param in self.parameters.items() if not param.optional) <= set(k for k, v in parsed_parameters.items() if v.parsed_obj is not None):
            #     raise ParseError(f"Did not find parameters: {set(self.parameters.keys()) - set(k for k, v in parsed_parameters.items() if v.parsed_obj is not None)}")

            all_parameters = {
                **{param.name: None for param in pattern.parameters.values()},  # all with optional
                **{k: v for k, v in parsed_parameters.items() if v.parsed_obj is not None},  # set parsed values
            }
            logger.debug(f"Parsed parameters: {all_parameters}")

            # Add match

            start = match.start() + new_match.start()
            end = match.start() + new_match.end()
            command_str = string[start:end].strip()

            matches.append(
                MatchResult(
                    substring=command_str,
                    start=start,
                    end=end,
                    parameters={name: (parameter.parsed_obj if parameter else None) for name, parameter in all_parameters.items()},
                )
            )
            logger.debug(f"Match result: {matches[-1]}")

        matches = self._filter_overlapping_matches(matches)
        return sorted(matches, key=lambda m: len(m.substring), reverse=True)

    def _find_initial_matches(self, compiled: str, string: str) -> list[re.Match]:
        return sorted(re.finditer(compiled, string), key=lambda match: match.start())

    async def _parse_parameters_for_match(
        self, pattern: Pattern, string: str, recognized_entities: list[RecognizedEntity]
    ) -> tuple[re.Match | None, dict[str, ParameterMatch]]:
        parsed_parameters: dict[str, ParameterMatch] = {}
        logger.debug(f'Captured candidate "{string}"')

        new_match = None

        while True:
            # rerun regex to recapture parameters after previous parameter took it's substring
            # prefill parsed values with exact substrings (replace regex capturing group with the exact substring) to:
            #     1. allow neighboring parameters with greedy pattern catch more string
            #     2. remove already parsed parameters from match groups
            #     3. improve performance by simplifying regex
            prefill = {name: parameter.parsed_substr for name, parameter in parsed_parameters.items()}

            # re-run regex only in the current command_str
            compiled = self._compile_pattern(pattern, prefill=prefill)
            new_matches = list(re.finditer(compiled, string))

            logger.debug(f'Re capturing parameters {string} prefill={prefill} compiled="{compiled}"')

            if not new_matches:
                break  # everything's parsed (probably not successfully)

            new_match = new_matches[0]

            logger.debug(f"Re Match: {new_match.groupdict()}")

            # Log

            for group_name, param in pattern.group_name_to_param.items():
                v = new_match.group(group_name)
                logger.debug(
                    f"{group_name}: {v}\t{param is not None}\t{group_name not in prefill}\t{new_match.start(group_name) != -1}\t{new_match.start(group_name)}\t{bool(v.strip() if v else '')}\t{v}"
                )

            # Filter remaining regex matched params to parse next

            match_str_groups = {
                name: new_match.group(name)
                for name in pattern.group_name_to_param
                # skip prefilled names
                if name not in prefill
                # skip not found names
                and new_match.start(name) != -1
                # skip whitespace-only values
                and new_match.group(name)
                and new_match.group(name).strip()
            }

            # Log

            logger.debug(
                f"Found re groups: {[(new_match.start(name), name, match_str_groups[name]) for name in sorted(match_str_groups.keys(), key=lambda name: (int(self.parameter_types_by_name[pattern.group_name_to_param[name].type_name].type.greedy), new_match.start(name)))]}"
            )

            if not match_str_groups:
                break  # everything's parsed (probably successfully)

            # Parse next parameter

            parameter_name = min(
                match_str_groups.keys(),
                key=lambda name: (
                    int(
                        self.parameter_types_by_name[pattern.parameters[name].type_name].type.greedy
                    ),  # parse greedy the last so they don't absorb neighbours
                    new_match.start(name),  # parse left to right
                ),
            )
            parameter_match = await self._parse_single_parameter(
                pattern, parameter_name, match_str_groups[parameter_name].strip(), recognized_entities
            )
            if parameter_match is not None:
                parsed_parameters[parameter_name] = parameter_match

        return new_match, parsed_parameters

    async def _parse_single_parameter(
        self, pattern: Pattern, parameter_name: str, raw_param_substr: str, recognized_entities: list[RecognizedEntity]
    ) -> ParameterMatch | None:
        param = pattern.group_name_to_param[parameter_name]
        parameter_reg_type = self.parameter_types_by_name[param.type_name]

        logger.debug(f'Parsing parameter "{parameter_name}" from "{raw_param_substr}"')

        # check recognized entities, update substring if found match
        for entity in recognized_entities:
            if entity.substring in raw_param_substr and entity.type is parameter_reg_type.type:
                raw_param_substr = entity.substring
                logger.debug(f"Adjusting for recognized entity: '{entity.substring}'")

        # parse the object
        try:
            object_matches = await self.match(parameter_reg_type.type.pattern, raw_param_substr)
            if not object_matches:
                raise ParseError(f"Failed to match object {parameter_reg_type.type} from {raw_param_substr}")
            object_pattern_match = object_matches[0]
            parse_result = await self.parse_object(
                parameter_reg_type.type,
                from_string=object_pattern_match.substring,
                parsed_parameters=object_pattern_match.parameters,
            )
        except ParseError as e:
            logger.debug(f"Pattern.match ParseError: {e}")
            # explicitly set match result with None obj so it won't stuck in an infinite retry loop
            return ParameterMatch(
                name=param.name,
                # regex_substr=raw_param_substr,
                parsed_obj=None,
                parsed_substr="",
            )

        return ParameterMatch(
            name=param.name,
            # regex_substr=raw_param_substr,
            parsed_obj=parse_result.obj,
            parsed_substr=parse_result.substring,
        )
        # return None

    def _filter_overlapping_matches(self, matches: list[MatchResult]) -> list[MatchResult]:
        filtered = matches.copy()
        for prev, current in zip(
            filtered.copy(), filtered[1:]
        ):  # copy to prevent affecting iteration by removing items; slice makes copy automatically
            if prev.start == current.start or prev.end > current.start:  # if overlap
                filtered.remove(min(prev, current, key=lambda m: len(m.substring)))  # remove shorter
        return filtered

    def _compile_pattern(
        self,
        pattern: Pattern,
        group_prefix: str = "",
        prefill: dict[str, str] | None = None,
    ) -> str:  # transform Pattern to classic regex with named groups
        prefill = prefill or {}

        pattern_str: str = pattern._origin

        #   transform core expressions to regex

        for rule in rules_list:
            if rule.func:
                pattern_str = re.sub(rule.pattern, rule.func, pattern_str)
            elif rule.replace:
                pattern_str = re.sub(rule.pattern, rule.replace, pattern_str)
            else:
                raise RuntimeError(f"Invalid rule: {rule}")

        #   find and transform parameters like $name:Type

        for parameter in pattern.parameters.values():
            parameter_type = self.parameter_types_by_name[parameter.type_name].type

            arg_declaration = f"\\${parameter.name}\\:{parameter_type.__name__}"  # NOTE: special chars escaped for regex
            if parameter.name in prefill:
                arg_pattern = prefill[parameter.name]  # TODO: review wether re.escape is needed
            else:  # replace pattern annotation with compiled regex
                parameter.group_name = ((group_prefix + "_") if group_prefix else "") + parameter.name
                arg_pattern = self._compile_pattern(parameter_type.pattern, group_prefix=parameter.group_name).replace("\\", r"\\")

                if parameter_type.greedy and arg_pattern[-1] in {"*", "+", "}", "?"}:
                    # compensate greedy did_parse with non-greedy regex, so it won't consume next params during initial regex
                    arg_pattern += "?"
                    if pattern_str.endswith(f"${parameter.name}:{parameter_type.__name__}"):  # NOTE: regex chars are NOT escaped
                        # compensate the last non_greedy regex to allow consuming till the end of the string
                        # middle greedy params are limited/stretched by neighbor params
                        arg_pattern += "$"

            pattern_str = re.sub(
                arg_declaration,
                f"(?P<{parameter.group_name}>{arg_pattern})",
                pattern_str,
            )

        return pattern_str
