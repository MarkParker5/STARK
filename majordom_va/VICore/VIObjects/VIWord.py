from .VIObject import Pattern, classproperty
from . import VIString

class VIWord(VIString):

    @classproperty
    def pattern() -> Pattern:
        return Pattern('[:word:]')
