from stark.core.patterns import Pattern, rules

from .object import Object, classproperty


class Word(Object):
    """
    Any single alphanumerics word; separated by spaces, punctuation, other non-alphanumeric characters, or string boundaries.
    """

    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern(f"[{rules.alphanumerics}]+")
        # return Pattern('*')
