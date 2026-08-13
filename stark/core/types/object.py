from __future__ import annotations

import copy
from abc import ABCMeta
from typing import Any, cast

from stark.core.patterns.pattern import Pattern
from stark.general.classproperty import classproperty
from stark.general.localisation import LocaleString


class UnionMeta(ABCMeta):
    """Metaclass that makes | on NLObject subclasses produce a STARK Union subclass instead of types.UnionType."""

    # Class-level flag on Union subclasses; synthetic MakeUnion classes set it True so PatternParser unwraps them.
    _transparent: bool = False

    def __call__(cls, *args, **kwargs):
        from stark.core.types.union import Union

        if cls is Union:
            raise TypeError("Union cannot be instantiated directly; subclass it or use | syntax or  MakeUnion")
        return super().__call__(*args, **kwargs)

    def __or__(cls, other: type) -> type:  # type: ignore[override]  # metaclass operator overload returning STARK Union
        from stark.core.types.union import MakeUnion

        if isinstance(other, type) and issubclass(other, NLObject):
            return MakeUnion(cls, other)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]  # UnionMeta instances are NLObject subclasses
        return type.__or__(cls, other)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]  # fall through to types.UnionType for X | None etc.

    def __ror__(cls, other: type) -> type:  # type: ignore[override]  # metaclass operator overload returning STARK Union
        from stark.core.types.union import MakeUnion

        if isinstance(other, type) and issubclass(other, NLObject):
            return MakeUnion(other, cls)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]  # UnionMeta instances are NLObject subclasses
        return type.__ror__(cls, other)  # type: ignore[return-value]  # ty: ignore[invalid-return-type]  # fall through to types.UnionType for X | None etc.

    def __format__(cls, spec) -> str:
        return cls.__name__


# TODO: review programmable init vs did_parse
# TODO: consider storing parsing metadata here like substr and span
class NLObject[T](metaclass=UnionMeta):
    value: T = cast(T, None)

    def __init__(self, value: Any = None):
        """Just init with a wrapped value."""
        self.value = value

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("**")

    @classproperty
    def patterns(cls) -> dict[str, Pattern]:
        return {"base": cls.pattern}

    @classproperty
    def greedy(
        cls,
    ) -> bool:  # TODO: review possibility of making this object's property to be set dynamically in did_parse
        """
        Indicates `did_parse` returns real minimal substring and doesn't take any extra characters.
        Makes this object be parsed before greedy objects.
        """
        return False  # TODO: review default behavior

    def __init__(self, *args, **kwargs):  # type: ignore[no-redef]  # noqa: F811  # intentional override of the documented single-value __init__ above
        """Init with wrapped value, if provided. Otherwise leave `value` untouched so a static
        value set at class declaration time (e.g. `value = "foo"`) survives instantiation."""
        if "value" in kwargs:
            self.value = kwargs["value"]
        elif args:
            self.value = args[0]

    async def did_parse(self, from_string: LocaleString) -> str:
        """
        This method is called after parsing from string and setting parameters found in pattern.
        You will very rarely, if ever, need to call this method directly.
        If you want to parse string to an object, use `parse_object` method of the `PatternParser` instance.

        Override this method for more complex parsing from string.

        If you need even more complex setup, for example, a long living object with DI, use define an ObjectParser subclass and pass it's instance to Pattern.add_parameter_type along with the NLObject's class. If both `did_parse` are defined, the ObjectParser's  will be called first.

        Returns:
            Minimal substring that is required to parse value.

        Raises:
            ParseError: if parsing failed.
        """
        if not self.value:
            self.value = cast(T, from_string)
        return from_string

    def copy(self) -> NLObject:
        return copy.copy(self)

    def __format__(self, spec) -> str:
        return f"{self.value:{spec}}"

    def __repr__(self):
        strValue = f'"{self.value!s}"' if isinstance(self.value, str) else str(self.value)
        return f"<{type(self).__name__} value: {strValue}>"

    def __eq__(self, other: object) -> bool:
        if other is None:
            return self.value is None
        if not isinstance(other, type(self)):
            raise NotImplementedError(f"Cannot compare {type(self)} with {type(other)}")
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


def __getattr__(name):
    # Deprecated alias — Object was renamed to NLObject.
    if name == "Object":
        import warnings

        warnings.warn(
            f"'{__name__}.{name}' is deprecated; use 'NLObject' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return NLObject
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
