from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta

from .ACObject import ACObject, Pattern, classproperty
from .ACTimeInterval import ACTimeInterval

class ACTime(ACObject):
    value: datetime

    def __init__(self, value: Optional[datetime] = None):
        self.value = value or datetime.now()

    def addingInterval(self, timeinterval: Union[ACObject, Number]) -> ACTime:
        seconds = timeinterval.value if isinstance(timeinterval, ACTimeInterval) else timeinterval
        return ACTime(self.value + timedelta(seconds = seconds))

    def addInterval(self, timeinterval: Union[ACObject, Number]):
        seconds = timeinterval.value if isinstance(timeinterval, ACTimeInterval) else timeinterval
        self.value += timedelta(seconds = seconds)

    @classmethod
    def parse(cls, fromString: str) -> ACObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError

    def __sub__(self, other: ACTime) -> ACTimeInterval:
        return ACTimeInterval((self.value - other.value).seconds)
