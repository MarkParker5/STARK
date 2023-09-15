# from __future__ import annotations
# from typing import Union
# from numbers import Number

# from .object import Object, Pattern, classproperty

# class TimeInterval(Object):
#     value: float # seconds

#     @classmethod
#     def initWith(
#         cls,
#         seconds: float = 0,
#         minutes: float = 0,
#         hours: float = 0,
#         days: float = 0,
#         weeks: float = 0
#     ) -> TimeInterval:

#         days += weeks * 7
#         hours += days * 24
#         minutes += hours * 60
#         seconds += minutes * 60
#         return cls(value = seconds)

#     @classmethod
#     def parse(cls, fromString: str) -> Object:
#         raise NotImplementedError

#     @classproperty
#     def pattern() -> Pattern:
#         raise NotImplementedError

#     def __lt__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value < value

#     def __le__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value <= value

#     def __gt__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value > value

#     def __ge__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value >= value

#     def __eq__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value == value

#     def __ne__(self, other: Object) -> bool:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return self.value != value

#     def __add__(self, other: Union[Object, Number]) -> TimeInterval:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return TimeInterval(self.value + value)

#     def __sub__(self, other: Union[Object, Number]) -> TimeInterval:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return TimeInterval(self.value - value)

#     def __mul__(self, other: Union[Object, Number]) -> TimeInterval:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return TimeInterval(self.value * value)

#     def __mod__(self, other: Union[Object, Number]) -> TimeInterval:
#         value = other.value if isinstance(other, TimeInterval) else other
#         return TimeInterval(self.value % value)

#     def __floordiv__(self, other: Union[Object, Number]) -> Union[Object, Number]:
#         return self.value // other.value if isinstance(other, TimeInterval) else TimeInterval(self.value // other)

#     def __truediv__(self, other: Union[Object, Number]) -> Union[Object, Number]:
#         return self.value / other.value if isinstance(other, TimeInterval) else TimeInterval(self.value / other)
