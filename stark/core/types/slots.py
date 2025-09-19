import logging
from abc import ABC
from typing import Union, get_args, get_origin

from stark.core.patterns.parsing import ParseError, parse_object
from stark.core.patterns.pattern import ParameterMatch

from .. import Pattern, PatternParameter
from .object import Object

logger = logging.getLogger(__name__)

# class SlotsPattern(Pattern):

#     def __init__(self, parameters: dict[str, PatternParameter]):
#         super().__init__('**')
#         self.parameters = parameters
#         self._update_group_name_to_param()
#         self.compiled = self.compile() # update group names of the parameters

#     async def _parse_parameters_for_match(self, command_str: str, match: re.Match, string: str, objects_cache: dict[str, Object]) -> dict[str, ParameterMatch]:
#         parsed_parameters: dict[str, ParameterMatch] = {}

#         while True:
#             # self._parse_single_parameter()
#             ...

#         return parsed_parameters

class Slots(Object, ABC):

    value: str

    at_least_one: bool = True
    all_required: bool = True

    # @classproperty
    # def pattern(cls) -> Pattern:
    #     return SlotsPattern({
    #         key: PatternParameter(
    #             name=key,
    #             group_name=key,
    #             type_name=(
    #                 get_args(type_)[0].__name__
    #                 if get_origin(type_) is Union and type(None) in get_args(type_)
    #                 else type_.__name__
    #             ),
    #             optional=(
    #                 get_origin(type_) is Union and type(None) in get_args(type_)
    #             )
    #         )
    #         for key, type_ in cls.__annotations__.items()
    #         if key != 'value'
    #     })

    async def did_parse(self, from_string: str) -> str:
        parsed_parameters: dict[str, ParameterMatch] = {}

        slots = {
            key: PatternParameter(
                name=key,
                group_name=key,
                type_name=(
                    get_args(type_)[0].__name__
                    if get_origin(type_) is Union and type(None) in get_args(type_)
                    else type_.__name__
                ),
                optional=(
                    get_origin(type_) is Union and type(None) in get_args(type_)
                )
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
            try:
                object_matches = await parameter_type.pattern.match(string)
                if not object_matches:
                    raise ParseError(f"Failed to match object {parameter_type} from {string}")
                object_pattern_match = object_matches[0]
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
            except ParseError as e:
                logger.error(f"Pattern.match ParseError: {e}")
                if param.optional:
                    parameter_match = ParameterMatch(
                        name=param.name,
                        regex_substr=string,
                        parsed_obj=None,
                        parsed_substr='',
                    )
                else:
                    raise

            if parameter_match is not None:
                parsed_parameters[param.name] = parameter_match
                start_index = min(start_index, from_string.index(parameter_match.parsed_substr))
                end_index = max(end_index, from_string.index(parameter_match.parsed_substr) + len(parameter_match.parsed_substr))
                string = string.replace(parameter_match.parsed_substr, '')

        parsed_keys = set(parsed_parameters.keys())
        all_keys = set(slots.keys())

        if self.at_least_one:
            assert len(parsed_parameters) >= 1, "At least one parameter must be matched"

        if self.all_required:
            assert parsed_keys == all_keys, "All required parameters must be matched"

        for name, value in parsed_parameters.items():
            setattr(self, name, value.parsed_obj)

        self.value = from_string = from_string[start_index:end_index]
        return from_string
