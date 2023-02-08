from __future__ import annotations
from typing import Callable, Any, Optional
from enum import Enum, auto

from pydantic import BaseModel

from ..patterns import Pattern
from ..VIObjects import VIObject
from .Threads import ThreadData


CommandRunner = Callable[[dict[str, VIObject]], 'Response']

class Command():
    name: str
    patterns: list[Pattern]

    def __init__(self, name: str, patterns: list[str], runner: CommandRunner):
        self.name = name
        self.patterns = [Pattern(pattern) for pattern in patterns]
        self.run = runner

    def run(self, params: dict[str, VIObject]) -> Response:
        raise NotImplementedError(f'Method start is not implemented for command with name {self.name}')

class ResponseAction(Enum):
    pop_context = auto()
    pop_to_root_context = auto()
    sleep = auto()
    repeat_last_answer = auto()

class Response(BaseModel):
    voice: str = ''
    text: str = ''
    commands: list[Command] = []
    parameters: dict[str, Any] = {}
    actions: list[ResponseAction] = []
    thread: Optional[ThreadData] = None
    # data: dict[str, Any]
    
    class Config:
        arbitrary_types_allowed = True