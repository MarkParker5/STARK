from __future__ import annotations
from typing import Type
from pydantic import BaseModel

from ..patterns import Pattern
from ..VIObjects import *
from .Threads import ThreadData, RThread, Event
from .Command import Command, CommandRunner, Response


class SearchResult(BaseModel):
    command: Command
    substring: str
    parameters: dict[str, VIObject] = []
    
    class Config:
        arbitrary_types_allowed = True

class CommandsManager:
    
    name: str
    commands: list[Command]
    QA: Command = None
    
    def __init__(self, name: str = ''):
        self.name = name or 'CommandsManager'
        self.commands = []

    def search(self, string: str, commands: list[Command] = None) -> list[SearchResult]:
        
        if not commands:
            commands = self.commands
        
        results: list[SearchResult] = []
        origin = VIString(string)

        for command in commands:
            match = command.pattern.match(string)
                
            if not match:
                continue
            
            parameters: dict[str: VIObject] = {}
            
            for name, value in match.groups.items():
                
                VIType: Type[VIObject] = command.pattern.parameters[name]
                
                if vi_object := VIType.parse(from_string = value):
                    parameters[name] = vi_object
                else:
                    break
            else:
                for parameter in parameters.values():
                    # move nested parameters to viobjects
                    self._map_viobject(parameter, parameters)
                results.append(SearchResult(
                    command = command,
                    substring = match.substring,
                    parameters = parameters
                ))

        if not results and (qa := self.QA):
            results.append(SearchResult(
                command = qa,
                origin = origin
            ))

        return results
    
    def _map_viobject(self, vi_object: VIObject, parameters: dict[str, VIObject]) -> VIObject:
        for name in vi_object.__annotations__.keys():
            if name == 'value': 
                continue
            elif name in parameters:
                value = parameters.pop(name)
                setattr(vi_object, name, value)
                if isinstance(value, VIObject):
                    self._map_viobject(value, parameters)
            else:
                pass # TODO: raise error
    
    def new(self, pattern_str: str, hidden: bool = False):
        def creator(func: CommandRunner) -> Command:
            pattern = Pattern(pattern_str)
            error_msg = f'Command {self.name}.{func.__name__} must have all parameters from pattern: {pattern.parameters=} {func.__annotations__=}'
            assert pattern.parameters.items() <= func.__annotations__.items(), error_msg
            cmd = Command(f'{self.name}.{func.__name__}', pattern, func)
            if not hidden:
                self.commands.append(cmd)
            return cmd
        return creator
    
    def run(self, command: Command, parameters: dict[str, VIObject]) -> Response:
        # TODO: check command.__annotations__
        return command.run(**parameters)
    
    def extend(self, other_manager: CommandsManager):
        self.commands.extend(other_manager.commands)

    @staticmethod
    def background(first_response: Response):
        def decorator(origin_runner: CommandRunner):
            def sync_command_runner(*args, **kwargs):
                finish_event = Event()
                
                def background_command_runner():
                    response = origin_runner(*args, **kwargs) # can be long, blocking
                    finish_event.set()
                    return response
                
                thread = RThread(target=background_command_runner)
                thread.start()
                first_response.thread = ThreadData(thread, finish_event)
                return first_response
            return sync_command_runner
        return decorator
