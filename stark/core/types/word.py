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
