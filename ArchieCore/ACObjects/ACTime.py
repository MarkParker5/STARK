from __future__ import annotations
from typing import Optional
from datetime import datetime, timedelta
from .ACObject import ACObject, Pattern, classproperty
from . import ACTimeInterval

class ACTime(ACObject):
    value: datetime

    def __init__(self, value: Optional[datetime] = None):
        self.value = value or datetime.now()

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
