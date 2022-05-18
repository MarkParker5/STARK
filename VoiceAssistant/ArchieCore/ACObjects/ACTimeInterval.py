from __future__ import annotations
from typing import Union
from numbers import Number

from .ACObject import ACObject, Pattern, classproperty

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
        return ACTimeInterval(value = seconds)

    @classmethod
    def parse(cls, fromString: str) -> ACObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError

    def __lt__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value < value

    def __le__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value <= value

    def __gt__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value > value

    def __ge__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value >= value

    def __eq__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value == value

    def __ne__(self, other: ACObject) -> bool:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return self.value != value

    def __add__(self, other: Union[ACObject, Number]) -> ACTimeInterval:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return ACTimeInterval(self.value + value)

    def __sub__(self, other: Union[ACObject, Number]) -> ACTimeInterval:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return ACTimeInterval(self.value - value)

    def __mul__(self, other: Union[ACObject, Number]) -> ACTimeInterval:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return ACTimeInterval(self.value * value)

    def __mod__(self, other: Union[ACObject, Number]) -> ACTimeInterval:
        value = other.value if isinstance(other, ACTimeInterval) else other
        return ACTimeInterval(self.value % value)

    def __floordiv__(self, other: Union[ACObject, Number]) -> Union[ACObject, Number]:
        return self.value // other.value if isinstance(other, ACTimeInterval) else ACTimeInterval(self.value // other)

    def __truediv__(self, other: Union[ACObject, Number]) -> Union[ACObject, Number]:
        return self.value / other.value if isinstance(other, ACTimeInterval) else ACTimeInterval(self.value / other)
