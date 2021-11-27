from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from copy import copy

from ..Pattern import Pattern

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class ACObject(ABC):
    pattern: Pattern # static getonly
    stringValue: str
    value: Any
    formatted: str

    def __init__(self, value: Any):
        self.value = value

    @classmethod
    def parse(cls, fromString: str) -> ACObject:
        object = cls()
        object.stringValue = fromString
        return cls()

    def __repr__(self):
        return str(self.value)

    @classproperty
    def pattern() -> Pattern:
        return Pattern('*')

    def __lt__(self, other: ACObject) -> bool:
        return self.value < other.value

    def __le__(self, other: ACObject) -> bool:
        return self.value <= other.value

    def __gt__(self, other: ACObject) -> bool:
        return self.value > other.value

    def __ge__(self, other: ACObject) -> bool:
        return self.value >= other.value

    def __eq__(self, other: ACObject) -> bool:
        return self.value == other.value

    def __ne__(self, other: ACObject) -> bool:
        return self.value != other.value

    def __neg__(self) -> ACObject:
        return type(self).__init__(value = -self.value)

    def __abs__(self) -> ACObject:
        return type(self).__init__(value = abs(self.value))

    def __round__(self, n) -> ACObject:
        return type(self).__init__(value = round(self.value))

    def __floor__(self) -> ACObject:
        return type(self).__init__(value = floor(self.value))

    def __ceil__(self) -> ACObject:
        return type(self).__init__(value = ceil(self.value))

    def __trunc__(self) -> ACObject:
        return type(self).__init__(value = trunc(self.value))

    def __add__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value + other.value)

    def __sub__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value - other.value)

    def __mul__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value * other.value)

    def __floordiv__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value // other.value)

    def __div__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value / other.value)

    def __mod__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value % other.value)

    def __pow__(self, other: ACObject) -> ACObjet:
        return type(self).__init__(value = self.value ** other.value)
