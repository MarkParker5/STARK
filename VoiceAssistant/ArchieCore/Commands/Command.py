from typing import Callable
from abc import ABC

from ..ACObjects import ACObject
from ..Pattern import Pattern

class Command(ABC):
    name: str
    patterns: list[Pattern]
    start: Callable

    def __init__(self, name: str, patterns: list[str] = [], primary: bool = True):
        self._name = name
        self._patterns = [Pattern(pattern) for pattern in patterns]
        self.primary = primary

        from .CommandsManager import CommandsManager
        CommandsManager().append(self)

    def start(self, params: dict[str, ACObject]):
        raise Exception(f'Method start is not implemented for command with name {name}')

    def setStart(self, function):                                               #   define start (required)
        self.start = function

    @property
    def name(self):
        return self._name

    @property
    def patterns(self):
        return self._patterns

    @classmethod
    def new(cls, *args, **kwargs):
        def creator(func) -> Command:
            cmd: Command = cls(func.__name__, *args, **kwargs)
            cmd.setStart(func)
            return cmd
        return creator
