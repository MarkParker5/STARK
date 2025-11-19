from stark.core.command import Command
from stark.core.commands_context_processor import RecognizedEntity
from stark.core.patterns.parsing import ParameterMatch, PatternParser
from stark.core.patterns.pattern import Pattern, PatternParameter


async def get_preparsed_parameters(
    pattern_parser: PatternParser,
    string: str,
    recognized_entities: list[RecognizedEntity],
    command: Command,
) -> dict[str, ParameterMatch]:
    # put parsed types to corresponding parameter keys; TODO: check for nested same name, consider making group_prefix public or calcing it in the function, or even moving the func to the Pattern
    param_type_to_key = {
        p.type_name: p.name for p in _get_pattern_param_types_recursively(pattern_parser, command.pattern)
    }  # TODO: list for multiple parameters (with defaultdict) and check for len==1, otherwise just put to cache

    # parse all suitable recognized entities to save them to cache with a proper substring
    parsed = {
        param_type_to_key[entity.type.__name__]: ParameterMatch(
            name=param_type_to_key[entity.type.__name__],
            parsed_obj=parsed.obj,
            parsed_substr=string[entity.span.slice],
        )
        for entity in recognized_entities
        if (parsed := await pattern_parser.parse_object(entity.type, string[entity.span.slice]))
    }

    return {
        k: v for k, v in parsed.items() if len(param_type_to_key[k]) == 1
    }  # avoid returning false/swapped keys if same type appears multiple times; it will be resolved by the cache


def _get_pattern_param_types_recursively(pattern_parser: PatternParser, pattern: Pattern) -> list[PatternParameter]:
    return [param for param in pattern.parameters.values()] + [
        subparam
        for param in pattern.parameters.values()
        for subparam in _get_pattern_param_types_recursively(pattern_parser, pattern_parser.parameter_types_by_name[param.type_name].type.pattern)
    ]
