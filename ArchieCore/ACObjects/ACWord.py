from .ACObject import Pattern, classproperty
from . import ACString

class ACWord(ACString):

    @classproperty
    def pattern() -> Pattern:
        return Pattern('[:word:]')
