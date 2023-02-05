from typing import Type
from pydantic import BaseModel

from ..patterns import Pattern
from ..VIObjects import *
from .RThread import RThread, Event
from .ThreadData import ThreadData
from .Command import Command, CommandRunner
from .Response import Response


class SearchResult(BaseModel):
    command: Command
    origin: VIString
    parameters: dict[str, VIObject]

class CommandsManager:
    commands: list[Command] = []
    QA: Command = None

    def search(self, string: str, commands: list[Command]) -> list[SearchResult]:
        results: list[SearchResult] = []
        origin = VIString(string)

        for command in commands:
            for pattern in command.patterns:
                match = pattern.match(string)
                
                if not match:
                    continue

                for key, value in match.groups.items():
                    parameters: dict[str: VIObject] = {}
                    
                    name, type_name = key.split(':')
                    VIType: Type[VIObject] = Pattern.argumentTypes[type_name]
                    
                    if vi_object := VIType.parse(string = value):
                        parameters[name] = vi_object
                    else:
                        break
                else:
                    results.append(SearchResult(command, origin, parameters))

        if not results and (qa := self.QA):
            results.append(SearchResult(qa, origin))

        return results
    
    def new(self, patterns: list[str]):
        def creator(func: CommandRunner) -> Command:
            cmd = Command(func.__name__, patterns, func)
            self.commands.append(cmd)
            return cmd
        return creator

    @staticmethod
    def background(answer = '', voice = ''):
        def decorator(func):
            def wrapper(text):
                finish_event = Event()
                thread = RThread(target=func, args=(text, finish_event))
                thread.start()
                return Response(voice = voice, text = answer, thread = ThreadData(thread, finish_event) )
            return wrapper
        return decorator
