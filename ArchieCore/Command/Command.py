from typing import Callable
from abc import ABC
from .RThread import RThread, Event
from .CommandsManager import CommandsManager
from .. import Pattern

class Command(ABC):
    name: str
    patterns: list[Pattern]
    start: Callable

    def __init__(self, name, keywords = {}, patterns = []):                     #   initialisation of new command
        self._name = name #TODO: change name to path
        self._patterns = patterns
        CommandsManager().append(self)

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
            cmd: Command = cls(*args, **kwargs)
            cmd.setStart(func)
            return func
        return creator
