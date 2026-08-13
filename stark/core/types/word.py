from stark.core.patterns import Pattern, rules

from .object import NLObject, classproperty


class NLWord(NLObject):
    """
    Any single alphanumerics word; separated by spaces, punctuation, other non-alphanumeric characters, or string boundaries.
    """

    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern(f"[{rules.alphanumerics}]+")
        # return Pattern('*')


def __getattr__(name):
    # Deprecated alias — Word was renamed to NLWord.
    if name == "Word":
        import warnings

        warnings.warn(
            f"'{__name__}.{name}' is deprecated; use 'NLWord' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return NLWord
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
