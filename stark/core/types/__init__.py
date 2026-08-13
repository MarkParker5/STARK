from .object import NLObject
from .slots import SlotsParser
from .string import NLString
from .union import MakeUnion, Union, any_subclass
from .word import NLWord

# from .Number import Number
# from .TimeInterval import TimeInterval
# from .Time import Time

# Deprecated aliases — the base type and native types were renamed to the NL* family
# (NLObject/NLWord/NLString). Old names keep working for a release; using them warns.
_DEPRECATED_ALIASES = {"Object": NLObject, "Word": NLWord, "String": NLString}


def __getattr__(name):
    new = _DEPRECATED_ALIASES.get(name)
    if new is not None:
        import warnings

        warnings.warn(
            f"'stark.core.types.{name}' is deprecated; use '{new.__name__}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return new
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
