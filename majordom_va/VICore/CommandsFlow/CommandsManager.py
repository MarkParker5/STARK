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
    commands: list[Command]
    QA: Command = None
    
    def __init__(self):
        self.commands = []

    def search(self, string: str, commands: list[Command] = None) -> list[SearchResult]:
        
        if not commands:
            commands = self.commands
        
        results: list[SearchResult] = []
        origin = VIString(string)

        for command in commands:
            for pattern in command.patterns:
                match = pattern.match(string)
                
                if not match:
                    continue
                
                parameters: dict[str: VIObject] = {}
                
                for name, value in match.groups.items():
                    
                    VIType: Type[VIObject] = pattern.arguments[name]
                    
                    if vi_object := VIType.parse(from_string = value):
                        parameters[name] = vi_object
                    else:
                        break
                else:
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
    
    def new(self, patterns: list[str], hidden: bool = False):
        def creator(func: CommandRunner) -> Command:
            cmd = Command(func.__name__, patterns, func)
            if not hidden:
                self.commands.append(cmd)
            return cmd
        return creator

    @staticmethod
    def background(first_response: Response):
        def decorator(origin_runner: CommandRunner):
            def sync_command_runner(params):
                finish_event = Event()
                
                def background_command_runner():
                    response = origin_runner(params) # can be long, blocking
                    finish_event.set()
                    return response
                
                thread = RThread(target=background_command_runner)
                thread.start()
                first_response.thread = ThreadData(thread, finish_event)
                return first_response
            return sync_command_runner
        return decorator
