from typing import Callable
from abc import ABC

from ..patterns import Pattern
from ..VIObjects import VIObject
from .Response import Response


CommandRunner = Callable[[dict[str, VIObject]], Response]

class Command(ABC):
    name: str
    patterns: list[Pattern]

    def __init__(self, name: str, patterns: list[str], runner: CommandRunner):
        self.name = name
        self.patterns = [Pattern(pattern) for pattern in patterns]
        self.run = runner

    def run(self, params: dict[str, VIObject]) -> Response:
        raise NotImplementedError(f'Method start is not implemented for command with name {self.name}')
