from __future__ import annotations
from typing import Callable, Awaitable, Any, Optional, Protocol
from enum import auto, Enum
from datetime import datetime
import inspect

from pydantic import BaseModel, Field

from general.classproperty import classproperty
from .patterns import Pattern


AwaitResponse = Awaitable['Response | None']
AsyncCommandRunner = Callable[..., AwaitResponse]
CommandRunner = Callable[..., 'Response | None'] | AsyncCommandRunner

class Command:
    name: str
    pattern: Pattern
    _runner: AsyncCommandRunner

    def __init__(self, name: str, pattern: Pattern, runner: AsyncCommandRunner):
        assert isinstance(pattern, Pattern)
        assert inspect.iscoroutinefunction(runner)
        self.name = name
        self.pattern = pattern
        self._runner = runner

    def run(self, parameters_dict: dict[str, Any] | None = None, / , **kwparameters: dict[str, Any]) -> AwaitResponse:
        # allow call both with and without dict unpacking 
        # e.g. command.run(foo = bar, lorem = ipsum), command.run(**parameters) and command.run(parameters)
        # where parameters is dict {'foo': bar, 'lorem': ipsum}
        
        parameters = parameters_dict or {}
        parameters.update(kwparameters) 
            
        if any(p.kind == p.VAR_KEYWORD for p in inspect.signature(self._runner).parameters.values()):
            # all extra params will be passed as **kwargs
            return self._runner(**parameters)
        else:
            # avoid TypeError: self._runner got an unexpected keyword argument
            return self._runner(**{k: v for k, v in parameters.items() if k in self._runner.__annotations__})
    
    def __call__(self, *args, **kwargs) -> AwaitResponse:
        # just syntactic sugar for command() instead of command.run()
        return self.run(*args, **kwargs)

class ResponseStatus(Enum):
    none = auto()
    not_found = auto()
    failed = auto()
    success = auto()
    info = auto()
    error = auto()

class Response(BaseModel):
    voice: str = ''
    text: str = ''
    status: ResponseStatus = ResponseStatus.success
    needs_user_input: bool = False
    commands: list[Command] = []
    parameters: dict[str, Any] = {}
    time: datetime = Field(default_factory=datetime.now)
    
    _repeat_last: Response | None = None # static instance
    
    @classproperty
    def repeat_last(cls) -> Response:
        if not Response._repeat_last:
            Response._repeat_last = Response()
            return Response._repeat_last
        return Response._repeat_last    
    
    class Config:
        arbitrary_types_allowed = True
        
class ResponseHandler(Protocol):
    def respond(self, response: Response): pass
    def unrespond(self, response: Response): pass
    def pop_context(self): pass

class AsyncResponseHandler(Protocol):
    async def respond(self, response: Response): pass
    async def unrespond(self, response: Response): pass
    async def pop_context(self): pass
