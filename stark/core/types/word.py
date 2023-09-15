from .object import Object, Pattern, classproperty


class Word(Object):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('*')
