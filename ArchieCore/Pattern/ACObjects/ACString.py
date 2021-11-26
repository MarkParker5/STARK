from .ACObject import ACObject, Pattern

class ACString(ACObject):
    value: str

    def __init__(self, value: str):
        self.value = string

    @classmethod
    def parse(class, fromString: str):
        acString = ACString(value: string)
        acString.stringValue = string
        return acString

    @classproperty
    def pattern() -> Pattern:
        return Pattern('*')
