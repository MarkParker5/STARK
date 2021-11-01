from typing import Callable
from abc import ABC

from ..Pattern import ACObject, Pattern
from .CommandsManager import CommandsManager

class Command(ABC):
    name: str
    patterns: list[Pattern]
    start: Callable

    def __init__(self, name, patterns = [], primary = True):
        self._name = name
        self._patterns = patterns
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
        def creator(func):
            cmd: Command = cls(func.__name__, *args, **kwargs)
            cmd.setStart(func)
            return cmd
        return creator
