import logging
from typing import TYPE_CHECKING, get_args

from stark.core.parsing import ObjectParser, ParameterMatch, ParseError

from ..patterns import PatternParameter
from .object import Object

if TYPE_CHECKING:
    from ..parsing import PatternParser

logger = logging.getLogger(__name__)


class SlotsParser(ObjectParser):
    def __init__(self, pattern_parser: "PatternParser"):
        self.pattern_parser = pattern_parser

    async def did_parse(self, obj: Object, from_string: str) -> str:
        parsed_parameters: dict[str, ParameterMatch] = {}

        slots = {
            key: PatternParameter(
                name=key,
                group_name=key,
                type_name=(get_args(type_)[0].__name__ if type(None) in get_args(type_) else type_.__name__),
                optional=type(None) in get_args(type_),
            )
            for key, type_ in type(obj).__annotations__.items()
            if key not in {"value", "at_least_one", "all_required"}
        }

        string = from_string[:]  # copy
        start_index = len(string)
        end_index = 0

        for param in slots.values():
            parameter_reg_type = self.pattern_parser.parameter_types_by_name[param.type_name]
            parameter_type = parameter_reg_type.type
            try:
                parse_result = await self.pattern_parser.parse_object(parameter_type, from_string=string)
                parameter_match = ParameterMatch(
                    name=param.name,
                    parsed_obj=parse_result.obj,
                    parsed_substr=parse_result.substring,
                )
                # If the "best" assignment of words to slots requires skipping a candidate for slot 1 in favor of a better overall fit for all slots, this approach won't find it. (Full backtracking over all slot assignments would be needed for that.)
            except ParseError as e:
                if param.optional:
                    logger.debug(f"Failed to match optional slot parameter {param.name} from {string}")
                    parameter_match = ParameterMatch(
                        name=param.name,
                        parsed_obj=None,
                        parsed_substr="",
                    )
                else:
                    msg = f"Failed to match required slot parameter {parameter_type} from {string}; {e}"
                    logger.debug(msg)
                    raise ParseError(msg) from e

            parsed_parameters[param.name] = parameter_match
            if parameter_match.parsed_substr:
                start_index = min(start_index, from_string.index(parameter_match.parsed_substr))
                end_index = max(
                    end_index,
                    from_string.index(parameter_match.parsed_substr) + len(parameter_match.parsed_substr),
                )
                string = string.replace(parameter_match.parsed_substr, "")

        if len([p for p in parsed_parameters.values() if p.parsed_obj is not None]) < 1:
            raise ParseError(f"{type(obj)} At least one parameter must be matched, can't find any of {slots.keys()} in '{from_string}'")

        for name, value in parsed_parameters.items():
            setattr(obj, name, value.parsed_obj)

        obj.value = from_string = from_string[start_index:end_index]
        return from_string
