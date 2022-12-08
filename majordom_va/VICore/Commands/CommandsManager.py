from typing import Type, Optional
from .Command import Command
from ..VIObjects import *
from .RThread import RThread, Event

import config
from ..Pattern import Pattern

class SearchResult:
    command: Command
    parameters: dict[str, VIObject]

    def __init__(self, command: Command, parameters: dict[str, VIObject] = {}):
        self.command = command
        self.parameters = parameters

class CommandsManager:
    allCommands: list[Command] = []
    QA: Command = None

    def __new__(cls):                                                           # Singleton
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def search(self, string: str, commands: list[Command]) -> list[SearchResult]:
        results: list[SearchResult] = []
        acstring = VIString(string.lower())

        #   find command obj by pattern
        for command in commands:
            for pattern in command.patterns:
                groupdict = pattern.match(acstring)

                if groupdict != None:

                    parameters: dict[str: VIObject] = {'string': acstring}

                    for key, value in groupdict.items():
                        name, typeName = key.split(':')
                        VIType: Type[VIObject] = CommandsManager.classFromString(typeName)

                        try: parameters[name] = VIType.parse(string = value)
                        except: break
                    else:
                        results.append(SearchResult(command, parameters))

        if not results and (qa := self.QA):
            results.append(SearchResult(qa, {'string': acstring,}))

        return results

    def append(self, command):
        if hasattr(self, command.name):
            Exception('Error: command with name \'{command.name}\' already exist')
        setattr(self, command.name, command)
        if command.primary:
            self.allCommands.append(command)

    def getCommand(self, name) -> Optional[Command]:
        return getattr(self, name) if hasattr(self, name) else None

    def stringHasName(self, string) -> bool:
        match = Pattern(
            f'({"|".join(config.names)})'
        ).match(
            VIString(string.lower())
        )
        return match != None

    @staticmethod
    def classFromString(className: str) -> VIObject:
        return getattr(sys.modules[__name__], className)

    @staticmethod
    def background(answer = '', voice = ''):                                    # make background cmd
        def decorator(func):
            def wrapper(text):
                finishEvent = Event()
                thread = RThread(target=func, args=(text, finish_event))
                thread.start()
                return Response(voice = voice, text = answer, thread = ThreadData(thread, finishEvent) )
            return wrapper
        return decorator
