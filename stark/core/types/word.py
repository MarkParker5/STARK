from .. import Pattern, rules
from .object import Object, classproperty


class Word(Object):

    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern(f'[{rules.alphanumerics}]+')
        # return Pattern('*')
