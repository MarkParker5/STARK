from __future__ import annotations
from typing import Callable, Any, Optional, Protocol
import inspect

from pydantic import BaseModel

from general.classproperty import classproperty
from ..patterns import Pattern
from .Threads import ThreadData


CommandRunner = Callable[..., 'Response']

class Command():
    name: str
    pattern: Pattern
    _runner: CommandRunner

    def __init__(self, name: str, pattern: Pattern, runner: CommandRunner):
        self.name = name
        self.pattern = pattern
        self._runner = runner

    def run(self, parameters_dict: dict[str, Any] | None = None, / , **kwparameters: dict[str, Any]) -> Response:
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
    
    def __call__(self, *args, **kwargs) -> Response:
        # just syntactic sugar for command() instead of command.run()
        return self.run(*args, **kwargs)

class Response(BaseModel):
    voice: str = ''
    text: str = ''
    needs_user_input: bool = False
    commands: list[Command] = []
    parameters: dict[str, Any] = {}
    thread: Optional[ThreadData] = None
    
    _repeat_last: Response | None = None
    
    @classproperty
    def repeat_last(cls) -> Response:
        if not Response._repeat_last:
            Response._repeat_last = Response()
            return Response._repeat_last
        return Response._repeat_last    
    
    class Config:
        arbitrary_types_allowed = True
        
class ResponseHandler(Protocol):
    def process_response(self, response: Response): pass
    def remove_response(self, response: Response): pass
    def pop_context(self): pass