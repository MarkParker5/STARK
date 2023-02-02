from .VIObject import Pattern, classproperty
from . import VIString

class VIWord(VIString):

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('*')
