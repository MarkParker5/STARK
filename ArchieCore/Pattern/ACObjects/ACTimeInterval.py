from .ACObject import ACObject, Pattern

class ACTimeInterval(ACObject):
    value: float # seconds

    @classmethod
    def initWith(seconds: float = 0,
                 minutes: float = 0,
                 hours: float = 0,
                 days: float = 0,
                 weeks: float = 0) -> ACTimeInterval:

    days += weeks * 7
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60
    return ACTimeInterval(value: seconds)

    @classmethod
    def parse(cls, fromString: str) -> ACObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError
