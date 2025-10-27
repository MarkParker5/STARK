from __future__ import annotations

import copy
from abc import ABC
from typing import Any

from stark.general.classproperty import classproperty

from .. import Pattern


class Object[T](ABC):
    value: T

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    @classproperty
    def greedy(
        cls,
    ) -> bool:  # TODO: review possibility of making this object's property to be set dynamically in did_parse
        """
        Indicates `did_parse` returns real minimal substring and doesn't take any extra characters.
        Makes this object be parsed before greedy objects.
        """
        return False  # TODO: review default behavior

    def __init__(self, value: Any):
        """Just init with wrapped value."""
        self.value = value

    async def did_parse(self, from_string: str) -> str:
        """
        This method is called after parsing from string and setting parameters found in pattern.
        You will very rarely, if ever, need to call this method directly.

        Override this method for more complex parsing from string.

        If you need even more complex setup, for example, a long living object with DI, use define an ObjectParser subclass and pass it's instance to Pattern.add_parameter_type along with the Object's class. If both `did_parse` are defined, the ObjectParser's  will be called first.

        Returns:
            Minimal substring that is required to parse value.

        Raises:
            ParseError: if parsing failed.
        """
        return from_string

    def copy(self) -> Object:
        return copy.copy(self)

    def __format__(self, spec) -> str:
        return f"{self.value:{spec}}"

    def __repr__(self):
        strValue = (
            f'"{str(self.value)}"' if type(self.value) is str else str(self.value)
        )
        return f"<{type(self).__name__} value: {strValue}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            raise NotImplementedError(f"Cannot compare {type(self)} with {type(other)}")
        return self.value == other.value
