from datetime import datetime, timedelta
from .ACObject import ACObject, Pattern

class ACTime(ACObject):
    value: datetime

    def __init__(self, value: time = datetime.now()):
        self.value = value

    def addingInterval(self, timeinterval: ACTimeInterval) -> ACTime:
        return ACTime(self.value + timedelta(seconds = timeinterval.value))

    def addInterval(self, timeinterval: ACTimeInterval):
        self.value += timedelta(seconds = timeinterval.value)

    @classmethod
    def parse(cls, fromString: str) -> ACObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError
