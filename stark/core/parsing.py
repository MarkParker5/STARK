from __future__ import annotations

import re
from abc import ABC
from dataclasses import dataclass, field
from typing import AsyncGenerator, NamedTuple

from stark.core.patterns.pattern import Pattern
from stark.core.patterns.rules import rules_list
from stark.core.types import Object
from stark.core.types.string import String
from stark.core.types.union import Union, _all_subclasses
from stark.core.types.word import Word
from stark.general.cache import alru_cache
from stark.general.localisation import LanguageCode, LocaleString, Localizer
from stark.models.transcription_string import Correction
from stark.tools.common.span import Span


class CorrectionMatch(NamedTuple):
    span: Span
    correction: Correction


type ObjectType = type[Object]


import logging

logger = logging.getLogger(__name__)

_LOCALIZER_KEY_REGEX = re.compile(r"@(?P<key>[A-Za-z_][A-Za-z0-9_]*)")


class ParseError(Exception):
    pass


@dataclass
class ParseResult:
    obj: Object
    substring: str


@dataclass
class RegisteredParameterType:
    name: str
    type: ObjectType
    parser: ObjectParser


@dataclass
class MatchResult:
    substring: str
    start: int
    end: int
    parameters: dict[str, Object | None]  # TODO: use ParameterMatch?
    corrections: list[CorrectionMatch] = field(default_factory=list)
    corrected_string: str = ""


@dataclass
class ParameterMatch:
    name: str
    parsed_obj: Object | None
    parsed_substr: str
    # TODO: add and use start and/end span to resolve duplication


@dataclass
class RecognizedEntity:
    # span: Span
    substring: str
    type: ObjectType
    key: str | None = None


class ObjectParser(ABC):
    localizer: Localizer | None = None

    @property
    def patterns(self) -> dict[str, Pattern] | None:
        return None

    async def did_parse(self, obj: Object, from_string: LocaleString) -> str:
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
    localizer: Localizer | None

    def __init__(self, localizer: Localizer | None = None):
        self.parameter_types_by_name = {}
        self._registering: set[str] = set()  # cycle guard for recursive register_parameter_type
        self.localizer = localizer
        self.register_parameter_type(Word)
        self.register_parameter_type(String)

    def register_parameter_type(
        self,
        object_type: ObjectType,
        parser: ObjectParser | None = None,
        # TODO: consider adding lang parameter
    ):
        name = object_type.__name__
        # Idempotent: skip if already registered or currently being registered (cycle guard).
        if name in self.parameter_types_by_name or name in self._registering:
            return
        self._registering.add(name)
        try:
            assert issubclass(object_type, Object), f'Can`t add parameter type "{name}": it is not a subclass of Object'
            # Resolve deps. Union types declare members explicitly in _types;
            # everything else declares deps implicitly via parameter annotations in the pattern.
            if issubclass(object_type, Union) and hasattr(object_type, "_types"):
                deps = object_type._types
            else:
                # Evaluate the pattern first — it may create new classes (e.g. any_subclass calls).
                # Build known AFTER so those new classes are visible by name.
                pattern = object_type.pattern
                known = {cls.__name__: cls for cls in _all_subclasses(Object)}
                deps = [known[p.type_name] for p in pattern.parameters.values() if p.type_name in known]
            # Register each dep before the type itself (depth-first, handles transitive deps).
            for dep in deps:
                self.register_parameter_type(dep)
            exists_type = self.parameter_types_by_name.get(name)
            assert exists_type is None, (
                f"Duplicate parameter type: can`t add parameter type '{name}' because it already exists"
            )
            resolved_parser = parser or ObjectParser()
            resolved_parser.localizer = self.localizer
            self.parameter_types_by_name[name] = RegisteredParameterType(
                name=name, type=object_type, parser=resolved_parser
            )
            self._validate_localizer_keys(object_type)
        finally:
            self._registering.discard(name)

    def _validate_localizer_keys(self, object_type: ObjectType):
        for pattern in object_type.patterns.values():
            keys = _LOCALIZER_KEY_REGEX.findall(pattern._origin)
            if not keys:
                continue
            if not self.localizer:
                raise ValueError(
                    f"Pattern '{pattern._origin}' of type '{object_type.__name__}' contains @key references but no Localizer is configured on PatternParser"
                )
            for key in keys:
                self.localizer.verify_recognizable(key)

    @staticmethod
    def _has_localizer_keys(pattern: Pattern) -> bool:
        return bool(_LOCALIZER_KEY_REGEX.search(pattern._origin))

    async def parse_object_name(self, class_name: str, from_string: str | LocaleString) -> ParseResult:
        return await self.parse_object(self.parameter_types_by_name[class_name].type, from_string)

    async def parse_object(self, object_type: ObjectType, from_string: str | LocaleString) -> ParseResult:
        async for obj in self.parse_objects(object_type, from_string):
            return obj  # take the first successful parsed result, usually the only one
        else:
            raise ParseError(f"Failed to parse object of type {object_type.__name__} from string '{from_string}'")

    def _resolve_pattern(self, object_type: ObjectType, language_code: LanguageCode) -> Pattern:
        parser = self.parameter_types_by_name[object_type.__name__].parser
        patterns = parser.patterns or object_type.patterns
        if language_code in patterns:
            return patterns[language_code]
        return patterns["base"]

    async def parse_objects(
        self, object_type: ObjectType, from_string: str | LocaleString
    ) -> AsyncGenerator[ParseResult]:
        from_string = from_string if isinstance(from_string, LocaleString) else LocaleString(from_string)
        language_code = from_string.language_code
        pattern = self._resolve_pattern(object_type, language_code)
        object_matches = await self.match(pattern, from_string)

        for object_pattern_match in object_matches:
            string = from_string._with(object_pattern_match.substring)  # TODO: review _with usage

            parser: ObjectParser = self.parameter_types_by_name[object_type.__name__].parser
            obj = object_type(string)  # temp/default value, may be overridden by did_parse

            matched_subparams = object_pattern_match.parameters
            assert matched_subparams.keys() <= {p.name for p in pattern.parameters.values() if not p.optional}

            for name in pattern.parameters:
                value = matched_subparams[name]
                setattr(obj, name, value)

            try:
                substring = await self._did_parse(obj, parser, string)
            except ParseError:
                logger.debug(f"Failed to parse object {object_type!r} with parser {parser!r} from '{string}'")
                continue  # skip an try the next match candidate

            assert substring.strip(), ValueError(
                f"Parsed substring must not be empty. Object: {obj!r}, Parser: {parser!r}"
            )
            assert substring in string, ValueError(
                f"Parsed substring must be a part of the original string. There is no '{substring}' in '{string}'. Object: {obj!r}, Parser: {parser!r}"
            )
            assert obj.value is not None, ValueError(
                f"Parsed object {obj!r} must have a `value` property set in did_parse method. Object: {obj!r}, Parser: {parser!r}"
            )

            yield ParseResult(obj, substring)

    @alru_cache(maxsize=256, ttl=60 * 10)  # TODO: env vars + disable option
    async def _did_parse(self, obj: Object, parser: ObjectParser, string: LocaleString) -> str:
        substring = await parser.did_parse(obj, string)
        substring = string._with(substring) if not isinstance(substring, LocaleString) else substring
        substring = await obj.did_parse(substring)
        return substring

    async def match(
        self,
        pattern: Pattern,
        string: str | LocaleString,
        recognized_entities: list[RecognizedEntity] | None = None,
    ) -> list[MatchResult]:
        string = string if isinstance(string, LocaleString) else LocaleString(string)
        language_code = string.language_code
        recognized_entities = recognized_entities or []
        compiled = self._compile_pattern(pattern, language_code=language_code)

        compiled, correction_groups = self._expand_corrections(compiled, string)

        logger.debug(f'Starting looking for "{pattern=}" "{compiled=}" in "{string}"')

        matches = []
        initial_matches = self._find_initial_matches(compiled, string)
        for match in initial_matches:
            if match.start() == -1 or match.start() == match.end():
                continue  # skip empty

            new_match = None
            command_substr = string[match.start() : match.end()]
            new_match, parsed_parameters = await self._parse_parameters_for_match(
                pattern, command_substr, recognized_entities, language_code
            )
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

            # Backtrack corrections via named groups
            match_corrections: list[CorrectionMatch] = []
            for group_name, keyword in correction_groups.items():
                if group_name not in match.groupdict():
                    continue
                captured = match.group(group_name)
                if captured and captured != keyword:
                    span = Span(match.start(group_name) - start, match.end(group_name) - start)
                    match_corrections.append(CorrectionMatch(span, Correction(captured, keyword)))

            # Reconstruct corrected string by applying replacements right-to-left
            corrected = str(command_str)
            for cm in sorted(match_corrections, key=lambda cm: cm.span.start, reverse=True):
                corrected = corrected[: cm.span.start] + cm.correction.keyword + corrected[cm.span.end :]

            matches.append(
                MatchResult(
                    substring=command_str,
                    start=start,
                    end=end,
                    parameters={
                        name: (parameter.parsed_obj if parameter else None)
                        for name, parameter in all_parameters.items()
                    },
                    corrections=match_corrections,
                    corrected_string=corrected,
                )
            )
            logger.debug(f"Match result: {matches[-1]}")

        matches = self._filter_overlapping_matches(matches)
        return sorted(matches, key=lambda m: len(m.substring), reverse=True)

    def _expand_corrections(self, compiled: str, string: LocaleString) -> tuple[str, dict[str, str]]:
        """Inject corrections into compiled regex as named groups.

        Returns (expanded_regex, group_to_keyword_map) where group_to_keyword_map
        maps named group names to their correction keywords for back-tracking.
        """
        from stark.models.transcription_string import TranscriptionString

        empty_map: dict[str, str] = {}
        if not isinstance(string, TranscriptionString):
            return compiled, empty_map

        all_corrections = list(string.corrections)
        for track_corrections in string._corrections_by_track.values():
            all_corrections.extend(track_corrections)

        if not all_corrections:
            return compiled, empty_map

        grouped: dict[str, set[str]] = {}
        for c in all_corrections:
            grouped.setdefault(c.keyword, set()).add(c.variant)

        # each occurrence of a keyword gets a unique named group because re module
        # doesn't allow duplicate group names
        # (the third-party `regex` module does via DUPNAMES, but some bechmarks show it's ~2x slower — not worth swapping for the hot path)
        # TODO: review regex vs re for STARK again later
        group_map: dict[str, str] = {}
        for keyword, variants in grouped.items():
            alternatives = "|".join([re.escape(v) for v in variants])
            result_parts: list[str] = []
            remaining = compiled
            found = False
            while keyword in remaining:
                idx = remaining.index(keyword)
                group_name = f"_corr{len(group_map)}"
                group_map[group_name] = keyword
                replacement = f"(?P<{group_name}>{re.escape(keyword)}|{alternatives})"
                result_parts.append(remaining[:idx])
                result_parts.append(replacement)
                remaining = remaining[idx + len(keyword) :]
                found = True
            if found:
                result_parts.append(remaining)
                compiled = "".join(result_parts)
        return compiled, group_map

    def _find_initial_matches(self, compiled: str, string: str) -> list[re.Match]:
        return sorted(re.finditer(compiled, string), key=lambda match: match.start())

    async def _parse_parameters_for_match(
        self,
        pattern: Pattern,
        string: LocaleString,
        recognized_entities: list[RecognizedEntity],
        language_code: LanguageCode,
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
            compiled = self._compile_pattern(pattern, prefill=prefill, language_code=language_code)
            compiled, _ = self._expand_corrections(compiled, string)
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
                pattern,
                parameter_name,
                string._with(match_str_groups[parameter_name].strip()),
                recognized_entities,
            )
            if parameter_match is not None:
                parsed_parameters[parameter_name] = parameter_match

        return new_match, parsed_parameters

    async def _parse_single_parameter(
        self,
        pattern: Pattern,
        parameter_name: str,
        raw_param_substr: LocaleString,
        recognized_entities: list[RecognizedEntity],
    ) -> ParameterMatch | None:
        param = pattern.group_name_to_param[parameter_name]
        parameter_reg_type = self.parameter_types_by_name[param.type_name]

        logger.debug(f'Parsing parameter "{parameter_name}" from "{raw_param_substr}"')

        # check recognized entities, update substring if found match
        for entity in recognized_entities:
            if entity.substring in raw_param_substr and entity.type is parameter_reg_type.type:
                raw_param_substr = raw_param_substr._with(entity.substring)
                logger.debug(f"Adjusting for recognized entity: '{entity.substring}'")

        # parse the object
        try:
            from stark.core.types.union import Union

            parse_result = await self.parse_object(parameter_reg_type.type, from_string=raw_param_substr)
            parsed_obj = parse_result.obj
            if isinstance(parsed_obj, Union) and getattr(type(parsed_obj), "_transparent", False):
                # Transparent Unions (MakeUnion / | / any_subclass) are unwrapped to the branch.
                # Named Union subclasses (class Foo(Union)) are kept as-is — caller uses .value.
                parsed_obj = parsed_obj.value
            return ParameterMatch(  # take the first match (the only in most cases)
                name=param.name,
                parsed_obj=parsed_obj,
                parsed_substr=parse_result.substring,
            )
        except ParseError as e:
            logger.debug(f"Pattern.match ParseError: {e}")
            # None found, explicitly set match result to None so it won't stuck in an infinite retry loop
            return ParameterMatch(
                name=param.name,
                parsed_obj=None,
                parsed_substr="",
            )

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
        language_code: LanguageCode = "base",
    ) -> str:  # transform Pattern to classic regex with named groups
        prefill = prefill or {}

        pattern_str: str = pattern._origin

        if self._has_localizer_keys(pattern):
            if not self.localizer:
                raise ValueError(
                    f"Pattern '{pattern._origin}' contains @key references but no Localizer is configured on PatternParser"
                )

            def _resolve_key(m: re.Match) -> str:
                key = m.group("key")
                resolved = self.localizer.get_recognizable(key, language_code)
                if resolved is None:
                    raise KeyError(f"Localizer key '@{key}' not found for language '{language_code}'")
                return resolved

            pattern_str = _LOCALIZER_KEY_REGEX.sub(_resolve_key, pattern_str)

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

            arg_declaration = (
                f"\\${parameter.name}\\:{parameter_type.__name__}"  # NOTE: special chars escaped for regex
            )
            if parameter.name in prefill:
                arg_pattern = prefill[parameter.name]  # TODO: review wether re.escape is needed
            else:  # replace pattern annotation with compiled regex
                parameter.group_name = ((group_prefix + "_") if group_prefix else "") + parameter.name
                param_pattern = self._resolve_pattern(parameter_type, language_code)
                arg_pattern = self._compile_pattern(
                    param_pattern, group_prefix=parameter.group_name, language_code=language_code
                ).replace("\\", r"\\")

                if parameter_type.greedy and arg_pattern[-1] in {"*", "+", "}", "?"}:
                    # compensate greedy did_parse with non-greedy regex, so it won't consume next params during initial regex
                    arg_pattern += "?"
                    if pattern_str.endswith(
                        f"${parameter.name}:{parameter_type.__name__}"
                    ):  # NOTE: regex chars are NOT escaped
                        # compensate the last non_greedy regex to allow consuming till the end of the string
                        # middle greedy params are limited/stretched by neighbor params
                        arg_pattern += "$"

            pattern_str = re.sub(
                arg_declaration,
                f"(?P<{parameter.group_name}>{arg_pattern})",
                pattern_str,
            )

        return pattern_str
