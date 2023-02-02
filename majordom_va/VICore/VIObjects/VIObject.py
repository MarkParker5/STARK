from __future__ import annotations

from abc import ABC
from typing import Any

from .. import Pattern


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class VIObject(ABC):

    value: Any

    def __init__(self, value: Any):
        self.value = value

    @classmethod
    def parse(cls, fromString: str) -> VIObject:
        object = cls()
        object.value = fromString
        return object

    @classproperty
    def pattern(cls) -> Pattern:
        return Pattern('**')
    
    @property
    def formatted(self) -> Pattern:
        return self.value

    def __repr__(self):
        strValue = f'"{str(self.value)}"' if type(self.value) == str else str(self.value)
        return f'<{type(self).__name__} value:{strValue}>'

    def __lt__(self, other: VIObject) -> bool:
        return self.value < other.value

    def __le__(self, other: VIObject) -> bool:
        return self.value <= other.value

    def __gt__(self, other: VIObject) -> bool:
        return self.value > other.value

    def __ge__(self, other: VIObject) -> bool:
        return self.value >= other.value

    def __eq__(self, other: VIObject) -> bool:
        return self.value == other.value

    def __ne__(self, other: VIObject) -> bool:
        return self.value != other.value

    def __neg__(self) -> VIObject:
        return type(self).__init__(value = -self.value)

    def __abs__(self) -> VIObject:
        return type(self).__init__(value = abs(self.value))

    def __round__(self, n) -> VIObject:
        return type(self).__init__(value = round(self.value))

    def __floor__(self) -> VIObject:
        return type(self).__init__(value = floor(self.value))

    def __ceil__(self) -> VIObject:
        return type(self).__init__(value = ceil(self.value))

    def __trunc__(self) -> VIObject:
        return type(self).__init__(value = trunc(self.value))

    def __add__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value + other.value)

    def __sub__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value - other.value)

    def __mul__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value * other.value)

    def __floordiv__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value // other.value)

    def __truediv__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value / other.value)

    def __mod__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value % other.value)

    def __pow__(self, other: VIObject) -> VIObject:
        return type(self).__init__(value = self.value ** other.value)
