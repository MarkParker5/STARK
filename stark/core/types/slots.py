import logging
from abc import ABC
from typing import get_args

from stark.core.patterns.parsing import ParseError, parse_object
from stark.core.patterns.pattern import ParameterMatch

from .. import Pattern, PatternParameter
from .object import Object

logger = logging.getLogger(__name__)

class Slots(Object, ABC):

    value: str

    async def did_parse(self, from_string: str) -> str: # TODO: consider to override def parse instead (if present) to keep did_parse free?
        parsed_parameters: dict[str, ParameterMatch] = {}

        slots = {
            key: PatternParameter(
                name = key,
                group_name = key,
                type_name = (
                    get_args(type_)[0].__name__
                    if type(None) in get_args(type_)
                    else type_.__name__
                ),
                optional = type(None) in get_args(type_)
            )
            for key, type_ in type(self).__annotations__.items()
            if key not in {'value', 'at_least_one', 'all_required'}
        }

        string = from_string[:] # copy
        start_index = len(string)
        end_index = 0

        for param in slots.values():
            parameter_reg_type = Pattern._parameter_types[param.type_name]
            parameter_type = parameter_reg_type.type
            object_matches = await parameter_type.pattern.match(string)
            for object_pattern_match in object_matches:
                try:
                    parse_result = await parse_object(
                        parameter_reg_type.type,
                        parameter_reg_type.parser,
                        from_string=object_pattern_match.substring,
                        parsed_parameters=object_pattern_match.parameters
                    )
                    parameter_match = ParameterMatch(
                        name=param.name,
                        regex_substr=string,
                        parsed_obj=parse_result.obj,
                        parsed_substr=parse_result.substring,
                    )
                    break
                except ParseError as e:
                    # partial backtracking
                    # If the "best" assignment of words to slots requires skipping a candidate for slot 1 in favor of a better overall fit for all slots, this approach won't find it. (Full backtracking over all slot assignments would be needed for that.)
                    logger.debug(f"Slot parameter match ParseError: {e}; trying next match...")
            else:
                if param.optional:
                    logger.debug(f"Failed to match optional slot parameter {param.name} from {string}")
                    parameter_match = ParameterMatch(
                        name=param.name,
                        regex_substr=string,
                        parsed_obj=None,
                        parsed_substr='',
                    )
                else:
                    msg = f"Failed to match required slot parameter {parameter_type} from {string}"
                    logger.debug(msg)
                    raise ParseError(msg)

            parsed_parameters[param.name] = parameter_match
            if parameter_match.parsed_substr:
                start_index = min(start_index, from_string.index(parameter_match.parsed_substr))
                end_index = max(end_index, from_string.index(parameter_match.parsed_substr) + len(parameter_match.parsed_substr))
                string = string.replace(parameter_match.parsed_substr, '')

        if len(list(p for p in parsed_parameters.values() if p.parsed_obj is not None)) < 1:
            raise ParseError(f"{type(self)} At least one parameter must be matched, can't find any of {slots.keys()} in '{from_string}'")

        for name, value in parsed_parameters.items():
            setattr(self, name, value.parsed_obj)

        self.value = from_string = from_string[start_index:end_index]
        return from_string
