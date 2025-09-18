from abc import ABC
from typing import Union, get_args, get_origin

from .. import Pattern, PatternParameter
from .object import Object


class SlotsPattern(Pattern):

    def __init__(self, parameters: dict[str, PatternParameter]):
        super().__init__('**')
        self.parameters = parameters
        self._update_group_name_to_param()
        self.compiled = self.compile() # update group names of the parameters

class Slots(Object, ABC):

    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return SlotsPattern({
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
            for key, type_ in cls.__annotations__.items()
            if key != 'value'
        })
