from abc import ABC, abstractmethod
from typing import Any
from .. import Pattern

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class ACObject(ABC):
    pattern: Pattern # static getonly
    value: Any

    @classproperty
    @abstractmethod
    def pattern() -> Pattern:
        return Pattern('')
