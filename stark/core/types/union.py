from __future__ import annotations

from stark.core.patterns.pattern import Pattern
from stark.core.types.object import Object, UnionMeta
from stark.general.classproperty import classproperty


def MakeUnion(*types: type[Object]) -> type:
    cls = UnionMeta("_".join(t.__name__ for t in types), (Union,), {"_types": list(types)})
    cls._transparent = True  # PatternParser unwraps to branch when used as a typed parameter
    return cls


def any_subclass(cls: type[Object]) -> type[Union]:
    """Returns a Union of all current concrete subclasses of cls.

    Result is cached on the base class so the same class object is returned on every call —
    required for stable type registration (the parser keys on class name and object identity).
    Discovered at first call time, so subclasses defined before the pattern is first accessed
    (i.e., at parse time) are included automatically.
    """
    cache_attr = f"_any_subclass_{cls.__name__}"
    if not hasattr(cls, cache_attr):
        u = MakeUnion(*_all_subclasses(cls))
        u.__name__ = f"Any{cls.__name__}"  # no | — Pattern syntax treats | as OR
        setattr(cls, cache_attr, u)
    return getattr(cls, cache_attr)


def _all_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)


class Union(Object):
    """Base for union types. Use as superclass or combine with | / MakeUnion.

    self.value  — the matched branch Object instance
    self.value.value  — the inner parsed value
    type(self.value)  — the matched branch type

    After PatternParser unwraps Union parameters, callers receive the concrete branch
    directly — isinstance, type(), and attribute access all work against the real class.
    """

    _types: list[type[Object]]
    value: Object

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "pattern" in cls.__dict__ or "patterns" in cls.__dict__:
            raise TypeError(f"{cls.__name__}: Union subclasses may not override 'pattern'")

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern("(" + "|".join(f"$m{n}:{t.__name__}" for n, t in enumerate(cls._types, 1)) + ")")

    async def did_parse(self, from_string) -> str:
        from stark.core.parsing import ParseError
        for k, v in self.__dict__.items():
            if k.startswith("m") and v is not None:
                self.value = v  # branch Object, not v.value
                return from_string
        raise ParseError("Union: no branch matched")
