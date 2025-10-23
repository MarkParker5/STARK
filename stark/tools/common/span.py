from typing import Self


class Span:
    start: int
    end: int

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    @property
    def length(self) -> int:
        return self.end - self.start

    @property
    def slice(self) -> slice:
        return slice(self.start, self.end)

    def __bool__(self) -> bool:
        return self.end > self.start

    def __repr__(self) -> str:
        return f"Span({self.start}, {self.end})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Span):
            return self.start == other.start and self.end == other.end
        if isinstance(other, tuple) and len(other) == 2:
            return self.start == other[0] and self.end == other[1]
        return NotImplemented
