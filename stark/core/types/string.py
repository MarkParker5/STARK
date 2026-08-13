from .object import NLObject


class NLString(NLObject):
    """
    Space separated alphanumerics words.
    """

    value: str


def __getattr__(name):
    # Deprecated alias — String was renamed to NLString.
    if name == "String":
        import warnings

        warnings.warn(
            f"'{__name__}.{name}' is deprecated; use 'NLString' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return NLString
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
