# from __future__ import annotations
# from typing import Optional
# from datetime import datetime, timedelta

# from .object import Object, Pattern, classproperty
# from .time_interval import TimeInterval

# class Time(Object):
#     value: datetime

#     def __init__(self, value: Optional[datetime] = None):
#         self.value = value or datetime.now()

#     def addingInterval(self, timeinterval: Union[Object, Number]) -> Time:
#         seconds = timeinterval.value if isinstance(timeinterval, TimeInterval) else timeinterval
#         return Time(self.value + timedelta(seconds = seconds))

#     def addInterval(self, timeinterval: Union[Object, Number]):
#         seconds = timeinterval.value if isinstance(timeinterval, TimeInterval) else timeinterval
#         self.value += timedelta(seconds = seconds)

#     @classmethod
#     def parse(cls, fromString: str) -> Object:
#         raise NotImplementedError

#     @classproperty
#     def pattern() -> Pattern:
#         raise NotImplementedError

#     def __sub__(self, other: Time) -> TimeInterval:
#         return TimeInterval((self.value - other.value).total_seconds())
