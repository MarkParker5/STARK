from .VIObject import VIObject, Pattern, classproperty


class VIWord(VIObject):
    value: str

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('*')
