from .VIObject import VIObject, Pattern, classproperty

class VIString(VIObject):
    value: str

    def __init__(self, value: str):
        self.value = value

    @classmethod
    def parse(cls, fromString: str):
        acString = cls(value = string)
        acString.stringValue = string
        return acString

    @classproperty
    def pattern() -> Pattern:
        return Pattern('*')
