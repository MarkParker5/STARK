from __future__ import annotations
from typing import Union
from numbers import Number

from .VIObject import VIObject, Pattern, classproperty

class VITimeInterval(VIObject):
    value: float # seconds

    @classmethod
    def initWith(seconds: float = 0,
                 minutes: float = 0,
                 hours: float = 0,
                 days: float = 0,
                 weeks: float = 0) -> VITimeInterval:

        days += weeks * 7
        hours += days * 24
        minutes += hours * 60
        seconds += minutes * 60
        return VITimeInterval(value = seconds)

    @classmethod
    def parse(cls, fromString: str) -> VIObject:
        raise NotImplementedError

    @classproperty
    def pattern() -> Pattern:
        raise NotImplementedError

    def __lt__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value < value

    def __le__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value <= value

    def __gt__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value > value

    def __ge__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value >= value

    def __eq__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value == value

    def __ne__(self, other: VIObject) -> bool:
        value = other.value if isinstance(other, VITimeInterval) else other
        return self.value != value

    def __add__(self, other: Union[VIObject, Number]) -> VITimeInterval:
        value = other.value if isinstance(other, VITimeInterval) else other
        return VITimeInterval(self.value + value)

    def __sub__(self, other: Union[VIObject, Number]) -> VITimeInterval:
        value = other.value if isinstance(other, VITimeInterval) else other
        return VITimeInterval(self.value - value)

    def __mul__(self, other: Union[VIObject, Number]) -> VITimeInterval:
        value = other.value if isinstance(other, VITimeInterval) else other
        return VITimeInterval(self.value * value)

    def __mod__(self, other: Union[VIObject, Number]) -> VITimeInterval:
        value = other.value if isinstance(other, VITimeInterval) else other
        return VITimeInterval(self.value % value)

    def __floordiv__(self, other: Union[VIObject, Number]) -> Union[VIObject, Number]:
        return self.value // other.value if isinstance(other, VITimeInterval) else VITimeInterval(self.value // other)

    def __truediv__(self, other: Union[VIObject, Number]) -> Union[VIObject, Number]:
        return self.value / other.value if isinstance(other, VITimeInterval) else VITimeInterval(self.value / other)
