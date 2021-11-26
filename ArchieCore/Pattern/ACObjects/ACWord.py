from .ACObject import ACString, Pattern

class ACWord(ACString):

    @classproperty
    def pattern() -> Pattern:
        return Pattern('[:word:]')
