from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta

from .VIObject import VIObject, Pattern, classproperty
from .VITimeInterval import VITimeInterval

class VITime(VIObject):
    value: datetime

    def __init__(self, value: Optional[datetime] = None):
        self.value = value or datetime.now()

    def addingInterval(self, timeinterval: Union[VIObject, Number]) -> VITime:
        seconds = timeinterval.value if isinstance(timeinterval, VITimeInterval) else timeinterval
        return VITime(self.value + timedelta(seconds = seconds))

    def addInterval(self, timeinterval: Union[VIObject, Number]):
        seconds = timeinterval.value if isinstance(timeinterval, VITimeInterval) else timeinterval
        self.value += timedelta(seconds = seconds)

    @classmethod
    def parse(cls, fromString: str) -> VIObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError

    def __sub__(self, other: VITime) -> VITimeInterval:
        return VITimeInterval((self.value - other.value).total_seconds())
